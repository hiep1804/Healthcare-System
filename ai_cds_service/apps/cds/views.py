from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsDoctor, IsDoctorOrAdmin
from .models import (
    CDSConversation, CDSMessage, CDSRecommendation,
    Drug, DrugInteraction, Disease, Symptom
)
from .serializers import (
    CDSConversationSerializer, CDSConversationCreateSerializer,
    CDSMessageSerializer, SendMessageSerializer,
    CDSRecommendationSerializer, ActOnRecommendationSerializer,
    DrugCheckRequestSerializer, DrugInteractionSerializer,
    DiseaseSerializer, SymptomSerializer, DrugSerializer
)
from .ai_service import AICDSService


class CDSConversationListCreateView(APIView):
    """
    POST /api/v1/cds/conversations - Tạo hoặc khôi phục phiên chat AI cho ca khám
    GET /api/v1/cds/conversations - Lấy danh sách các phiên chat
    """
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def get(self, request):
        consultation_id = request.GET.get('consultation_id')
        queryset = CDSConversation.objects.all()
        if consultation_id:
            queryset = queryset.filter(consultation_id=consultation_id)
        serializer = CDSConversationSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = CDSConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        consultation_id = data.get('consultation_id')
        patient_id = data.get('patient_id')
        provider_id = data.get('provider_id')

        force_new = data.get('force_new', True)

        # Reuse existing active conversation ONLY if force_new is False
        if not force_new:
            if consultation_id:
                existing = CDSConversation.objects.filter(consultation_id=consultation_id, status='ACTIVE').first()
            else:
                existing = CDSConversation.objects.filter(consultation_id__isnull=True, status='ACTIVE').first()

            if existing:
                return Response(CDSConversationSerializer(existing).data, status=status.HTTP_200_OK)

        # Fetch patient context if patient_id is available
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        patient_context = AICDSService.fetch_patient_context(patient_id, auth_header) if patient_id else {}

        conversation = CDSConversation.objects.create(
            consultation_id=consultation_id,
            patient_id=patient_id,
            provider_id=provider_id,
            patient_context_snapshot=patient_context
        )

        # Create initial system welcome message
        initial_content = (
            "Xin chào Bác sĩ! Tôi là Trợ lý AI Hỗ trợ Quyết định Lâm sàng (AI CDS).\n"
            "Tôi đã tự động tải dữ liệu dị ứng, bệnh nền và chỉ số sinh tồn của bệnh nhân này. "
            "Bác sĩ có thể hỏi bất kỳ thắc mắc nào về chẩn đoán, tương tác thuốc hoặc hướng điều trị."
        )
        CDSMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=initial_content
        )

        return Response(CDSConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)


class CDSConversationDetailView(APIView):
    """GET /api/v1/cds/conversations/{id} - Xem chi tiết phiên chat"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def get(self, request, conversation_id):
        try:
            conversation = CDSConversation.objects.get(id=conversation_id)
        except CDSConversation.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Không tìm thấy phiên chat AI.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CDSConversationSerializer(conversation)
        return Response(serializer.data)


class CDSSendMessageView(APIView):
    """POST /api/v1/cds/conversations/{id}/messages - Gửi câu hỏi cho AI và nhận câu trả lời"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, conversation_id):
        try:
            conversation = CDSConversation.objects.get(id=conversation_id)
        except CDSConversation.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Không tìm thấy phiên chat AI.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_text = serializer.validated_data['content']

        # 1. Save doctor message
        doctor_msg = CDSMessage.objects.create(
            conversation=conversation,
            role='doctor',
            content=user_text
        )

        # Always refresh patient_context_snapshot to capture real-time vitals, allergies, conditions
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if conversation.patient_id:
            try:
                latest_context = AICDSService.fetch_patient_context(conversation.patient_id, auth_header)
                if latest_context:
                    conversation.patient_context_snapshot = latest_context
                    conversation.save(update_fields=['patient_context_snapshot'])
            except Exception as ctx_err:
                pass

        # 2. History for context
        history = CDSMessage.objects.filter(conversation=conversation).order_by('created_at')

        # 3. Call AI Inference Service (Gemini API or Fallback)
        ai_res = AICDSService.generate_ai_response(conversation, user_text, history)
        ai_text = ai_res.get('text', '')
        recs_data = ai_res.get('recommendations', [])

        # 4. Save AI assistant message
        ai_msg = CDSMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=ai_text
        )

        # 5. Save structured recommendations
        created_recs = []
        for rec in recs_data:
            rec_obj = CDSRecommendation.objects.create(
                conversation=conversation,
                message=ai_msg,
                category=rec.get('category', 'GENERAL_ADVICE'),
                severity=rec.get('severity', 'MEDIUM'),
                summary=rec.get('summary', 'Khuyên dùng từ AI'),
                explanation=rec.get('explanation', ''),
                confidence=rec.get('confidence', 0.85)
            )
            created_recs.append(rec_obj)

        conversation.updated_at = timezone.now()
        conversation.save()

        return Response({
            'message': CDSMessageSerializer(ai_msg).data,
            'recommendations': CDSRecommendationSerializer(created_recs, many=True).data
        }, status=status.HTTP_201_CREATED)


