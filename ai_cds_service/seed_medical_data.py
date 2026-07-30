import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cds.models import Disease, Symptom, Drug, DrugInteraction, DiseaseSymptom, DiseaseTreatment, PromptTemplate


def seed_data():
    print("[+] Starting Medical Knowledge Base Seeding...")

    # 1. Diseases
    diseases_data = [
        {"name": "Viêm phổi cộng đồng", "icd_code": "J18.9", "severity_level": "SEVERE", "description": "Nhiễm trùng nhu mô phổi do vi khuẩn hoặc virus."},
        {"name": "Đái tháo đường Tuýp 2", "icd_code": "E11", "severity_level": "MODERATE", "is_chronic": True, "description": "Rối loạn chuyển hóa đường huyết mạn tính."},
        {"name": "Tăng huyết áp vô căn", "icd_code": "I10", "severity_level": "MODERATE", "is_chronic": True, "description": "Huyết áp tâm thu >= 140 mmHg hoặc tâm trương >= 90 mmHg."},
        {"name": "Viêm họng cấp", "icd_code": "J02", "severity_level": "MILD", "description": "Viêm niêm mạc họng do vi khuẩn hoặc virus."},
        {"name": "Sốt xuất huyết Dengue", "icd_code": "A90", "severity_level": "SEVERE", "description": "Bệnh truyền nhiễm cấp tính do virus Dengue truyền qua muỗi."},
        {"name": "Viêm dạ dày - tá tràng", "icd_code": "K29", "severity_level": "MILD", "description": "Tổn thương niêm mạc dạ dày do Hp hoặc NSAID."},
    ]

    disease_objs = {}
    for d in diseases_data:
        obj, created = Disease.objects.get_or_create(name=d["name"], defaults=d)
        disease_objs[d["name"]] = obj
    print(f"[OK] Loaded {len(disease_objs)} Diseases")

    # 2. Symptoms
    symptoms_data = [
        {"name": "Sốt cao", "body_system": "Toàn thân", "is_red_flag": False},
        {"name": "Ho có đờm", "body_system": "Hô hấp", "is_red_flag": False},
        {"name": "Khó thở", "body_system": "Hô hấp", "is_red_flag": True},
        {"name": "Đau ngực", "body_system": "Tim mạch", "is_red_flag": True},
        {"name": "Đau họng", "body_system": "Hô hấp", "is_red_flag": False},
        {"name": "Khát nước nhiều", "body_system": "Nội tiết", "is_red_flag": False},
        {"name": "Đi tiểu nhiều lần", "body_system": "Nội tiết", "is_red_flag": False},
        {"name": "Đau đầu", "body_system": "Thần kinh", "is_red_flag": False},
        {"name": "Xuất huyết dưới da", "body_system": "Huyết học", "is_red_flag": True},
    ]

    symptom_objs = {}
    for s in symptoms_data:
        obj, created = Symptom.objects.get_or_create(name=s["name"], defaults=s)
        symptom_objs[s["name"]] = obj
    print(f"[OK] Loaded {len(symptom_objs)} Symptoms")

    # 3. Drugs
    drugs_data = [
        {"name": "Amoxicillin", "atc_code": "J01CA04", "drug_class": "Kháng sinh Penicillin", "common_dosage": "500mg x 3 lần/ngày"},
        {"name": "Warfarin", "atc_code": "B01AA03", "drug_class": "Thuốc chống đông máu", "common_dosage": "2.5mg - 5mg/ngày"},
        {"name": "Aspirin", "atc_code": "B01AC06", "drug_class": "Kháng tiểu cầu / NSAID", "common_dosage": "81mg - 100mg/ngày"},
        {"name": "Metformin", "atc_code": "A10BA02", "drug_class": "Thuốc hạ đường huyết Biguanide", "common_dosage": "500mg - 1000mg x 2 lần/ngày"},
        {"name": "Amlodipine", "atc_code": "C08CA01", "drug_class": "Thuốc chẹn kênh Canxi", "common_dosage": "5mg - 10mg/ngày"},
        {"name": "Paracetamol", "atc_code": "N02BE01", "drug_class": "Hạ sốt giảm đau", "common_dosage": "500mg x 3-4 lần/ngày"},
        {"name": "Azithromycin", "atc_code": "J01FA10", "drug_class": "Kháng sinh Macrolide", "common_dosage": "500mg x 1 lần/ngày"},
        {"name": "Ibuprofen", "atc_code": "M01AE01", "drug_class": "Kháng viêm NSAID", "common_dosage": "400mg x 3 lần/ngày"},
    ]

    drug_objs = {}
    for dr in drugs_data:
        obj, created = Drug.objects.get_or_create(name=dr["name"], defaults=dr)
        drug_objs[dr["name"]] = obj
    print(f"[OK] Loaded {len(drug_objs)} Drugs")

    # 4. Drug Interactions
    interactions_data = [
        {
            "drug_a": drug_objs["Warfarin"],
            "drug_b": drug_objs["Aspirin"],
            "severity": "CRITICAL",
            "mechanism": "Cùng ức chế đông máu và chức năng tiểu cầu.",
            "clinical_effect": "Tăng đáng kể nguy cơ xuất huyết nặng và xuất huyết dạ dày.",
            "recommendation": "Tránh phối hợp ngoại trừ trường hợp có chỉ định đặc biệt từ chuyên khoa Tim mạch."
        },
        {
            "drug_a": drug_objs["Warfarin"],
            "drug_b": drug_objs["Ibuprofen"],
            "severity": "MAJOR",
            "mechanism": "NSAID làm tăng nguy cơ tổn thương niêm mạc dạ dày và ức chế tiểu cầu.",
            "clinical_effect": "Tăng nguy cơ chảy máu tiêu hóa.",
            "recommendation": "Thay thế Ibuprofen bằng Paracetamol để giảm đau hạ sốt."
        },
        {
            "drug_a": drug_objs["Amoxicillin"],
            "drug_b": drug_objs["Azithromycin"],
            "severity": "MODERATE",
            "mechanism": "Kháng sinh diệt khuẩn (Amoxicillin) kết hợp kháng sinh kìm khuẩn (Azithromycin).",
            "clinical_effect": "Có thể làm giảm hiệu quả diệt khuẩn của Amoxicillin.",
            "recommendation": "Cân nhắc sử dụng đơn trị liệu hoặc phối hợp theo hướng dẫn vi sinh."
        }
    ]

    for inter in interactions_data:
        DrugInteraction.objects.get_or_create(
            drug_a=inter["drug_a"],
            drug_b=inter["drug_b"],
            defaults=inter
        )
    print(f"[OK] Loaded {len(interactions_data)} Drug Interactions")

    print("[SUCCESS] Medical Knowledge Base Seeding Complete!")


if __name__ == '__main__':
    seed_data()
