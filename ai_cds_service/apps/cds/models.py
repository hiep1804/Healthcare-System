import uuid
from django.db import models


# ==========================================
# 1. KNOWLEDGE BASE MODELS (Tri thức Y khoa)
# ==========================================

class Disease(models.Model):
    """Bệnh / Tình trạng bệnh lý (ICD-10)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, unique=True)
    icd_code = models.CharField(max_length=20, blank=True, help_text="Mã ICD-10")
    description = models.TextField(blank=True)
    severity_level = models.CharField(
        max_length=20,
        choices=[('MILD', 'Nhẹ'), ('MODERATE', 'Trung bình'), ('SEVERE', 'Nặng'), ('CRITICAL', 'Nguy kịch')],
        default='MODERATE'
    )
    is_chronic = models.BooleanField(default=False, help_text="Bệnh mãn tính")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'diseases'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.icd_code or 'N/A'})"


class Symptom(models.Model):
    """Triệu chứng lâm sàng"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    body_system = models.CharField(max_length=100, blank=True, help_text="Hệ cơ quan (Hô hấp, Tim mạch...)")
    is_red_flag = models.BooleanField(default=False, help_text="Triệu chứng cờ đỏ / nguy hiểm")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'symptoms'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {'🚩' if self.is_red_flag else ''}"


