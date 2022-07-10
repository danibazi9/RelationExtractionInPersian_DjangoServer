from django.urls import path

from app.api.views import seraji_output_view, perdt_output_view

app_name = 'app'

urlpatterns = [
    path('seraji', seraji_output_view, name='seraji-output'),
    path('perdt', perdt_output_view, name='perdt-output'),
]
