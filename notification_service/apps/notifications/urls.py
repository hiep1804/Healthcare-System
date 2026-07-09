from django.urls import path
from .views import (
    TemplateListCreateView, TemplateDetailView, SendNotificationView, JobDetailView, JobRetryView
)

urlpatterns = [
    path('notifications/send', SendNotificationView.as_view(), name='notification-send'),
    path('notification-templates', TemplateListCreateView.as_view(), name='template-list-create'),
    path('notification-templates/<uuid:template_id>', TemplateDetailView.as_view(), name='template-detail'),
    path('notification-jobs/<uuid:job_id>', JobDetailView.as_view(), name='job-detail'),
    path('notification-jobs/<uuid:job_id>/retry', JobRetryView.as_view(), name='job-retry'),
]
