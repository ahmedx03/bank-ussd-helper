from django.urls import path
from . import views

urlpatterns = [
    path('a2a/agent/ussd-helper', views.ussd_agent, name='ussd_agent'),
    path('a2a/health', views.a2a_health, name='a2a_health'),
]