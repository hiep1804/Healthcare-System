import os
import json
import logging
import requests
from django.conf import settings
from .models import DrugInteraction, DrugAllergenCrossRef, Drug

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


DEFAULT_SYSTEM_PROMPT = """Bạn là Trợ lý AI Hỗ trợ Quyết định Lâm sàng (AI CDS - Clinical Decision Support Assistant) chuyên nghiệp dành cho Bác sĩ tại Việt Nam.

NHIỆM VỤ CỦA BẠN:
1. Phân tích triệu chứng, chỉ số sinh tồn và hồ sơ bệnh nhân để đưa ra gợi ý chẩn đoán phân biệt (Differential Diagnosis).
2. Kiểm tra cảnh báo tương tác thuốc (Drug Interactions), tác dụng phụ và dị ứng/chống chỉ định.
3. Diễn giải kết quả xét nghiệm và gợi ý hướng điều trị (Treatment Guidelines).

QUY TẮC BẮT BUỘC:
- Trả lời bằng tiếng Việt chuyên môn y khoa nhưng dễ hiểu, súc tích.
- Luôn tôn trọng quyết định cuối cùng của Bác sĩ. Bạn là công cụ hỗ trợ, KHÔNG đưa ra chẩn đoán cuối cùng.
- Nếu phát hiện tương tác thuốc nguy hiểm hoặc chống chỉ định dị ứng, phải CẢNH BÁO NỔI BẬT.

ĐỊNH DẠNG TRẢ LỜI:
Hãy trả lời bác sĩ một cách tự nhiên. Ngoài ra, nếu có khuyến nghị quan trọng (cảnh báo tương tác thuốc, dị ứng, chẩn đoán phân biệt), hãy chèn một khối JSON ở CUỐI bài trả lời theo định dạng sau:

```json
{
  "recommendations": [
    {
      "category": "DRUG_INTERACTION | ALLERGY_ALERT | DIFFERENTIAL_DIAGNOSIS | LAB_INTERPRETATION | TREATMENT_SUGGESTION | DOSAGE_WARNING",
      "severity": "INFO | LOW | MEDIUM | HIGH | CRITICAL",
      "summary": "Tóm tắt khuyến nghị trong 1 câu ngắn",
      "explanation": "Giải thích chi tiết ngắn gọn",
      "confidence": 0.85
    }
  ]
}
```
"""


