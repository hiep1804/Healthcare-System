import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedNeo4j100")

def seed_graph():
    from neo4j import GraphDatabase
    uri = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD', 'healthcare_neo4j_2026')

    logger.info(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # Clear existing graph data
        logger.info("Cleaning old graph nodes & relationships...")
        session.run("MATCH (n) DETACH DELETE n")

        # ============================================================
        # 1. CREATE 35 DRUG NODES
        # ============================================================
        logger.info("Creating 35 Drug nodes...")
        session.run("""
        UNWIND [
          {name: 'Aspirin', atc: 'B01AC06', class: 'Kháng tiểu cầu', dosage: '81mg - 325mg/ngày'},
          {name: 'Warfarin', atc: 'B01AA03', class: 'Kháng đông máu', dosage: '2mg - 5mg/ngày'},
          {name: 'Paracetamol', atc: 'N02BE01', class: 'Hạ sốt giảm đau', dosage: '500mg - 1000mg/lần'},
          {name: 'Amoxicillin', atc: 'J01CA04', class: 'Kháng sinh Beta-lactam', dosage: '500mg mỗi 8 giờ'},
          {name: 'Ibuprofen', atc: 'M01AE01', class: 'Kháng viêm NSAID', dosage: '400mg mỗi 6 giờ'},
          {name: 'Clopidogrel', atc: 'B01AC04', class: 'Kháng tiểu cầu', dosage: '75mg/ngày'},
          {name: 'Metformin', atc: 'A10BA02', class: 'Hạ đường huyết Biguanide', dosage: '500mg - 1000mg/lần x 2 lần/ngày'},
          {name: 'Atorvastatin', atc: 'C10AA05', class: 'Hạ lipid máu Statin', dosage: '10mg - 40mg/ngày'},
          {name: 'Amlodipine', atc: 'C08CA01', class: 'Hạ áp Chẹn kênh Canxi', dosage: '5mg - 10mg/ngày'},
          {name: 'Enalapril', atc: 'C09AA02', class: 'Hạ áp Ức chế men chuyển ACE', dosage: '5mg - 20mg/ngày'},
          {name: 'Losartan', atc: 'C09CA01', class: 'Hạ áp Chẹn thụ thể ARB', dosage: '50mg - 100mg/ngày'},
          {name: 'Omeprazole', atc: 'A02BC01', class: 'Ức chế bơm Proton PPI', dosage: '20mg - 40mg/ngày'},
          {name: 'Ranitidine', atc: 'A02BA02', class: 'Kháng H2 dạ dày', dosage: '150mg x 2 lần/ngày'},
          {name: 'Azithromycin', atc: 'J01FA10', class: 'Kháng sinh Macrolide', dosage: '500mg/ngày x 3 ngày'},
          {name: 'Ciprofloxacin', atc: 'J01MA02', class: 'Kháng sinh Quinolone', dosage: '500mg x 2 lần/ngày'},
          {name: 'Ceftriaxone', atc: 'J01DD04', class: 'Kháng sinh Cephalosporin TH3', dosage: '1g - 2g/ngày tiêm IV'},
          {name: 'Prednisolone', atc: 'H02AB06', class: 'Corticoid chống viêm', dosage: '5mg - 60mg/ngày'},
          {name: 'Dexamethasone', atc: 'H02AB02', class: 'Corticoid mạnh', dosage: '0.5mg - 10mg/ngày'},
          {name: 'Salbutamol', atc: 'R03AC02', class: 'Giãn phế quản Beta-2', dosage: '2-4mg/lần hoặc xịt hít'},
          {name: 'Montelukast', atc: 'R03DC03', class: 'Kháng Leukotriene', dosage: '10mg/ngày buổi tối'},
          {name: 'Loratadine', atc: 'R06AX13', class: 'Kháng Histamine H1 TH2', dosage: '10mg/ngày'},
          {name: 'Cetirizine', atc: 'R06AE07', class: 'Kháng Histamine H1 TH2', dosage: '10mg/ngày'},
          {name: 'Diazepam', atc: 'N05BA01', class: 'An thần Benzodiazepine', dosage: '2mg - 10mg/ngày'},
          {name: 'Sertraline', atc: 'N06AB06', class: 'Chống trầm cảm SSRI', dosage: '50mg - 100mg/ngày'},
          {name: 'Furosemide', atc: 'C03CA01', class: 'Lợi tiểu quai', dosage: '20mg - 80mg/ngày'},
          {name: 'Hydrochlorothiazide', atc: 'C03AA03', class: 'Lợi tiểu Thiazide', dosage: '12.5mg - 25mg/ngày'},
          {name: 'Spironolactone', atc: 'C03DA01', class: 'Lợi tiểu tiết kiệm Kali', dosage: '25mg - 100mg/ngày'},
          {name: 'Insulin Regular', atc: 'A10AB01', class: 'Insulin hạ đường huyết', dosage: 'Tùy chỉnh theo chỉ số đường huyết'},
          {name: 'Gliclazide', atc: 'A10BB09', class: 'Hạ đường huyết Sulfonylurea', dosage: '30mg - 120mg/ngày'},
          {name: 'Tramadol', atc: 'N02AJ13', class: 'Giảm đau Opioid nhẹ', dosage: '50mg - 100mg/lần'},
          {name: 'Morphine', atc: 'N02AA01', class: 'Giảm đau Opioid mạnh', dosage: '10mg - 30mg/lần'},
          {name: 'Allopurinol', atc: 'M04AA01', class: 'Hạ Acid Uric máu (Gút)', dosage: '100mg - 300mg/ngày'},
          {name: 'Colchicine', atc: 'M04AC01', class: 'Điều trị gút cấp', dosage: '1mg/lần, theo dõi độc tính'},
          {name: 'Levothyroxine', atc: 'H03AA01', class: 'Hormone tuyến giáp', dosage: '25mcg - 150mcg/ngày'},
          {name: 'Metoclopramide', atc: 'A03FA01', class: 'Chống nôn & kích thích nhu động', dosage: '10mg/lần trước ăn'}
        ] AS d
        CREATE (:Drug {name: d.name, atc_code: d.atc, drug_class: d.class, common_dosage: d.dosage})
        """)

        # ============================================================
        # 2. CREATE 25 DISEASE NODES
        # ============================================================
        logger.info("Creating 25 Disease nodes...")
        session.run("""
        UNWIND [
          {name: 'Sốt xuất huyết Dengue', icd: 'A90', desc: 'Nhiễm virus Dengue do muỗi Aedes truyền'},
          {name: 'Tăng huyết áp nguyên phát', icd: 'I10', desc: 'Tăng áp lực máu trong lòng động mạch mãn tính'},
          {name: 'Đái tháo đường Type 2', icd: 'E11', desc: 'Rối loạn chuyển hóa đường do đề kháng Insulin'},
          {name: 'Viêm phế quản cấp', icd: 'J20', desc: 'Nhiễm trùng niêm mạc phế quản'},
          {name: 'Viêm phổi cộng đồng', icd: 'J18', desc: 'Nhiễm trùng tổn thương nhu mô phổi'},
          {name: 'Viêm loét dạ dày thực quản', icd: 'K27', desc: 'Viêm loét tổn thương niêm mạc tiêu hóa'},
          {name: 'Trào ngược dạ dày thực quản GERD', icd: 'K21', desc: 'Dịch vị dạ dày trào ngược lên thực quản'},
          {name: 'Hen phế quản', icd: 'J45', desc: 'Viêm mãn tính đường hô hấp gây co thắt phế quản'},
          {name: 'Bệnh phổi tắc nghẽn mãn tính COPD', icd: 'J44', desc: 'Tắc nghẽn luồng khí thở không phục hồi hoàn toàn'},
          {name: 'Suy tim mãn tính', icd: 'I50', desc: 'Tim giảm khả năng bơm máu đáp ứng nhu cầu cơ thể'},
          {name: 'Xơ vữa động mạch', icd: 'I70', desc: 'Lắng đọng mảng xơ vữa trong lòng động mạch'},
          {name: 'Rung nhĩ', icd: 'I48', desc: 'Rối loạn nhịp tim nhanh không đều ở tâm nhĩ'},
          {name: 'Gút cấp và mãn', icd: 'M10', desc: 'Lắng đọng tinh thể Urat tại các khớp'},
          {name: 'Rối loạn lipid máu', icd: 'E78', desc: 'Tăng Cholesterol / Triglyceride máu'},
          {name: 'Viêm họng cấp', icd: 'J02', desc: 'Viêm nhiễm trùng cấp tính vùng họng'},
          {name: 'Viêm xoang cấp', icd: 'J01', desc: 'Viêm nhiễm trùng các xoang cạnh mũi'},
          {name: 'Nhiễm trùng đường tiết niệu', icd: 'N39', desc: 'Nhiễm khuẩn vi sinh vật tại đường niệu'},
          {name: 'Suy gan mãn tính', icd: 'K72', desc: 'Tổn thương tế bào gan di tiến hoại tử xơ hóa'},
          {name: 'Suy thận mãn tính', icd: 'N18', desc: 'Giảm mức lọc cầu thận tiến triển kéo dài'},
          {name: 'Rối loạn lo âu lan tỏa', icd: 'F41', desc: 'Trạng thái lo âu căng thẳng quá mức kéo dài'},
          {name: 'Trầm cảm nặng', icd: 'F32', desc: 'Rối loạn khí sắc giảm hứng thú và năng lượng'},
          {name: 'Rối loạn tiền đình', icd: 'H81', desc: 'Tổn thương cơ quan tiền đình gây mất thăng bằng'},
          {name: 'Nhồi máu cơ tim cấp', icd: 'I21', desc: 'Hoại tử cơ tim do thiếu máu cục bộ đột ngột'},
          {name: 'Viêm khớp dạng thấp', icd: 'M05', desc: 'Bệnh tự miễn gây viêm mạn tính nhiều khớp'},
          {name: 'Đau đầu Migraine', icd: 'G43', desc: 'Đau đầu nửa đầu nguyên phát dạng mạch máu'}
        ] AS dis
        CREATE (:Disease {name: dis.name, icd_code: dis.icd, description: dis.desc})
        """)

        # ============================================================
        # 3. CREATE 25 SYMPTOM NODES
        # ============================================================
        logger.info("Creating 25 Symptom nodes...")
        session.run("""
        UNWIND [
          {name: 'Sốt', desc: 'Thân nhiệt đo tại nách/miệng >= 37.5 độ C'},
          {name: 'Ho', desc: 'Ho khan hoặc ho khạc đờm mủ'},
          {name: 'Đau đầu', desc: 'Cảm giác đau nhức vùng vòm đầu hoặc nửa đầu'},
          {name: 'Đau bụng', desc: 'Đau tức vùng thượng vị hoặc quanh rốn'},
          {name: 'Khó thở', desc: 'Thở nhanh nông, cảm giác hụt hơi thiếu không khí'},
          {name: 'Xuất huyết dưới da', desc: 'Chấm xuất huyết bầm tím rải rác trên da'},
          {name: 'Tăng đường huyết', desc: 'Chỉ số đường huyết lúc đói >= 126 mg/dL'},
          {name: 'Đau ngực', desc: 'Cảm giác đè nén, thắt chặt vùng sau xương ức'},
          {name: 'Chóng mặt', desc: 'Cảm giác chao đảo, quay mòng mòng mất thăng bằng'},
          {name: 'Ợ chua', desc: 'Dịch chua từ dạ dày trào ngược lên họng'},
          {name: 'Buồn nôn', desc: 'Cảm giác nôn nao muốn nôn mửa'},
          {name: 'Tiêu chảy', desc: 'Đi ngoài phân lỏng >= 3 lần/ngày'},
          {name: 'Đau khớp', desc: 'Sưng nóng đỏ đau tại các khớp ngón tay/chân'},
          {name: 'Phù chân', desc: 'Phù mềm ấn lõm vùng mu bàn chân và cẳng chân'},
          {name: 'Khàn tiếng', desc: 'Giọng nói khàn đục hoặc mất tiếng'},
          {name: 'Mất ngủ', desc: 'Trằn trọc khó ngủ hoặc thức giấc sớm'},
          {name: 'Hồi hộp đánh trống ngực', desc: 'Cảm giác tim đập nhanh dồn dập bất thường'},
          {name: 'Thở khò khè', desc: 'Tiếng rít phế quản khi hít vào thở ra'},
          {name: 'Mệt mỏi kéo dài', desc: 'Cơ thể kiệt sức giảm khả năng lao động'},
          {name: 'Đái buốt', desc: 'Cảm giác đau rát nhói khi đi tiểu'},
          {name: 'Vàng da', desc: 'Da và kết mạc mắt nhuốm màu vàng ối'},
          {name: 'Đau vùng hạ sườn phải', desc: 'Đau tức vùng gan dưới bờ sườn phải'},
          {name: 'Co thắt cơ', desc: 'Chuột rút bắp chân co thắt cơ đau đột ngột'},
          {name: 'Phát ban da', desc: 'Mẩn đỏ ngứa mề đay trên bề mặt da'},
          {name: 'Giảm cân nhanh', desc: 'Sút cân đột ngột không rõ nguyên nhân (>5%/tháng)'}
        ] AS sym
        CREATE (:Symptom {name: sym.name, description: sym.desc})
        """)

        # ============================================================
        # 4. CREATE 15 ALLERGEN NODES
        # ============================================================
        logger.info("Creating 15 Allergen nodes...")
        session.run("""
        UNWIND [
          {name: 'Penicillin', desc: 'Dị ứng kháng sinh nhóm Penicillin & Beta-lactam'},
          {name: 'Cephalosporin', desc: 'Dị ứng kháng sinh Cephalosporin các thế hệ'},
          {name: 'NSAID', desc: 'Dị ứng thuốc chống viêm không steroid'},
          {name: 'Aspirin', desc: 'Dị ứng các chế phẩm gốc Salicylate'},
          {name: 'Sulfa', desc: 'Dị ứng nhóm thuốc Sulfonamide'},
          {name: 'Macrolide', desc: 'Dị ứng Erythromycin, Azithromycin'},
          {name: 'Quinolone', desc: 'Dị ứng Ciprofloxacin, Levofloxacin'},
          {name: 'Tetracycline', desc: 'Dị ứng Doxycycline, Tetracycline'},
          {name: 'Opioid', desc: 'Dị ứng Morphine, Tramadol'},
          {name: 'Barbiturate', desc: 'Dị ứng Phenobarbital'},
          {name: 'Lidocaine', desc: 'Dị ứng thuốc gây tê tại chỗ'},
          {name: 'Iodine Contrast', desc: 'Dị ứng thuốc phản quang chứa I-ốt'},
          {name: 'Aminoglycoside', desc: 'Dị ứng Gentamicin, Amikacin'},
          {name: 'Carbapenem', desc: 'Dị ứng Meropenem, Imipenem'},
          {name: 'Anticonvulsant', desc: 'Dị ứng thuốc chống co giật (Carbamazepine)'}
        ] AS all
        CREATE (:Allergen {name: all.name, description: all.desc})
        """)

        # ============================================================
        # 5. CREATE DRUG-DRUG INTERACTIONS (INTERACTS_WITH)
        # ============================================================
        logger.info("Creating INTERACTS_WITH relationships...")
        session.run("""
        UNWIND [
          {d1: 'Aspirin', d2: 'Warfarin', sev: 'CRITICAL', mech: 'Hiệp đồng tác dụng kháng đông & kháng tiểu cầu', eff: 'Xuất huyết tiêu hóa & chảy máu nội tạng cực kỳ nghiêm trọng', rec: 'Chống chỉ định tuyệt đối phối hợp'},
          {d1: 'Aspirin', d2: 'Ibuprofen', sev: 'MODERATE', mech: 'Cạnh tranh vị trí gắn COX-1 tiểu cầu', eff: 'Giảm tác dụng bảo vệ tim mạch của Aspirin và tăng nguy cơ loét dạ dày', rec: 'Uống Aspirin trước Ibuprofen ít nhất 2 giờ'},
          {d1: 'Warfarin', d2: 'Ciprofloxacin', sev: 'MAJOR', mech: 'Ức chế enzym CYP1A2 và CYP3A4 chuyển hóa Warfarin', eff: 'Tăng nồng độ Warfarin máu, gây tăng chỉ số INR và nguy cơ xuất huyết cao', rec: 'Tránh dùng cùng hoặc giảm liều Warfarin và kiểm tra INR hằng ngày'},
          {d1: 'Metformin', d2: 'Iodine Contrast', sev: 'MAJOR', mech: 'Thuốc cản quang gây suy thận cấp làm tích tụ Metformin', eff: 'Tăng nguy cơ nhiễm toan Axit Lactic đe dọa tính mạng', rec: 'Ngừng Metformin 48 giờ trước và sau khi chụp cản quang'},
          {d1: 'Amlodipine', d2: 'Atorvastatin', sev: 'MINOR', mech: 'Ức chế nhẹ CYP3A4', eff: 'Tăng nhẹ nồng độ Atorvastatin trong máu', rec: 'Theo dõi dấu hiệu đau cơ, không vượt quá 20mg Atorvastatin'},
          {d1: 'Enalapril', d2: 'Spironolactone', sev: 'MAJOR', mech: 'Cùng giảm thải trừ Kali qua đường tiết niệu', eff: 'Tăng Kali máu nghiêm trọng gây rối loạn nhịp tim tử vong', rec: 'Thận trọng theo dõi sát chỉ số Kali máu định kỳ'},
          {d1: 'Tramadol', d2: 'Sertraline', sev: 'CRITICAL', mech: 'Tăng nồng độ Serotonin trong khe Synap thần kinh', eff: 'Hội chứng Serotonin cấp (Sốt cao, co giật, ảo giác, tử vong)', rec: 'Chống chỉ định phối hợp Tramadol với thuốc SSRI'},
          {d1: 'Omeprazole', d2: 'Clopidogrel', sev: 'MAJOR', mech: 'Omeprazole ức chế CYP2C19 chuyển hóa Clopidogrel thành dạng có hoạt tính', eff: 'Giảm hiệu quả kháng tiểu cầu của Clopidogrel, tăng nguy cơ tái nhồi máu cơ tim', rec: 'Thay Omeprazole bằng Pantoprazole hoặc Rabeprazole'},
          {d1: 'Allopurinol', d2: 'Amoxicillin', sev: 'MODERATE', mech: 'Tăng phản ứng quá mẫn da', eff: 'Tăng mạnh tỷ lệ phát ban da mày đay', rec: 'Theo dõi sát phản ứng phát ban da ở bệnh nhân'}
        ] AS item
        MATCH (a:Drug {name: item.d1}), (b:Drug {name: item.d2})
        CREATE (a)-[:INTERACTS_WITH {
          severity: item.sev,
          mechanism: item.mech,
          clinical_effect: item.eff,
          recommendation: item.rec
        }]->(b)
        """)

        # ============================================================
        # 6. CREATE DRUG-ALLERGEN CROSS-REACTIVITY (HAS_ALLERGEN)
        # ============================================================
        logger.info("Creating HAS_ALLERGEN relationships...")
        session.run("""
        UNWIND [
          {drug: 'Amoxicillin', allergen: 'Penicillin', risk: 'HIGH', note: 'Dị ứng chéo nhóm Beta-lactam'},
          {drug: 'Ceftriaxone', allergen: 'Cephalosporin', risk: 'HIGH', note: 'Dị ứng kháng sinh nhóm Cephalosporin'},
          {drug: 'Ceftriaxone', allergen: 'Penicillin', risk: 'MODERATE', note: 'Nguy cơ dị ứng chéo 5-10% với Penicillin'},
          {drug: 'Ibuprofen', allergen: 'NSAID', risk: 'HIGH', note: 'Dị ứng chéo nhóm NSAIDs'},
          {drug: 'Aspirin', allergen: 'Aspirin', risk: 'HIGH', note: 'Dị ứng hoạt chất Salicylate'},
          {drug: 'Ibuprofen', allergen: 'Aspirin', risk: 'HIGH', note: 'Dị ứng chéo giữa NSAID và Aspirin'},
          {drug: 'Azithromycin', allergen: 'Macrolide', risk: 'HIGH', note: 'Dị ứng nhóm Macrolide'},
          {drug: 'Ciprofloxacin', allergen: 'Quinolone', risk: 'HIGH', note: 'Dị ứng nhóm Quinolone'},
          {drug: 'Morphine', allergen: 'Opioid', risk: 'HIGH', note: 'Dị ứng nhóm thuốc giảm đau Opioid'},
          {drug: 'Tramadol', allergen: 'Opioid', risk: 'MODERATE', note: 'Dị ứng chéo với dòng Opioid'}
        ] AS item
        MATCH (d:Drug {name: item.drug}), (a:Allergen {name: item.allergen})
        CREATE (d)-[:HAS_ALLERGEN {risk_level: item.risk, note: item.note}]->(a)
        """)

        # ============================================================
        # 7. CREATE SYMPTOM-DISEASE INDICATIONS (INDICATES)
        # ============================================================
        logger.info("Creating INDICATES relationships...")
        session.run("""
        UNWIND [
          {sym: 'Sốt', dis: 'Sốt xuất huyết Dengue', freq: 'ALWAYS'},
          {sym: 'Xuất huyết dưới da', dis: 'Sốt xuất huyết Dengue', freq: 'OFTEN'},
          {sym: 'Đau đầu', dis: 'Sốt xuất huyết Dengue', freq: 'OFTEN'},
          {sym: 'Ho', dis: 'Viêm phế quản cấp', freq: 'ALWAYS'},
          {sym: 'Khàn tiếng', dis: 'Viêm phế quản cấp', freq: 'OFTEN'},
          {sym: 'Ho', dis: 'Viêm phổi cộng đồng', freq: 'ALWAYS'},
          {sym: 'Khó thở', dis: 'Viêm phổi cộng đồng', freq: 'OFTEN'},
          {sym: 'Sốt', dis: 'Viêm phổi cộng đồng', freq: 'OFTEN'},
          {sym: 'Đau bụng', dis: 'Viêm loét dạ dày thực quản', freq: 'ALWAYS'},
          {sym: 'Ợ chua', dis: 'Trào ngược dạ dày thực quản GERD', freq: 'ALWAYS'},
          {sym: 'Buồn nôn', dis: 'Trào ngược dạ dày thực quản GERD', freq: 'OFTEN'},
          {sym: 'Thở khò khè', dis: 'Hen phế quản', freq: 'ALWAYS'},
          {sym: 'Khó thở', dis: 'Hen phế quản', freq: 'ALWAYS'},
          {sym: 'Tăng đường huyết', dis: 'Đái tháo đường Type 2', freq: 'ALWAYS'},
          {sym: 'Giảm cân nhanh', dis: 'Đái tháo đường Type 2', freq: 'OFTEN'},
          {sym: 'Đau ngực', dis: 'Nhồi máu cơ tim cấp', freq: 'ALWAYS'},
          {sym: 'Hồi hộp đánh trống ngực', dis: 'Rung nhĩ', freq: 'ALWAYS'},
          {sym: 'Phù chân', dis: 'Suy tim mãn tính', freq: 'OFTEN'},
          {sym: 'Chóng mặt', dis: 'Rối loạn tiền đình', freq: 'ALWAYS'},
          {sym: 'Đau khớp', dis: 'Gút cấp và mãn', freq: 'ALWAYS'},
          {sym: 'Đái buốt', dis: 'Nhiễm trùng đường tiết niệu', freq: 'ALWAYS'},
          {sym: 'Vàng da', dis: 'Suy gan mãn tính', freq: 'ALWAYS'}
        ] AS item
        MATCH (s:Symptom {name: item.sym}), (d:Disease {name: item.dis})
        CREATE (s)-[:INDICATES {frequency: item.freq}]->(d)
        """)

        # ============================================================
        # 8. CREATE DISEASE-DRUG TREATMENT PROTOCOLS (TREATED_BY)
        # ============================================================
        logger.info("Creating TREATED_BY relationships...")
        session.run("""
        UNWIND [
          {dis: 'Sốt xuất huyết Dengue', drug: 'Paracetamol', line: '1ST_LINE', notes: 'Hạ sốt duy nhất an toàn. Tuyệt đối chống chỉ định Aspirin / NSAID'},
          {dis: 'Tăng huyết áp nguyên phát', drug: 'Amlodipine', line: '1ST_LINE', notes: 'Lựa chọn đầu tay hạ áp nhóm Chẹn kênh Canxi'},
          {dis: 'Tăng huyết áp nguyên phát', drug: 'Enalapril', line: '1ST_LINE', notes: 'Lựa chọn đầu tay nhóm ACEi (Bảo vệ thận ở bệnh nhân tiểu đường)'},
          {dis: 'Tăng huyết áp nguyên phát', drug: 'Losartan', line: '1ST_LINE', notes: 'Thay thế ACEi khi bệnh nhân bị ho khan'},
          {dis: 'Đái tháo đường Type 2', drug: 'Metformin', line: '1ST_LINE', notes: 'Lựa chọn đầu tay hạ đường huyết ưu tiên'},
          {dis: 'Đái tháo đường Type 2', drug: 'Gliclazide', line: '2ND_LINE', notes: 'Phối hợp khi Metformin chưa đạt HbA1c mục tiêu'},
          {dis: 'Viêm loét dạ dày thực quản', drug: 'Omeprazole', line: '1ST_LINE', notes: 'Ức chế tiết Axit dạ dày 4-8 tuần'},
          {dis: 'Trào ngược dạ dày thực quản GERD', drug: 'Ranitidine', line: '2ND_LINE', notes: 'Kháng H2 giảm tiết axit vào ban đêm'},
          {dis: 'Viêm phổi cộng đồng', drug: 'Amoxicillin', line: '1ST_LINE', notes: 'Kháng sinh ngoại trú đầu tay'},
          {dis: 'Viêm phổi cộng đồng', drug: 'Azithromycin', line: '1ST_LINE', notes: 'Phối hợp điều trị vi khuẩn không điển hình'},
          {dis: 'Hen phế quản', drug: 'Salbutamol', line: '1ST_LINE', notes: 'Thuốc cắt cơn hen cấp tức thì'},
          {dis: 'Hen phế quản', drug: 'Montelukast', line: '2ND_LINE', notes: 'Dự phòng cơn hen phế quản ban đêm'},
          {dis: 'Rung nhĩ', drug: 'Warfarin', line: '1ST_LINE', notes: 'Kháng đông ngừa đột quỵ huyết khối'},
          {dis: 'Nhồi máu cơ tim cấp', drug: 'Aspirin', line: '1ST_LINE', notes: 'Kháng tiểu cầu cấp cứu ban đầu'},
          {dis: 'Nhồi máu cơ tim cấp', drug: 'Clopidogrel', line: '1ST_LINE', notes: 'Kháng tiểu cầu kép cùng Aspirin'},
          {dis: 'Rối loạn lipid máu', drug: 'Atorvastatin', line: '1ST_LINE', notes: 'Hạ LDL-Cholesterol ngừa xơ vữa'},
          {dis: 'Gút cấp và mãn', drug: 'Colchicine', line: '1ST_LINE', notes: 'Giảm đau chống viêm trong gút cấp 24 giờ đầu'},
          {dis: 'Gút cấp và mãn', drug: 'Allopurinol', line: '1ST_LINE', notes: 'Hạ Urat máu dự phòng tái phát (không dùng trong đợt cấp)'}
        ] AS item
        MATCH (d:Disease {name: item.dis}), (dr:Drug {name: item.drug})
        CREATE (d)-[:TREATED_BY {line_of_treatment: item.line, notes: item.notes}]->(dr)
        """)

        # Verification query
        result = session.run("MATCH (n) RETURN count(n) AS nodes")
        nodes_count = result.single()["nodes"]
        rel_result = session.run("MATCH ()-[r]->() RETURN count(r) AS rels")
        rels_count = rel_result.single()["rels"]

        logger.info(f"🎉 SUCCESSFULLY SEEDED 100+ NODES MEDICAL NEO4J GRAPH! Created {nodes_count} Nodes and {rels_count} Relationships.")

    driver.close()

if __name__ == "__main__":
    seed_graph()
