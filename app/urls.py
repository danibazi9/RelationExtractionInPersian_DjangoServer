from django.urls import path, include

from app import views

urlpatterns = [
    path('', views.result, name='service'),
    path('api/', include('app.api.urls')),
]
