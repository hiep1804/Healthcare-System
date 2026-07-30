from django.urls import path
from .views import (
    CDSConversationListCreateView, CDSConversationDetailView,
    CDSSendMessageView, CDSRecommendationActionView,
    DrugInteractionCheckView, KnowledgeBaseView
)

urlpatterns = [
    path('cds/conversations', CDSConversationListCreateView.as_view(), name='cds-conversations-list-create'),
    path('cds/conversations/<uuid:conversation_id>', CDSConversationDetailView.as_view(), name='cds-conversation-detail'),
    path('cds/conversations/<uuid:conversation_id>/messages', CDSSendMessageView.as_view(), name='cds-send-message'),
    path('cds/recommendations/<uuid:recommendation_id>', CDSRecommendationActionView.as_view(), name='cds-recommendation-action'),
    path('cds/drug-interactions', DrugInteractionCheckView.as_view(), name='cds-drug-interactions'),
    path('cds/knowledge', KnowledgeBaseView.as_view(), name='cds-knowledge'),
]
