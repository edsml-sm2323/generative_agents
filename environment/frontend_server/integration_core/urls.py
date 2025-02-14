from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from integration_core.views import ExperimentListView  # 引入 ExperimentListView 视图集

# 配置 Swagger Schema
schema_view = get_schema_view(
   openapi.Info(
      title="epitome平台集成斯坦福小镇 API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@myapi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [    
    path('swagger/', schema_view.as_view()),  # Swagger 文档的路由
    path('experiments/', ExperimentListView.as_view(),  name='experiment-list'),
]