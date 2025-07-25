"""
URL configuration for movieproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="MovieApp API",
      default_version='v1',
      description="API documentation for the MovieApp project, which manages movie metadata, user interactions, and comments using XML.",
      terms_of_service="https://www.google.com/policies/terms/", # Örnek
      contact=openapi.Contact(email="contact@movieapp.local"), # Örnek
      license=openapi.License(name="BSD License"), # Örnek
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    # 1. Path for the Django Admin interface
    path('admin/', admin.site.urls),

    # 2. Path for all Version 1 API endpoints
    # All requests starting with /api/v1/ will be handled by the 'api.urls' file.
    path('api/v1/', include('api.urls')),

   # 3. Paths for the interactive API documentation (Swagger and ReDoc)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API şemasını JSON veya YAML olarak indirmek için
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]