class Drug(models.Model):
    """Danh mục thuốc & hoạt chất (ATC)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250, unique=True, help_text="Tên hoạt chất / biệt dược")
    atc_code = models.CharField(max_length=20, blank=True, help_text="Mã ATC")
    drug_class = models.CharField(max_length=150, blank=True, help_text="Nhóm thuốc (Kháng sinh, Hạ áp...)")
    dosage_forms = models.CharField(max_length=200, blank=True, help_text="Dạng bào chế (Viên nén, Si-rô...)")
    common_dosage = models.CharField(max_length=200, blank=True, help_text="Liều dùng tham khảo")
    contraindications_text = models.TextField(blank=True, help_text="Chống chỉ định chung")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'drugs'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} [{self.drug_class}]"


class DiseaseSymptom(models.Model):
    """Mapping Bệnh ↔ Triệu chứng"""
    FREQUENCY_CHOICES = [
        ('ALWAYS', 'Luôn có (100%)'),
        ('OFTEN', 'Thường gặp (>70%)'),
        ('SOMETIMES', 'Đôi khi (30-70%)'),
        ('RARE', 'Hiếm gặp (<30%)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='symptom_mappings')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE, related_name='disease_mappings')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='OFTEN')
    specificity = models.DecimalField(max_digits=3, decimal_places=2, default=0.50, help_text="Độ đặc hiệu (0.00-1.00)")

    class Meta:
        db_table = 'disease_symptoms'
        unique_together = ('disease', 'symptom')

    def __str__(self):
        return f"{self.disease.name} -> {self.symptom.name} ({self.frequency})"


class DiseaseTreatment(models.Model):
    """Mapping Bệnh ↔ Thuốc điều trị"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='treatment_mappings')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='disease_treatments')
    line_of_treatment = models.CharField(
        max_length=50,
        choices=[('1ST_LINE', 'Lựa chọn đầu tay'), ('2ND_LINE', 'Lựa chọn hàng 2'), ('ALTERNATIVE', 'Thay thế')],
        default='1ST_LINE'
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'disease_treatments'
        unique_together = ('disease', 'drug')

    def __str__(self):
        return f"{self.disease.name} treated by {self.drug.name} ({self.line_of_treatment})"


class DrugInteraction(models.Model):
    """Bảng Tương tác thuốc - Thuốc"""
    SEVERITY_CHOICES = [
        ('MINOR', 'Nhẹ — Theo dõi'),
        ('MODERATE', 'Trung bình — Thận trọng'),
        ('MAJOR', 'Nặng — Tránh dùng cùng'),
        ('CRITICAL', 'Chống chỉ định tuyệt đối'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drug_a = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='interactions_as_a')
    drug_b = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='interactions_as_b')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MODERATE')
    mechanism = models.TextField(blank=True, help_text="Cơ chế tương tác")
    clinical_effect = models.TextField(blank=True, help_text="Hậu quả lâm sàng (ví dụ: Tăng nguy cơ chảy máu)")
    recommendation = models.TextField(blank=True, help_text="Khuyên dùng / Giải pháp thay thế")

    class Meta:
        db_table = 'drug_interactions'
        unique_together = ('drug_a', 'drug_b')

    def __str__(self):
        return f"{self.drug_a.name} ⚡ {self.drug_b.name} [{self.severity}]"


class DrugAllergenCrossRef(models.Model):
    """Phản ứng chéo giữa Thuốc và Dị ứng nguyên"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='allergen_cross_refs')
    allergen_name = models.CharField(max_length=200, help_text="Tên nhóm dị ứng (Penicillin, Sulfa...)")
    cross_reactivity_probability = models.DecimalField(max_digits=3, decimal_places=2, default=0.10, help_text="Tỷ lệ phản ứng chéo (0.0-1.0)")
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'drug_allergen_cross_refs'

    def __str__(self):
        return f"{self.drug.name} x {self.allergen_name} ({self.cross_reactivity_probability * 100}%)"


# ==========================================
# 2. CONVERSATION & CHAT MODELS
# ==========================================

class CDSConversation(models.Model):
    """Phiên chat AI giữa Bác sĩ và AI CDS cho 1 ca khám"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Đang hoạt động'),
        ('COMPLETED', 'Đã đóng'),
        ('ARCHIVED', 'Đã lưu trữ'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation_id = models.UUIDField(null=True, blank=True, help_text="ID phiên khám từ consultation-service")
    provider_id = models.UUIDField(null=True, blank=True, help_text="ID bác sĩ")
    patient_id = models.UUIDField(null=True, blank=True, help_text="ID bệnh nhân")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    patient_context_snapshot = models.JSONField(default=dict, blank=True, help_text="Snapshot dị ứng, bệnh nền, thuốc của BN khi mở chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cds_conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return f"CDS Session {self.id} (Consultation {self.consultation_id})"


class CDSMessage(models.Model):
    """Tin nhắn trong phiên chat AI CDS"""
    ROLE_CHOICES = [
        ('system', 'Hệ thống'),
        ('doctor', 'Bác sĩ'),
        ('assistant', 'Trợ lý AI'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(CDSConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True, help_text="Thông tin bổ sung (tokens, confidence...)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cds_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:40]}..."


# ==========================================
# 3. RECOMMENDATION MODELS (Khuyến nghị AI)
# ==========================================

class CDSRecommendation(models.Model):
    """Khuyến nghị trích xuất từ AI response mà bác sĩ cần tương tác (Accept/Ignore/Edit)"""
    CATEGORY_CHOICES = [
        ('DRUG_INTERACTION', 'Tương tác thuốc'),
        ('ALLERGY_ALERT', 'Cảnh báo dị ứng'),
        ('DIFFERENTIAL_DIAGNOSIS', 'Gợi ý chẩn đoán phân biệt'),
        ('LAB_INTERPRETATION', 'Diễn giải xét nghiệm'),
        ('TREATMENT_SUGGESTION', 'Gợi ý điều trị'),
        ('DOSAGE_WARNING', 'Cảnh báo liều dùng'),
        ('GENERAL_ADVICE', 'Tư vấn chung'),
    ]

    SEVERITY_CHOICES = [
        ('INFO', 'Thông tin'),
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Nguy kịch'),
    ]

    ACTION_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('ACCEPTED', 'Đã chấp nhận'),
        ('IGNORED', 'Đã bỏ qua'),
        ('EDITED', 'Đã chỉnh sửa'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(CDSConversation, on_delete=models.CASCADE, related_name='recommendations')
    message = models.ForeignKey(CDSMessage, on_delete=models.CASCADE, null=True, blank=True, related_name='recommendations')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='GENERAL_ADVICE')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    summary = models.CharField(max_length=300, help_text="Tóm tắt ngắn gọn khuyến nghị")
    explanation = models.TextField(blank=True, help_text="Giải thích chi tiết")
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=0.85, help_text="Độ tin cậy của AI (0.0-1.0)")
    doctor_action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='PENDING')
    doctor_note = models.TextField(blank=True, help_text="Ghi chú của bác sĩ khi phản hồi")
    acted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cds_recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.summary} ({self.doctor_action})"


# ==========================================
# 4. PROMPT TEMPLATE MODEL
# ==========================================

class PromptTemplate(models.Model):
    """Mẫu System Prompt cho AI CDS"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=50, default='GENERAL')
    system_prompt = models.TextField()
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prompt_templates'

    def __str__(self):
        return f"{self.name} ({self.version})"