class AICDSService:
    """Service xử lý tương tác AI CDS bằng Google Gemini API"""

    @staticmethod
    def fetch_patient_context(patient_id, auth_header=None):
        """Fetch patient context from patient-service & medical-record-service"""
        context = {
            'patient_id': str(patient_id),
            'allergies': [],
            'conditions': [],
            'medications': [],
            'recent_vitals': None
        }

        headers = {'Host': 'localhost'}
        if auth_header:
            headers['Authorization'] = auth_header

        import os
        is_docker = os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_DOCKER', 'False').lower() in ('true', '1')
        gateway_host = 'api_gateway' if is_docker else '127.0.0.1'
        base_url = f'http://{gateway_host}:8000/api/v1'

        # Fetch Allergies
        try:
            r = requests.get(f"{base_url}/patients/{patient_id}/allergies", headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                context['allergies'] = data.get('data', data) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Failed to fetch allergies for patient {patient_id}: {e}")

        # Fetch Conditions
        try:
            r = requests.get(f"{base_url}/patients/{patient_id}/conditions", headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                context['conditions'] = data.get('data', data) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Failed to fetch conditions for patient {patient_id}: {e}")

        # Fetch Medications
        try:
            r = requests.get(f"{base_url}/patients/{patient_id}/medications", headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                context['medications'] = data.get('data', data) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Failed to fetch medications for patient {patient_id}: {e}")

        # Fetch Vitals
        try:
            r = requests.get(f"{base_url}/patients/{patient_id}/vitals", headers=headers, timeout=3)
            if r.status_code == 200:
                data = r.json()
                v_list = data.get('data', data) if isinstance(data, dict) else data
                if isinstance(v_list, list) and len(v_list) > 0:
                    context['recent_vitals'] = v_list[0]
        except Exception as e:
            logger.warning(f"Failed to fetch vitals for patient {patient_id}: {e}")

        return context

    @classmethod
    def build_prompt_context_string(cls, patient_context, user_message_text=""):
        """Build text summary of patient context + Neo4j Graph Knowledge for Gemini prompt"""
        from .graph_db import Neo4jGraphDB
        lines = []

        if patient_context:
            allergies = patient_context.get('allergies', [])
            conditions = patient_context.get('conditions', [])
            medications = patient_context.get('medications', [])
            vitals = patient_context.get('recent_vitals', {})

            if allergies or conditions or medications or vitals:
                lines.append("=== HỒ SƠ BỆNH NHÂN THỜI GIAN THỰC ===")
                if allergies:
                    lines.append("⚠️ DỊ ỨNG:")
                    for a in allergies:
                        lines.append(f"  - {a.get('allergen')}: {a.get('reaction', 'Không rõ')}")

                if conditions:
                    lines.append("🩺 BỆNH NỀN:")
                    for c in conditions:
                        lines.append(f"  - {c.get('condition_name')}")

                if medications:
                    lines.append("💊 THUỐC ĐANG DÙNG:")
                    for m in medications:
                        lines.append(f"  - {m.get('drug_name')}")

                if vitals:
                    sys = vitals.get('blood_pressure_systolic')
                    dia = vitals.get('blood_pressure_diastolic')
                    hr = vitals.get('heart_rate')
                    temp = vitals.get('temperature_c') or vitals.get('temperature_celsius')
                    v_str = []
                    if sys and dia: v_str.append(f"Huyết áp: {sys}/{dia} mmHg")
                    if hr: v_str.append(f"Nhịp tim: {hr} BPM")
                    if temp: v_str.append(f"Nhiệt độ: {temp} °C")
                    if v_str:
                        lines.append(f"📊 CHỈ SỐ SINH TỒN: {', '.join(v_str)}")
                lines.append("=====================================\n")

        # Query Neo4j Graph Database Grounding Knowledge for user message
        if user_message_text:
            user_lower = user_message_text.lower()
            known_drugs = Drug.objects.all()
            found_drugs = [d for d in known_drugs if d.name.lower() in user_lower]
            if len(found_drugs) >= 2:
                d1, d2 = found_drugs[0], found_drugs[1]
                neo_interactions = Neo4jGraphDB.check_drug_interaction(d1.name, d2.name)
                if neo_interactions and len(neo_interactions) > 0:
                    inter = neo_interactions[0]
                    lines.append("=== TRI THỨC ĐỒ THỊ Y KHOA NEO4J (GRAPHRAG GROUNDING) ===")
                    lines.append(f"⚠️ CẢNH BÁO TƯƠNG TÁC THUỐC (Mức độ: {inter['severity']}):")
                    lines.append(f"  - Thuốc 1: {inter['drug_a']} | Thuốc 2: {inter['drug_b']}")
                    lines.append(f"  - Cơ chế dược lý: {inter['mechanism']}")
                    lines.append(f"  - Hậu quả lâm sàng: {inter['clinical_effect']}")
                    lines.append(f"  - Khuyên dùng: {inter['recommendation']}")
                    lines.append("=========================================================\n")

        return "\n".join(lines)

    @classmethod
    def generate_ai_response(cls, conversation, user_message_text, history_messages=None):
        """Gửi câu hỏi tới Gemini API (đã nạp dữ liệu Neo4j GraphRAG) hoặc Fallback Mode"""
        api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')

        patient_context = conversation.patient_context_snapshot or {}
        context_str = cls.build_prompt_context_string(patient_context, user_message_text)
        
        if context_str:
            full_user_input = f"{context_str}\nBác sĩ hỏi: {user_message_text}"
        else:
            full_user_input = user_message_text

        if api_key and genai is not None:
            try:
                genai.configure(api_key=api_key)

                try:
                    model = genai.GenerativeModel(
                        model_name='gemini-1.5-flash',
                        system_instruction=DEFAULT_SYSTEM_PROMPT
                    )
                except Exception:
                    model = genai.GenerativeModel(
                        model_name='gemini-pro',
                        system_instruction=DEFAULT_SYSTEM_PROMPT
                    )

                contents = []
                if history_messages:
                    for msg in history_messages:
                        if msg.role == 'doctor':
                            contents.append({'role': 'user', 'parts': [msg.content]})
                        elif msg.role == 'assistant':
                            contents.append({'role': 'model', 'parts': [msg.content]})

                contents.append({'role': 'user', 'parts': [full_user_input]})

                response = model.generate_content(contents)
                raw_text = response.text
                return cls._parse_ai_output(raw_text)

            except Exception as e:
                logger.error(f"Gemini API error: {e}. Falling back to Rule-based response.")
                return cls._generate_fallback_response(user_message_text, patient_context)
        else:
            logger.info("GEMINI_API_KEY not set. Using Standard Chatbot Engine.")
            return cls._generate_fallback_response(user_message_text, patient_context)

    @classmethod
    def _parse_ai_output(cls, raw_text):
        """Tách nội dung văn bản và phần JSON recommendations trong câu trả lời của AI"""
        text_content = raw_text
        recommendations_data = []

        if "```json" in raw_text:
            try:
                parts = raw_text.split("```json")
                text_content = parts[0].strip()
                json_part = parts[1].split("```")[0].strip()
                parsed = json.loads(json_part)
                recommendations_data = parsed.get('recommendations', [])
            except Exception as e:
                logger.warning(f"Could not parse AI JSON recommendations: {e}")

        return {
            'text': text_content,
            'recommendations': recommendations_data
        }

    @classmethod
    def _generate_fallback_response(cls, user_message, patient_context):
        """Standard Assistant Engine khi chat tư vấn tự do hoặc không có chỉ số"""
        user_lower = user_message.lower()
        recs = []
        response_lines = []

        allergies = patient_context.get('allergies', []) or []
        conditions = patient_context.get('conditions', []) or []
        medications = patient_context.get('medications', []) or []
        vitals = patient_context.get('recent_vitals', {}) or {}

        # 1. Neo4j Knowledge Graph Interaction Check
        from .graph_db import Neo4jGraphDB
        known_drugs = Drug.objects.all()
        found_drugs = [d for d in known_drugs if d.name.lower() in user_lower]

        if len(found_drugs) >= 2:
            d1, d2 = found_drugs[0], found_drugs[1]
            # Priority 1: Query Neo4j Dedicated Graph Database
            neo_interactions = Neo4jGraphDB.check_drug_interaction(d1.name, d2.name)
            if neo_interactions and len(neo_interactions) > 0:
                inter = neo_interactions[0]
                response_lines.append(f"🌐 **TRUY VẤN ĐỒ THỊ TRI THỨC NEO4J (MEDICAL GRAPH DB):**")
                response_lines.append(f"⚠️ **CẢNH BÁO TƯƠNG TÁC THUỐC:** giữa **{inter['drug_a']}** và **{inter['drug_b']}** (Mức độ: **{inter['severity']}**)")
                response_lines.append(f"- **Cơ chế Dược lý:** {inter['mechanism']}")
                response_lines.append(f"- **Hậu quả Lâm sàng:** {inter['clinical_effect']}")
                response_lines.append(f"- **Khuyên dùng:** {inter['recommendation']}\n")

                recs.append({
                    'category': 'DRUG_INTERACTION',
                    'severity': inter['severity'],
                    'summary': f"Tương tác Neo4j Graph: {inter['drug_a']} + {inter['drug_b']}",
                    'explanation': inter['clinical_effect'],
                    'confidence': 0.99
                })
            else:
                # Fallback to RDBMS DrugInteraction table
                interaction = DrugInteraction.objects.filter(
                    drug_a=d1, drug_b=d2
                ).first() or DrugInteraction.objects.filter(
                    drug_a=d2, drug_b=d1
                ).first()

                if interaction:
                    response_lines.append(f"⚠️ **CẢNH BÁO TƯƠNG TÁC THUỐC:**")
                    response_lines.append(f"- Phát hiện tương tác giữa **{d1.name}** và **{d2.name}** ({interaction.get_severity_display()}).")
                    response_lines.append(f"- **Hậu quả:** {interaction.clinical_effect}")
                    response_lines.append(f"- **Khuyên dùng:** {interaction.recommendation}\n")

                    recs.append({
                        'category': 'DRUG_INTERACTION',
                        'severity': interaction.severity,
                        'summary': f"Tương tác thuốc: {d1.name} + {d2.name}",
                        'explanation': interaction.clinical_effect,
                        'confidence': 0.95
                    })

        # Allergy Check Rule
        for a in allergies:
            allergen = a.get('allergen', '').lower()
            if allergen and allergen in user_lower:
                response_lines.append(f"⛔ **CẢNH BÁO DỊ ỨNG:** Bệnh nhân có tiền sử dị ứng với **{a.get('allergen')}** (Phản ứng: {a.get('reaction', 'N/A')}). Cần tránh sử dụng thuốc này!\n")
                recs.append({
                    'category': 'ALLERGY_ALERT',
                    'severity': 'HIGH',
                    'summary': f"Cảnh báo dị ứng: {a.get('allergen')}",
                    'explanation': f"Bệnh nhân bị dị ứng {a.get('allergen')}.",
                    'confidence': 0.90
                })

        # Dynamic Intelligence Engine for fallback
        user_words = set(user_lower.split())
        if user_words.intersection({"chào", "hi", "hello", "xinchào", "xin-chào"}):
            response_lines.append("Xin chào Bác sĩ! Tôi là Trợ lý Y Khoa AI CDS. Tôi có thể giúp bác sĩ tra cứu liều dùng thuốc, tương tác thuốc hoặc phân tích triệu chứng lâm sàng. Bác sĩ cần tư vấn trường hợp nào ạ?")
        elif "sốt" in user_lower or "fever" in user_lower:
            response_lines.append("📋 **Gợi ý Chẩn đoán Phân biệt (Trường hợp Sốt):**")
            response_lines.append("1. Viêm đường hô hấp trên / Sốt siêu vi (Theo dõi ho, đau họng)")
            response_lines.append("2. Sốt xuất huyết Dengue (Kiểm tra dấu hiệu xuất huyết & công thức máu)")
            response_lines.append("3. Viêm phổi (Kiểm tra SpO2 và nghe phổi)")
            recs.append({
                'category': 'DIFFERENTIAL_DIAGNOSIS',
                'severity': 'MEDIUM',
                'summary': 'Gợi ý chẩn đoán phân biệt cho triệu chứng Sốt',
                'explanation': 'Cân nhắc Sốt siêu vi, Sốt xuất huyết Dengue hoặc Viêm đường hô hấp.',
                'confidence': 0.80
            })
        elif "ho" in user_lower or "khó thở" in user_lower or "phổi" in user_lower:
            response_lines.append("📋 **Gợi ý Chẩn đoán Phân biệt (Hô hấp):**")
            response_lines.append("1. Viêm phế quản cấp")
            response_lines.append("2. Viêm phổi cộng đồng")
            response_lines.append("3. Cơn hen phế quản cấp")
            recs.append({
                'category': 'DIFFERENTIAL_DIAGNOSIS',
                'severity': 'MEDIUM',
                'summary': 'Gợi ý chẩn đoán phân biệt Hô hấp',
                'explanation': 'Đánh giá Viêm phế quản cấp vs Viêm phổi.',
                'confidence': 0.82
            })
        # Drug Specific Queries (Side effects, usage, info)
        if "paracetamol" in user_lower or "acetaminophen" in user_lower or "panadol" in user_lower:
            if "tác dụng phụ" in user_lower or "phụ" in user_lower or "tác hại" in user_lower or "nguy hiểm" in user_lower:
                response_lines.append("💊 **Tác dụng phụ của Paracetamol (Acetaminophen):**")
                response_lines.append("1. **Độc tính trên gan (Hepatotoxicity):** Nguy cơ suy gan cấp nghiêm trọng nếu dùng quá liều (> 4g/ngày đối với người lớn).")
                response_lines.append("2. **Phản ứng dị ứng da:** Phát ban, mẩn ngứa, mày đay (hiếm gặp như hội chứng Stevens-Johnson).")
                response_lines.append("3. **Rối loạn tiêu hóa:** Buồn nôn, nôn mửa nhẹ.")
                response_lines.append("4. **Khuyến cáo:** Tránh uống rượu bia trong thời gian dùng thuốc. Liều an toàn: 500mg - 1000mg mỗi 4-6 giờ, tối đa 4000mg/ngày.")
            else:
                response_lines.append("💊 **Thông tin thuốc Paracetamol (Acetaminophen):**")
                response_lines.append("- **Chỉ định:** Hạ sốt, giảm đau vừa và nhẹ (đau đầu, đau răng, đau cơ).")
                response_lines.append("- **Liều dùng:** 500mg - 1000mg/lần, cách nhau 4-6 giờ. Tối đa 4g/ngày.")
                response_lines.append("- **Chống chỉ định:** Bệnh nhân suy gan nặng, thiếu hụt G6PD.")

        elif "aspirin" in user_lower:
            if "tác dụng phụ" in user_lower or "phụ" in user_lower:
                response_lines.append("💊 **Tác dụng phụ của Aspirin:**")
                response_lines.append("1. **Kích ứng & Xuất huyết tiêu hóa:** Viêm loét dạ dày, chảy máu đường tiêu hóa.")
                response_lines.append("2. **Kéo dài thời gian chảy máu:** Tăng nguy cơ bầm tím, chảy máu cam.")
                response_lines.append("3. **Hội chứng Reye:** Chống chỉ định cho trẻ em dưới 12 tuổi bị nhiễm virus (sốt siêu vi, thủy đậu).")
            else:
                response_lines.append("💊 **Thông tin thuốc Aspirin (Acid Acetylsalicylic):**")
                response_lines.append("- **Chỉ định:** Kháng tiểu cầu phòng ngừa huyết khối tim mạch, giảm đau, chống viêm.")
                response_lines.append("- **Thận trọng:** Nguy cơ tương tác nghiêm trọng với Warfarin và các thuốc chống đông máu.")

        elif "warfarin" in user_lower:
            response_lines.append("💊 **Thông tin & Tác dụng phụ của Warfarin:**")
            response_lines.append("- **Tác dụng phụ:** Nguy cơ xuất huyết cao (chảy máu nướu răng, đi ngoài phân đen, bầm tím lớn).")
            response_lines.append("- **Cảnh báo:** Cần theo dõi chỉ số INR định kỳ. Tương tác nghiêm trọng với Aspirin, NSAIDs và Vitamin K.")

        elif "amoxicillin" in user_lower:
            response_lines.append("💊 **Thông tin & Tác dụng phụ của Amoxicillin:**")
            response_lines.append("- **Tác dụng phụ:** Phát ban da, tiêu chảy, buồn nôn, nguy cơ sốc bảo vệ nếu dị ứng nhóm Beta-lactam.")
            response_lines.append("- **Chỉ định:** Kháng sinh điều trị nhiễm khuẩn đường hô hấp, tai mũi họng, tiết niệu.")

        elif "ibuprofen" in user_lower:
            response_lines.append("💊 **Thông tin & Tác dụng phụ của Ibuprofen (NSAID):**")
            response_lines.append("- **Tác dụng phụ:** Viêm loét dạ dày thực quản, giảm chức năng thận khi dùng kéo dài, tăng nguy cơ sự cố tim mạch.")
            response_lines.append("- **Khuyên dùng:** Nên uống sau khi ăn no để giảm kích ứng dạ dày.")

        elif "đau đầu" in user_lower or "chóng mặt" in user_lower:
            response_lines.append("📋 **Gợi ý Chẩn đoán Phân biệt (Thần kinh / Tuần hoàn):**")
            response_lines.append("1. Đau đầu căng thẳng (Tension headache)")
            response_lines.append("2. Tăng huyết áp / Rối loạn tiền đình")
            response_lines.append("3. Thiểu năng tuần hoàn脳 (Thiếu máu não)")

        elif "đau bụng" in user_lower or "tiêu hóa" in user_lower:
            response_lines.append("📋 **Gợi ý Chẩn đoán Phân biệt (Tiêu hóa):**")
            response_lines.append("1. Viêm dạ dày cấp / Trào ngược dạ dày thực quản (GERD)")
            response_lines.append("2. Hội chứng ruột kích thích (IBS)")
            response_lines.append("3. Viêm ruột thừa cấp (Cần loại trừ nếu đau hố chậu phải)")

        elif "thuốc" in user_lower or "đơn thuốc" in user_lower or "kê đơn" in user_lower:
            response_lines.append("💊 **Hỗ trợ Kê đơn & Dược lâm sàng:**")
            response_lines.append("- Nhập tên 2 loại thuốc (ví dụ: 'Aspirin và Warfarin') để AI tự động kiểm tra tương tác thuốc nguy hiểm.")
            response_lines.append("- AI sẽ tự động đối chiếu danh mục dị ứng của bệnh nhân khi bác sĩ nhập tên thuốc.")

        elif any(k in user_lower for k in ["sinh tồn", "chỉ số", "vitals", "huyết áp", "nhịp tim", "nhiệt độ", "thân nhiệt", "ổn không", "bệnh nhân", "sức khỏe"]):
            vitals = patient_context.get('recent_vitals')
            response_lines.append("📊 **ĐÁNH GIÁ CHỈ SỐ SINH TỒN & SỨC KHỎE BỆNH NHÂN:**\n")
            if vitals:
                sys = vitals.get('blood_pressure_systolic')
                dia = vitals.get('blood_pressure_diastolic')
                hr = vitals.get('heart_rate')
                temp = vitals.get('temperature_c') or vitals.get('temperature_celsius')

                if sys and dia:
                    try:
                        if float(sys) >= 140 or float(dia) >= 90:
                            response_lines.append(f"- ⚠️ **Huyết áp:** {sys}/{dia} mmHg (**TĂNG HUYẾT ÁP** - Cần theo dõi sát).")
                            recs.append({'category': 'DOSAGE_WARNING', 'severity': 'HIGH', 'summary': f'Huyết áp cao ({sys}/{dia} mmHg)', 'explanation': 'Bệnh nhân có chỉ số huyết áp vượt ngưỡng bình thường.', 'confidence': 0.90})
                        elif float(sys) < 90 or float(dia) < 60:
                            response_lines.append(f"- ⚠️ **Huyết áp:** {sys}/{dia} mmHg (**HUYẾT ÁP THẤP**).")
                        else:
                            response_lines.append(f"- ✅ **Huyết áp:** {sys}/{dia} mmHg (Trong ngưỡng bình thường).")
                    except (ValueError, TypeError):
                        response_lines.append(f"- 🩺 **Huyết áp:** {sys}/{dia} mmHg.")

                if temp:
                    try:
                        t_val = float(temp)
                        if t_val >= 38.5:
                            response_lines.append(f"- 🌡️ **Nhiệt độ:** {temp} °C (**SỐT CAO** - Gợi ý dùng hạ sốt nếu không có chống chỉ định).")
                            recs.append({'category': 'TREATMENT_SUGGESTION', 'severity': 'HIGH', 'summary': f'Sốt cao ({temp} °C)', 'explanation': 'Cần chẩn đoán nguyên nhân gây sốt và cho dùng thuốc hạ sốt.', 'confidence': 0.92})
                        elif t_val >= 37.5:
                            response_lines.append(f"- 🌡️ **Nhiệt độ:** {temp} °C (**SỐT NHẸ** / Thân nhiệt tăng nhẹ).")
                        elif t_val < 36.0:
                            response_lines.append(f"- 🥶 **Nhiệt độ:** {temp} °C (**HẠ THÂN NHIỆT** - Bệnh nhân bị hạ thân nhiệt, cần giữ ấm & đo lại).")
                            recs.append({'category': 'VITAL_WARNING', 'severity': 'HIGH', 'summary': f'Hạ thân nhiệt ({temp} °C)', 'explanation': 'Nhiệt độ cơ thể dưới 36.0°C chỉ ra tình trạng hạ thân nhiệt.', 'confidence': 0.90})
                        else:
                            response_lines.append(f"- ✅ **Nhiệt độ:** {temp} °C (Thân nhiệt bình thường).")
                    except (ValueError, TypeError):
                        response_lines.append(f"- 🌡️ **Nhiệt độ:** {temp} °C.")

                if hr:
                    try:
                        h_val = float(hr)
                        if h_val >= 100:
                            response_lines.append(f"- ❤️ **Nhịp tim:** {hr} BPM (**NHỊP TIM NHANH**).")
                        elif h_val < 60:
                            response_lines.append(f"- ❤️ **Nhịp tim:** {hr} BPM (**NHỊP TIM CHẬM**).")
                        else:
                            response_lines.append(f"- ✅ **Nhịp tim:** {hr} BPM (Nhịp tim bình thường).")
                    except (ValueError, TypeError):
                        response_lines.append(f"- ❤️ **Nhịp tim:** {hr} BPM.")
            else:
                response_lines.append("- ⚠️ **Chưa có chỉ số sinh tồn:** Ca khám này chưa lưu chỉ số sinh tồn mới nhất trong CSDL. Bác sĩ/y tá có thể điền thông số tại form '2. Ghi nhận Chỉ số Sinh tồn' bên trái và nhấn 'Lưu Chỉ số Sinh tồn'.")

            if allergies:
                response_lines.append("\n⚠️ **TIỀN SỬ DỊ ỨNG:**")
                for a in allergies:
                    response_lines.append(f"- {a.get('allergen')}: {a.get('reaction', 'Không rõ phản ứng')}")

            if conditions:
                response_lines.append("\n🩺 **BỆNH NỀN GHI NHẬN:**")
                for c in conditions:
                    response_lines.append(f"- {c.get('condition_name')}")

        else:
            response_lines.append(f"Về thắc mắc **'{user_message}'**:\n")
            response_lines.append("Trợ lý AI CDS đã ghi nhận câu hỏi. Để tư vấn chính xác nhất cho trường hợp này, bác sĩ có thể cung cấp thêm thông tin triệu chứng hoặc tên loại thuốc cần tra cứu cụ thể.")

        return {
            'text': "\n".join(response_lines),
            'recommendations': recs
        }
