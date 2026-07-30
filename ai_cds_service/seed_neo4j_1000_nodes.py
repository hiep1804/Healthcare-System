import os
import sys
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedNeo4j1000")

def generate_1000_nodes_data():
    # 1. 350 Drugs
    drug_classes = [
        ("Kháng sinh Beta-lactam", "J01C"), ("Kháng sinh Macrolide", "J01F"),
        ("Kháng sinh Quinolone", "J01M"), ("Kháng sinh Cephalosporin", "J01D"),
        ("Thuốc Hạ áp Chẹn Canxi", "C08C"), ("Thuốc Hạ áp Ức chế men chuyển", "C09A"),
        ("Thuốc Hạ áp Chẹn ARB", "C09C"), ("Thuốc Hạ áp Chẹn Beta", "C07A"),
        ("Thuốc Lợi tiểu", "C03A"), ("Thuốc Hạ lipid Statin", "C10A"),
        ("Thuốc Antidiabetic Biguanide", "A10B"), ("Thuốc Antidiabetic Sulfonylurea", "A10B"),
        ("Thuốc Antidiabetic SGLT2i", "A10B"), ("Thuốc Antidiabetic DPP4i", "A10B"),
        ("Thuốc NSAID Giảm đau", "M01A"), ("Thuốc Opioid Giảm đau", "N02A"),
        ("Thuốc Corticosteroid", "H02A"), ("Thuốc Kháng Histamine H1", "R06A"),
        ("Thuốc Giãn phế quản", "R03A"), ("Thuốc PPI Dạ dày", "A02B"),
        ("Thuốc An thần Benzodiazepine", "N05B"), ("Thuốc Chống trầm cảm SSRI", "N06A"),
        ("Thuốc Chống co giật", "N03A"), ("Thuốc Kháng đông máu", "B01A")
    ]

    base_drugs = [
        ("Aspirin", "B01AC06", "Kháng tiểu cầu", "81mg - 325mg/ngày"),
        ("Warfarin", "B01AA03", "Kháng đông máu", "2mg - 5mg/ngày"),
        ("Paracetamol", "N02BE01", "Hạ sốt giảm đau", "500mg - 1000mg/lần"),
        ("Amoxicillin", "J01CA04", "Kháng sinh Beta-lactam", "500mg mỗi 8 giờ"),
        ("Ibuprofen", "M01AE01", "Kháng viêm NSAID", "400mg mỗi 6 giờ"),
        ("Clopidogrel", "B01AC04", "Kháng tiểu cầu", "75mg/ngày"),
        ("Metformin", "A10BA02", "Hạ đường huyết Biguanide", "500mg - 1000mg/lần"),
        ("Atorvastatin", "C10AA05", "Hạ lipid máu Statin", "10mg - 40mg/ngày"),
        ("Amlodipine", "C08CA01", "Hạ áp Chẹn kênh Canxi", "5mg - 10mg/ngày"),
        ("Enalapril", "C09AA02", "Hạ áp Ức chế men chuyển ACE", "5mg - 20mg/ngày"),
        ("Losartan", "C09CA01", "Hạ áp Chẹn thụ thể ARB", "50mg - 100mg/ngày"),
        ("Omeprazole", "A02BC01", "Ức chế bơm Proton PPI", "20mg - 40mg/ngày"),
        ("Ranitidine", "A02BA02", "Kháng H2 dạ dày", "150mg x 2 lần/ngày"),
        ("Azithromycin", "J01FA10", "Kháng sinh Macrolide", "500mg/ngày x 3 ngày"),
        ("Ciprofloxacin", "J01MA02", "Kháng sinh Quinolone", "500mg x 2 lần/ngày"),
        ("Ceftriaxone", "J01DD04", "Kháng sinh Cephalosporin TH3", "1g - 2g/ngày"),
        ("Prednisolone", "H02AB06", "Corticoid chống viêm", "5mg - 60mg/ngày"),
        ("Dexamethasone", "H02AB02", "Corticoid mạnh", "0.5mg - 10mg/ngày"),
        ("Salbutamol", "R03AC02", "Giãn phế quản Beta-2", "2-4mg/lần"),
        ("Montelukast", "R03DC03", "Kháng Leukotriene", "10mg/ngày"),
        ("Loratadine", "R06AX13", "Kháng Histamine H1 TH2", "10mg/ngày"),
        ("Cetirizine", "R06AE07", "Kháng Histamine H1 TH2", "10mg/ngày"),
        ("Diazepam", "N05BA01", "An thần Benzodiazepine", "2mg - 10mg/ngày"),
        ("Sertraline", "N06AB06", "Chống trầm cảm SSRI", "50mg - 100mg/ngày"),
        ("Furosemide", "C03CA01", "Lợi tiểu quai", "20mg - 80mg/ngày"),
        ("Hydrochlorothiazide", "C03AA03", "Lợi tiểu Thiazide", "12.5mg - 25mg/ngày"),
        ("Spironolactone", "C03DA01", "Lợi tiểu tiết kiệm Kali", "25mg - 100mg/ngày"),
        ("Insulin Regular", "A10AB01", "Insulin hạ đường huyết", "Tùy chỉnh"),
        ("Gliclazide", "A10BB09", "Hạ đường huyết Sulfonylurea", "30mg - 120mg/ngày"),
        ("Tramadol", "N02AJ13", "Giảm đau Opioid nhẹ", "50mg - 100mg/lần"),
        ("Morphine", "N02AA01", "Giảm đau Opioid mạnh", "10mg - 30mg/lần"),
        ("Allopurinol", "M04AA01", "Hạ Acid Uric máu (Gút)", "100mg - 300mg/ngày"),
        ("Colchicine", "M04AC01", "Điều trị gút cấp", "1mg/lần"),
        ("Levothyroxine", "H03AA01", "Hormone tuyến giáp", "25mcg - 150mcg/ngày"),
        ("Metoclopramide", "A03FA01", "Chống nôn & nhu động", "10mg/lần")
    ]

    drugs = [{'name': d[0], 'atc': d[1], 'class': d[2], 'dosage': d[3]} for d in base_drugs]
    
    # Generate additional 315 drugs to reach 350 drugs
    drug_prefixes = ["Cef", "Levo", "Moxi", "Val", "Biso", "Metop", "Carve", "Panto", "Rabe", "Esome", "Rivarox", "Apix", "Dabi", "Empag", "Dapag", "Sitag", "Vildag", "Linag", "Pioglit", "Rosug", "Simvas", "Pravas", "Fenofib", "Gemfib", "Gabap", "Pregab", "Dulox", "Fluox", "Escital", "Venlaf", "Quetiap", "Olanzap", "Risper", "Haloper", "Aripip", "Alpraz", "Loraz", "Clonaz", "Midaz", "Zolpid", "Bupren", "Fentany", "Oxycod", "Methad", "Nalox", "Sumatr", "Zolmitr", "Ergot", "Domper", "Ondans", "Granis", "Aprepit", "Loper", "Diosm", "Lactu", "Polyeth", "Bisac", "Sulfasal", "Mesal", "Inflix", "Adalim", "Ritux", "Methot", "Azathio", "Cyclosp", "Tacrol", "Mycophen", "Everol", "Sirol", "Tamsul", "Silod", "Finast", "Dutast", "Sildena", "Tadala", "Vardena", "Alprost", "Oxybut", "Solifen", "Mirabeg", "Desmopr", "Oxytoc", "Dinopr", "Mifepr", "Misopr", "Tranex", "Aminoc", "Phytomen", "Protami", "Heparin", "Enoxap", "Daltep", "Fondap", "Bivalir", "Altepl", "Tenect", "Retepl", "Urokin", "Streptok", "Berber", "Artemis", "Chloroq", "Hydroxyc", "Quinine", "Mefloq", "Proguan", "Atovaq", "Pyrimeth", "Sulfad", "Metronid", "Tinid", "Secnid", "Albend", "Mebend", "Ivermect", "Praziquant", "Permeth", "Malath", "Crotam", "Terbinaf", "Itracona", "Flucona", "Voricona", "Posacona", "Isavucona", "Caspofung", "Micafung", "Anidulaf", "Amphoter", "Nystat", "Griseo", "Flucyt", "Acyclovir", "Valacycl", "Gancicl", "Valganc", "Foscarn", "Cidofov", "Oseltam", "Zanam", "Peram", "Balox", "Ribavir", "Sofosb", "Velpat", "Ledip", "Voxil", "Glecap", "Pibrent", "Tenofov", "Entec", "Lamiv", "Emtric", "Abac", "Zidov", "Efavir", "Rilpiv", "Dolut", "Bict", "Ralteg", "Darun", "Atazan", "Ritonav", "Cobic", "Interfer", "Peginterf", "Paliviz", "Inflix", "Etaner", "Tociliz", "Secuk", "Ixekiz", "Ustekin", "Dupilum", "Omaliz", "Benral", "Mepoliz", "Resliz", "Nucala", "Fasenra", "Xolair", "Dupixent", "Stelara", "Cosentyx", "Taltz", "Actemra", "Enbrel", "Remicade", "Humira", "Avastin", "Herceptin", "Mabthera", "Keytruda", "Opdivo", "Tecentriq", "Iervoy", "Imfinzi", "Bavencio", "Libtayo", "Enhertu", "Kadcyla", "Perjeta", "Cyramza", "Erbitux", "Vectibix", "Tarceva", "Iressa", "Tagrisso", "Xalkori", "Alecensa", "Zykadia", "Alunbrig", "Lorbret", "Venclexta", "Ibrut", "Calquence", "Brukinsa", "Imbruvica", "Jakafe", "Inrebic", "Jakavi", "Xeljanz", "Olumiant", "Rinvoq", "Cibinqo", "Jyseleca", "Otezla", "Apremil", "Thalid", "Lenalid", "Pomalid", "Revlimid", "Pomalyst", "Velcade", "Kyprolis", "Ninlaro", "Darzalex", "Sarclisa", "Elotuz", "Blincyto", "Kymriah", "Yescarta", "Tecartus", "Abecma", "Carvykti", "Zolgensma", "Spinraza", "Evrysdi", "Luxturna", "Exondys", "Vyondys", "Viltepso", "Amondys", "Casgevy", "Lyfgenia", "Roctavian", "Hemgenix", "Valoctocogene", "Etranacogene", "Delandistrogene", "Beremagene", "Pegvaliase", "Paliperidone", "Lurasidone", "Cariprazine", "Brexpiprazole", "Pimavanserin", "Lumateperone", "Suborexant", "Lemborexant", "Daridorexant", "Pitolisant", "Solriamfetol", "Sodium Oxybate", "Tasimelteon", "Deutetrabenazine", "Valbenazine", "Tetrabenazine", "Riluzole", "Edaravone", "Tafenocrine", "Buparvaquone", "Halofantrine", "Lumefantrine", "Piperaquine", "Pyronaridine", "Artenimol", "Artemether", "Artesunate", "Dihydroartemisinin"]
    
    for i in range(len(drugs), 350):
        prefix = drug_prefixes[i % len(drug_prefixes)]
        suffix = random.choice(["zol", "cin", "mab", "tin", "vir", "lol", "pril", "sartan", "pine", "dronate", "statin", "glin", "gliptin", "gliflozin", "prazole", "tidine"])
        cls_info = drug_classes[i % len(drug_classes)]
        name = f"{prefix}{suffix}-{i+100}"
        atc = f"{cls_info[1]}{random.randint(10,99)}"
        drugs.append({'name': name, 'atc': atc, 'class': cls_info[0], 'dosage': f"{random.choice([5,10,20,50,100,500])}mg/ngày"})

    # 2. 250 Diseases
    disease_categories = [
        ("Tim mạch", "I"), ("Hô hấp", "J"), ("Tiêu hóa", "K"), ("Nội tiết", "E"),
        ("Thần kinh", "G"), ("Nhiễm trùng", "A"), ("Xương khớp", "M"), ("Thận tiết niệu", "N"),
        ("Tâm thần", "F"), ("Da liễu", "L"), ("Huyết học", "D"), ("Ung bướu", "C")
    ]
    
    base_diseases = [
        ("Sốt xuất huyết Dengue", "A90", "Nhiễm virus Dengue do muỗi Aedes"),
        ("Tăng huyết áp nguyên phát", "I10", "Tăng áp lực máu động mạch mạn tính"),
        ("Đái tháo đường Type 2", "E11", "Rối loạn chuyển hóa đường do đề kháng Insulin"),
        ("Viêm phế quản cấp", "J20", "Nhiễm trùng niêm mạc phế quản"),
        ("Viêm phổi cộng đồng", "J18", "Nhiễm trùng tổn thương nhu mô phổi"),
        ("Viêm loét dạ dày thực quản", "K27", "Viêm loét tổn thương niêm mạc tiêu hóa"),
        ("Trào ngược dạ dày GERD", "K21", "Dịch vị dạ dày trào ngược thực quản"),
        ("Hen phế quản", "J45", "Viêm mạn tính đường hô hấp co thắt phế quản"),
        ("Bệnh phổi tắc nghẽn COPD", "J44", "Tắc nghẽn luồng khí thở không phục hồi"),
        ("Suy tim mãn tính", "I50", "Tim giảm khả năng bơm máu"),
        ("Xơ vữa động mạch", "I70", "Lắng đọng mảng xơ vữa trong lòng mạch"),
        ("Rung nhĩ", "I48", "Rối loạn nhịp tim nhanh không đều ở tâm nhĩ"),
        ("Gút cấp và mãn", "M10", "Lắng đọng tinh thể Urat tại các khớp"),
        ("Rối loạn lipid máu", "E78", "Tăng Cholesterol / Triglyceride máu"),
        ("Viêm họng cấp", "J02", "Viêm nhiễm trùng cấp tính vùng họng"),
        ("Viêm xoang cấp", "J01", "Viêm nhiễm trùng các xoang cạnh mũi"),
        ("Nhiễm trùng đường tiết niệu", "N39", "Nhiễm khuẩn vi sinh vật đường niệu"),
        ("Suy gan mãn tính", "K72", "Tổn thương tế bào gan di tiến hoại tử"),
        ("Suy thận mãn tính", "N18", "Giảm mức lọc cầu thận tiến triển kéo dài"),
        ("Rối loạn lo âu lan tỏa", "F41", "Trạng thái lo âu căng thẳng quá mức"),
        ("Trầm cảm nặng", "F32", "Rối loạn khí sắc giảm hứng thú năng lượng"),
        ("Rối loạn tiền đình", "H81", "Tổn thương tiền đình gây mất thăng bằng"),
        ("Nhồi máu cơ tim cấp", "I21", "Hoại tử cơ tim do thiếu máu cục bộ"),
        ("Viêm khớp dạng thấp", "M05", "Bệnh tự miễn gây viêm mạn tính nhiều khớp"),
        ("Đau đầu Migraine", "G43", "Đau đầu nửa đầu nguyên phát dạng mạch máu")
    ]
    diseases = [{'name': d[0], 'icd': d[1], 'desc': d[2]} for d in base_diseases]

    for i in range(len(diseases), 250):
        cat = disease_categories[i % len(disease_categories)]
        name = f"Bệnh lý {cat[0]} Chuyên sâu Type-{i+1}"
        icd = f"{cat[1]}{random.randint(10,99)}.{random.randint(0,9)}"
        diseases.append({'name': name, 'icd': icd, 'desc': f"Tổn thương bệnh lý hệ {cat[0]} theo tiêu chuẩn ICD-10 ({icd})"})

    # 3. 250 Symptoms
    symptom_types = ["Cấp tính", "Mãn tính", "Từng đợt", "Cơ năng", "Thực thể"]
    base_symptoms = [
        "Sốt", "Ho", "Đau đầu", "Đau bụng", "Khó thở", "Xuất huyết dưới da",
        "Tăng đường huyết", "Đau ngực", "Chóng mặt", "Ợ chua", "Buồn nôn",
        "Tiêu chảy", "Đau khớp", "Phù chân", "Khàn tiếng", "Mất ngủ",
        "Hồi hộp đánh trống ngực", "Thở khò khè", "Mệt mỏi kéo dài", "Đái buốt",
        "Vàng da", "Đau vùng hạ sườn phải", "Co thắt cơ", "Phát ban da", "Giảm cân nhanh"
    ]
    symptoms = [{'name': s, 'desc': f"Triệu chứng lâm sàng {s}"} for s in base_symptoms]
    
    extra_sym_names = [
        "Tăng huyết áp đột ngột", "Hạ huyết áp tư thế", "Mạch chậm bất thường", "Thở nhanh nông", "Co giật toàn thân",
        "Run tay chân", "Liệt nửa người", "Mất ngôn ngữ", "Nói ngọng", "Nhìn đôi (Song thị)",
        "Giảm thị lực đột ngột", "Ù tai", "Giảm thính lực", "Chảy máu cam", "Chảy máu chân răng",
        "Đái ra máu (Huyết niệu)", "Đái ít (Thiểu niệu)", "Đái nhiều (Đa niệu)", "Đái đêm", "Tiểu không tự chủ",
        "Phù mặt", "Phù toàn thân", "Bụng chướng cổ chướng", "Gan to", "Lách to",
        "Hạch cổ sưng đau", "Đau thắt lưng", "Đau thần kinh tọa", "Tê bì chân tay", "Yếu cơ tiến triển",
        "Cứng khớp buổi sáng", "Sưng đỏ khớp ngón", "Khô mắt khô miệng", "Rụng tóc nhiều", "Tăng mồ hôi đêm",
        "Sợ ánh sáng", "Cổ cứng", "Dấu hiệu Meningism", "Ảo giác thị giác", "Ảo giác thính giác",
        "Ho ra máu", "Nôn ra máu", "Đi ngoài phân đen", "Phân có nhầy máu", "Táo bón kéo dài",
        "Khó nuốt (Nuốt nghẹn)", "Nuốt đau", "Cảm giác nghẹn vùng cổ", "Tăng cân đột ngột", "Da khô nứt nẻ",
        "Ngứa toàn thân", "Mề đay cấp", "Mụn mủ ngoài da", "Loét niêm mạc miệng", "Viêm lưỡi gồ",
        "Cảm giác kiến bò", "Mất cảm giác nông", "Tăng cảm giác đau", "Sợ lạnh", "Sợ nóng",
        "Hạ thân nhiệt", "Vàng mắt", "Xanh xao niêm mạc nhợt", "Móng tay dùi trống", "Ban đỏ hình cánh bướm",
        "Xơ cứng da", "Khô da nứt nẻ", "Mắt lồi", "Bướu cổ to", "Nhịp tim không đều",
        "Cơn đau thắt ngực không ổn định", "Đau cách hồi cẳng chân", "Tím tái đầu chi (Cyanosis)", "Mạch ngoại vi yếu", "Tiếng thổi ở tim",
        "Tiếng rít thanh quản (Stridor)", "Tiếng ngáy ngưng thở khi ngủ", "Rần rần vùng ngực", "Vú to ở nam giới", "Rối loạn kinh nguyệt",
        "Mất kinh nguyên phát", "Đau kinh dữ dội", "Xuất huyết âm đạo bất thường", "Rối loạn cương dương", "Giảm ham muốn tình dục",
        "Co thắt cơ thắt lưng", "Đau vùng chậu", "Ấn đau điểm niệu quản", "Cầu bàng quang dương tính", "Tiếng cọ màng tim",
        "Tiếng cọ màng phổi", "Rì rào phế nang giảm", "Đờm mủ xanh vàng", "Đờm rỉ sắt", "Nước tiểu sẫm màu như nước vối",
        "Nước tiểu đục có cặn", "Phân bạc màu như cò", "Cảm giác sợ hãi tột cùng", "Cơn hoảng loạn Panick", "Mất trí nhớ ngắn hạn",
        "Lú lẫn cấp tính (Delirium)", "Mất định hướng không gian", "Giảm tập trung chú ý", "Tâm trạng trầm cảm u ủ", "Hưng cảm tăng hoạt động",
        "Hành vi xung động", "Áo tưởng bị hại", "Suy giảm nhận thức", "Ngủ ngáy to", "Cơn giật cơ ngắt quãng",
        "Giật cơ mặt", "Mất thăng bằng dáng đi", "Dáng đi lắc lư", "Run khi nghỉ (Resting tremor)", "Run khi hành động",
        "Cứng cống kiểu bánh xe răng cưa", "Mặt như mặt nạ", "Cảm giác rát bỏng bàn chân", "Viêm đau thần kinh liên sườn", "Đau vai lan xuống tay",
        "Sưng đau tuyến mang tai", "Đau góc hàm", "Khó há miệng (Trismus)", "Nổi mụn nước dọc dây thần kinh", "Đau nhức hốc mắt",
        "Mắt đỏ kết mạc", "Tăng áp lực nội nhãn", "Xuất huyết kết mạc", "Lỗ tử cung mở", "Cổ tử cung xóa mở",
        "Cơn co tử cung", "Rỉ ối", "Rau tiền đạo chảy máu", "Vỡ ối sớm", "Chửa ngoài tử cung vỡ",
        "Viêm phần phụ sưng đau", "Khí hư ra nhiều mùi hôi", "Huyết trắng đóng cặn", "Ngứa âm hộ âm đạo", "Xoắn tinh hoàn đau đột ngột",
        "Tràn dịch tinh mạc", "Sưng đau mào tinh hoàn", "Phì đại tuyến tiền liệt", "Bí tiểu cấp", "Sỏi đường tiết niệu di chuyển",
        "Cơn đau quặn thận", "Cơn đau quặn mật", "Viêm túi mật ấn Murphy dương tính", "Dấu hiệu Blumberg bụng dương tính", "Dấu hiệu Rovsing ruột thừa",
        "Điểm McBurney ấn đau nhói", "Phản ứng ứng cơ thành bụng", "Cảm ứng màng bụng", "Tiếng gõ đục vùng thấp", "Quai ruột nổi",
        "Dấu hiệu Rắn bò", "Tiếng trung tiện biến mất", "Quá trướng bụng", "Dấu hiệu Grey Turner bầm tím", "Dấu hiệu Cullen quanh rốn",
        "Huyết khối tĩnh mạch sâu (DVT)", "Dấu hiệu Homans dương tính", "Tắc mạch phổi đột ngột", "Xẹp phổi", "Tràn dịch màng phổi",
        "Tràn khí màng phổi", "Tràn mủ màng phổi", "Tràn máu màng phổi", "Khai khí quản cấp", "Mở phế quản",
        "Sốc nhiễm trùng", "Sốc phản vệ", "Sốc mất máu", "Sốc tim", "Sốc thần kinh",
        "Hội chứng suy hô hấp cấp ARDS", "Hội chứng đông máu rải rác DIC", "Suy đa cơ quan MODS", "Ngừng tuần hoàn hô hấp", "Tử vong lâm sàng"
    ]
    for idx, sym_name in enumerate(extra_sym_names):
        symptoms.append({'name': sym_name, 'desc': f"Triệu chứng lâm sàng {sym_name}"})
        
    for i in range(len(symptoms), 250):
        sym_type = symptom_types[i % len(symptom_types)]
        symptoms.append({'name': f"Triệu chứng {sym_type} Mô phỏng-{i+1}", 'desc': f"Dấu hiệu lâm sàng {sym_type} số {i+1}"})

    # 4. 150 Allergens & Lab Parameters
    base_allergens = [
        "Penicillin", "Cephalosporin", "NSAID", "Aspirin", "Sulfa", "Macrolide",
        "Quinolone", "Tetracycline", "Opioid", "Barbiturate", "Lidocaine",
        "Iodine Contrast", "Aminoglycoside", "Carbapenem", "Anticonvulsant"
    ]
    allergens = [{'name': a, 'desc': f"Nhóm dị ứng {a}"} for a in base_allergens]

    lab_markers = [
        "Chỉ số HbA1c", "Troponin I tim", "Troponin T tim", "Protein C phản ứng CRP", "Chỉ số Creatinine máu",
        "Men gan ALT (GPT)", "Men gan AST (GOT)", "Chỉ số D-dimer", "Chỉ số Pro-BNP", "Chỉ số Ferritin máu",
        "Nồng độ Kali máu", "Nồng độ Natri máu", "Nồng độ Canxi máu", "Khí máu động mạch PaO2", "Khí máu động mạch PaCO2",
        "Chỉ số Bạch cầu WBC", "Chỉ số Tiểu cầu PLT", "Chỉ số Hồng cầu RBC", "Tốc độ lắng máu ESR", "Chỉ số Prothrombin PT/INR",
        "Chỉ số Ure máu", "Bilirubin toàn phần", "Bilirubin trực tiếp", "Chỉ số Albumin máu", "Chỉ số Acid Uric máu"
    ]
    for marker in lab_markers:
        allergens.append({'name': marker, 'desc': f"Thông số xét nghiệm {marker}"})

    for i in range(len(allergens), 150):
        allergens.append({'name': f"Chỉ số Xét nghiệm / Chất Dị ứng #{i+1}", 'desc': f"Thông số xét nghiệm / Dị nguyên thứ {i+1}"})

    return drugs, diseases, symptoms, allergens

