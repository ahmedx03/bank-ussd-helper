from django.urls import path
from . import views

urlpatterns = [
    path('a2a/agent/ussd-helper', views.ussd_agent, name='ussd_agent'),
    path('health', views.health_check, name='health_check'),
    path('test-simple', views.test_simple, name='test_simple'),
    path('test-ai-direct', views.test_ai_direct, name='test_ai_direct'),
]