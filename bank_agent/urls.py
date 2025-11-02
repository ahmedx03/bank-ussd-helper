from django.urls import path
from . import views

urlpatterns = [
    path('a2a/agent/ussd-helper', views.ussd_agent, name='ussd_agent'),
    path('health', views.health_check, name='health_check'),
    path('test', views.simple_test, name='simple_test'),
]