def seed_1000_nodes():
    from neo4j import GraphDatabase
    uri = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD', 'healthcare_neo4j_2026')

    logger.info(f"Connecting to Neo4j at {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    drugs, diseases, symptoms, allergens = generate_1000_nodes_data()

    total_nodes = len(drugs) + len(diseases) + len(symptoms) + len(allergens)
    logger.info(f"Generated data: {len(drugs)} Drugs, {len(diseases)} Diseases, {len(symptoms)} Symptoms, {len(allergens)} Allergens/Labs. Total Nodes = {total_nodes}")

    with driver.session() as session:
        logger.info("Cleaning old graph nodes & relationships...")
        session.run("MATCH (n) DETACH DELETE n")

        # 1. Batch Create 350 Drug Nodes
        logger.info(f"Inserting {len(drugs)} Drug nodes...")
        session.run("""
        UNWIND $drugs AS d
        CREATE (:Drug {name: d.name, atc_code: d.atc, drug_class: d.class, common_dosage: d.dosage})
        """, {'drugs': drugs})

        # 2. Batch Create 250 Disease Nodes
        logger.info(f"Inserting {len(diseases)} Disease nodes...")
        session.run("""
        UNWIND $diseases AS dis
        CREATE (:Disease {name: dis.name, icd_code: dis.icd, description: dis.desc})
        """, {'diseases': diseases})

        # 3. Batch Create 250 Symptom Nodes
        logger.info(f"Inserting {len(symptoms)} Symptom nodes...")
        session.run("""
        UNWIND $symptoms AS sym
        CREATE (:Symptom {name: sym.name, description: sym.desc})
        """, {'symptoms': symptoms})

        # 4. Batch Create 150 Allergen/Lab Nodes
        logger.info(f"Inserting {len(allergens)} Allergen/Lab nodes...")
        session.run("""
        UNWIND $allergens AS all
        CREATE (:Allergen {name: all.name, description: all.desc})
        """, {'allergens': allergens})

        # 5. Generate 1,500+ Relationships (INTERACTS_WITH, INDICATES, TREATED_BY, HAS_ALLERGEN)
        logger.info("Building 1,500+ Graph Relationships...")

        # A. INTERACTS_WITH (300 drug-drug interactions)
        interactions = []
        severities = ['CRITICAL', 'MAJOR', 'MODERATE', 'MINOR']
        for i in range(300):
            d1 = drugs[i % len(drugs)]['name']
            d2 = drugs[(i * 7 + 3) % len(drugs)]['name']
            if d1 != d2:
                interactions.append({
                    'd1': d1, 'd2': d2,
                    'sev': random.choice(severities),
                    'mech': f"Tương tác chuyển hóa enzym CYP450 giữa {d1} và {d2}",
                    'eff': f"Tăng/giảm nồng độ dược chất {d1} trong máu, cần theo dõi lâm sàng",
                    'rec': f"Thận trọng khi phối hợp {d1} và {d2}, điều chỉnh liều nếu cần"
                })

        session.run("""
        UNWIND $items AS item
        MATCH (a:Drug {name: item.d1}), (b:Drug {name: item.d2})
        CREATE (a)-[:INTERACTS_WITH {
          severity: item.sev,
          mechanism: item.mech,
          clinical_effect: item.eff,
          recommendation: item.rec
        }]->(b)
        """, {'items': interactions})

        # B. INDICATES (500 symptom-disease links)
        indicates = []
        freqs = ['ALWAYS', 'OFTEN', 'SOMETIMES', 'RARE']
        for i in range(500):
            s_name = symptoms[i % len(symptoms)]['name']
            dis_name = diseases[(i * 3 + 1) % len(diseases)]['name']
            indicates.append({'sym': s_name, 'dis': dis_name, 'freq': random.choice(freqs)})

        session.run("""
        UNWIND $items AS item
        MATCH (s:Symptom {name: item.sym}), (d:Disease {name: item.dis})
        CREATE (s)-[:INDICATES {frequency: item.freq}]->(d)
        """, {'items': indicates})

        # C. TREATED_BY (500 disease-drug treatment links)
        treated_by = []
        lines = ['1ST_LINE', '2ND_LINE', 'ALTERNATIVE']
        for i in range(500):
            dis_name = diseases[i % len(diseases)]['name']
            dr_name = drugs[(i * 5 + 2) % len(drugs)]['name']
            treated_by.append({'dis': dis_name, 'drug': dr_name, 'line': random.choice(lines), 'notes': f"Phác đồ điều trị {dis_name} bằng {dr_name}"})

        session.run("""
        UNWIND $items AS item
        MATCH (d:Disease {name: item.dis}), (dr:Drug {name: item.drug})
        CREATE (d)-[:TREATED_BY {line_of_treatment: item.line, notes: item.notes}]->(dr)
        """, {'items': treated_by})

        # D. HAS_ALLERGEN (200 drug-allergen links)
        has_allergen = []
        risks = ['HIGH', 'MODERATE', 'LOW']
        for i in range(200):
            dr_name = drugs[i % len(drugs)]['name']
            all_name = allergens[(i * 2 + 1) % len(allergens)]['name']
            has_allergen.append({'drug': dr_name, 'allergen': all_name, 'risk': random.choice(risks), 'note': f"Dị ứng chéo / chỉ số liên quan giữa {dr_name} và {all_name}"})

        session.run("""
        UNWIND $items AS item
        MATCH (d:Drug {name: item.drug}), (a:Allergen {name: item.allergen})
        CREATE (d)-[:HAS_ALLERGEN {risk_level: item.risk, note: item.note}]->(a)
        """, {'items': has_allergen})

        # Verification query
        result = session.run("MATCH (n) RETURN count(n) AS nodes")
        final_nodes = result.single()["nodes"]
        rel_result = session.run("MATCH ()-[r]->() RETURN count(r) AS rels")
        final_rels = rel_result.single()["rels"]

        logger.info(f"🚀🚀🚀 SUCCESSFULLY SEEDED EXACTLY {final_nodes} NODES AND {final_rels} RELATIONSHIPS IN NEO4J GRAPH!")

    driver.close()

if __name__ == "__main__":
    seed_1000_nodes()
