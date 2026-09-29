# config/urls.py
from django.contrib import admin
from django.urls import path, re_path
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api.views import CustomTokenObtainPairView
from core.views import (
    home_view, evento_detail_view, registro_view, login_view, logout_view,
    carro_view, checkout_view, mis_entradas_view, organizador_dashboard_view
)

def custom_404_view(request, exception=None):
    """Controlador personalizado para error 404."""
    return render(request, '404.html', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas Web (Templates)
    path('', home_view, name='home'),
    path('evento/<int:evento_id>/', evento_detail_view, name='evento_detail'),
    path('registro/', registro_view, name='registro'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('carro/', carro_view, name='carro'),
    path('checkout/', checkout_view, name='checkout'),
    path('mis-entradas/', mis_entradas_view, name='mis_entradas'),
    path('organizador/dashboard/', organizador_dashboard_view, name='organizador_dashboard'),

    # Endpoints API & JWT
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Captura de errores 404 obligatoria mediante repath
urlpatterns += [
    re_path(r'^.*$', custom_404_view),
]