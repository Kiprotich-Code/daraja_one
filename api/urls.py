from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('daraja/c2b/', views.daraja_c2b_callback, name='c2b_callback'),
    path('daraja/validation/', views.daraja_validation_endpoint, name='validation'),
]
