from django.urls import path
from . import views

urlpatterns = [
    path('', views.subreport_view, name='subreport'),
    path('report/', views.subreport_view, name='subreport_main'),
]