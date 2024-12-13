from django.urls import path
from . import views

urlpatterns = [
    # path('metrics/', views.get_metrics, name='get_metrics'),
    # path('htop-screenshot/', views.get_htop_screenshot, name='get_htop_screenshot'),
    path('dashboard/', views.performance_dashboard, name='performance_dashboard'),
]