class CDSRecommendationActionView(APIView):
    """PATCH /api/v1/cds/recommendations/{id} - Bác sĩ Accept/Ignore/Edit recommendation"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def patch(self, request, recommendation_id):
        try:
            rec = CDSRecommendation.objects.get(id=recommendation_id)
        except CDSRecommendation.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Không tìm thấy khuyến nghị.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ActOnRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rec.doctor_action = serializer.validated_data['action']
        rec.doctor_note = serializer.validated_data.get('doctor_note', '')
        rec.acted_at = timezone.now()
        rec.save()

        # Sync back to consultation-service if needed
        return Response(CDSRecommendationSerializer(rec).data)


class DrugInteractionCheckView(APIView):
    """POST /api/v1/cds/drug-interactions - Fast check tương tác thuốc từ local Knowledge Base"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        serializer = DrugCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        drug_names = serializer.validated_data['drug_names']
        patient_allergies = serializer.validated_data.get('patient_allergies', [])

        alerts = []

        # Find drugs in local DB
        db_drugs = []
        for name in drug_names:
            matched = Drug.objects.filter(name__icontains=name).first()
            if matched:
                db_drugs.append(matched)

        # Check interactions between pairs
        for i in range(len(db_drugs)):
            for j in range(i + 1, len(db_drugs)):
                d1, d2 = db_drugs[i], db_drugs[j]
                inter = DrugInteraction.objects.filter(
                    drug_a=d1, drug_b=d2
                ).first() or DrugInteraction.objects.filter(
                    drug_a=d2, drug_b=d1
                ).first()

                if inter:
                    alerts.append({
                        'category': 'DRUG_INTERACTION',
                        'severity': inter.severity,
                        'drug_a': d1.name,
                        'drug_b': d2.name,
                        'summary': f"Tương tác {inter.get_severity_display()}: {d1.name} + {d2.name}",
                        'clinical_effect': inter.clinical_effect,
                        'recommendation': inter.recommendation
                    })

        # Check allergy cross refs
        for drug in db_drugs:
            for allergy in patient_allergies:
                if allergy.lower() in drug.name.lower() or drug.name.lower() in allergy.lower():
                    alerts.append({
                        'category': 'ALLERGY_ALERT',
                        'severity': 'CRITICAL',
                        'drug': drug.name,
                        'summary': f"Cảnh báo trùng dị ứng: {drug.name}",
                        'clinical_effect': f"Bệnh nhân bị dị ứng với {allergy}.",
                        'recommendation': "Ngừng sử dụng thuốc này ngay lập tức!"
                    })

        return Response({
            'checked_drugs': [d.name for d in db_drugs],
            'alerts_count': len(alerts),
            'alerts': alerts
        })


class KnowledgeBaseView(APIView):
    """GET /api/v1/cds/knowledge - Tra cứu danh mục bệnh, triệu chứng, thuốc"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target = request.GET.get('type', 'all')
        res = {}
        if target in ['diseases', 'all']:
            res['diseases'] = DiseaseSerializer(Disease.objects.all()[:50], many=True).data
        if target in ['symptoms', 'all']:
            res['symptoms'] = SymptomSerializer(Symptom.objects.all()[:50], many=True).data
        if target in ['drugs', 'all']:
            res['drugs'] = DrugSerializer(Drug.objects.all()[:50], many=True).data
        return Response(res)
