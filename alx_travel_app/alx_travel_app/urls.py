from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from listings.views import (
    ListingViewSet, BookingViewSet, 
    ReviewViewSet, PaymentViewSet, 
    UserViewSet, StatsAPIView
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payments', PaymentViewSet, basename='payment')

# Swagger/OpenAPI configuration
schema_view = get_schema_view(
    openapi.Info(
        title="ALX Travel App API",
        default_version='v1',
        description="""
        Comprehensive API for ALX Travel Application.
        
        This API allows users to:
        - Browse and search travel listings
        - Make bookings
        - Submit reviews
        - Process payments
        
        ## Authentication
        The API uses token-based authentication. 
        Obtain your token by logging in at `/api/auth/login/`
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@alxtravel.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stats/', StatsAPIView.as_view(), name='stats'),
    
    # Authentication (if using DRF's token auth or Djoser)
    path('api/auth/', include('rest_framework.urls')),
    
    # Swagger/OpenAPI URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Make Swagger the home page (optional)
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='home'),
]
