from django.urls import path
from .views import (
    PlanListCreateView, PlanDetailView, SubscriptionListCreateView, SubscriptionCancelView, SubscriptionUsageView
)

urlpatterns = [
    path('plans', PlanListCreateView.as_view(), name='plan-list-create'),
    path('plans/<uuid:plan_id>', PlanDetailView.as_view(), name='plan-detail'),
    path('subscriptions', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/me', SubscriptionListCreateView.as_view(), name='subscription-me'),  # maps to get in SubscriptionListCreateView
    path('subscriptions/<uuid:subscription_id>/cancel', SubscriptionCancelView.as_view(), name='subscription-cancel'),
    path('subscriptions/<uuid:subscription_id>/usage', SubscriptionUsageView.as_view(), name='subscription-usage'),
]
