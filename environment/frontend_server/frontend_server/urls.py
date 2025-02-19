"""frontend_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
"""
frontend_server URL Configuration 
 
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/ 
"""
from django.urls  import include, path, re_path 
from django.contrib  import admin 
from django.conf  import settings 
from django.conf.urls.static  import static 
from translator import views as translator_views 

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
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
    # 使用re_path保持正则表达式匹配 
    re_path(r'^$', translator_views.landing,  name='landing'),
    re_path(r'^simulator_home$', translator_views.home,  name='home'),
    
    # 带参数的路由保持原始正则表达式 
    re_path(
        r'^demo/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<play_speed>[\w-]+)/$',
        translator_views.demo, 
        name='demo'
    ),
    re_path(
        r'^replay/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/$',
        translator_views.replay, 
        name='replay'
    ),
    re_path(
        r'^replay_persona_state/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<persona_name>[\w-]+)/$',
        translator_views.replay_persona_state, 
        name='replay_persona_state'
    ), 
 
    # API端点改用path+转换器（可选改进）
    path('process_environment/', translator_views.process_environment,  name='process_environment'),
    path('update_environment/', translator_views.update_environment,  name='update_environment'),
    path('path_tester/', translator_views.path_tester,  name='path_tester'),
    path('path_tester_update/', translator_views.path_tester_update,  name='path_tester_update'), 
 
    # 管理后台路径保持不变 
    path('admin/', admin.site.urls), 
    
    # 第三方集成路径 
    path('epitome/', include('integration_core.urls')), 
    path('swagger/', schema_view.with_ui('swagger',  cache_timeout=60), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',  cache_timeout=60), name='redoc-ui'),
    # 提供swagger.json下载接口
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='swagger-json'),
]
 
# 开发环境静态文件服务配置 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)