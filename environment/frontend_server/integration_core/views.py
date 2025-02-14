import os 
from django.core.cache  import cache 
from rest_framework.views  import APIView 
from rest_framework.response  import Response 
from rest_framework import status 
from rest_framework.permissions  import AllowAny 
from drf_yasg.utils  import swagger_auto_schema 
from drf_yasg import openapi 
from django.conf  import settings 
 
EXPERIMENT_STORAGE_ROOT = settings.EXPERIMENT_STORAGE_ROOT 
PUBLIC_EXPERIMENT_WHITELIST = settings.PUBLIC_EXPERIMENT_WHITELIST 
 
CACHE_KEY = 'experiment_list'
CACHE_TIMEOUT = 60 * 5  # 优化缓存时间为5分钟 
 
class ExperimentListView(APIView):
    """
    实验列表视图（支持公共和个性化实验查询）
    """
    permission_classes = [AllowAny]
 
    def _get_experiments(self):
        """ 获取实验列表（带缓存机制） """
        experiments = cache.get(CACHE_KEY) 
        if not experiments:
            try:
                experiments = os.listdir(EXPERIMENT_STORAGE_ROOT) 
                cache.set(CACHE_KEY,  experiments, CACHE_TIMEOUT)
            except FileNotFoundError as e:
                raise ValueError(f"实验存储目录不存在: {EXPERIMENT_STORAGE_ROOT}") from e 
            except PermissionError as e:
                raise RuntimeError(f"目录访问权限不足: {EXPERIMENT_STORAGE_ROOT}") from e 
        return experiments 
 
    @swagger_auto_schema(
        operation_description="获取公共实验列表（白名单内实验）",
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="实验类型过滤（public/personalized）",
                type=openapi.TYPE_STRING,
                enum=['public', 'personalized'],
                default='public'
            )
        ],
        responses={
            200: openapi.Response(
                description="实验列表",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="错误信息",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """ 统一入口处理GET请求 """
        try:
            experiments = self._get_experiments()
            exp_type = request.query_params.get('type',  'public').lower()
 
            if exp_type == 'public':
                data = [exp for exp in experiments if exp in PUBLIC_EXPERIMENT_WHITELIST]
            elif exp_type == 'personalized':
                data = [exp for exp in experiments if exp not in PUBLIC_EXPERIMENT_WHITELIST]
            else:
                return Response(
                    {"error": "无效的实验类型参数，可选值: public/personalized"},
                    status=status.HTTP_400_BAD_REQUEST 
                )
 
            return Response({
                "count": len(data),
                "results": sorted(data)
            }, status=status.HTTP_200_OK)
 
        except Exception as e:
            error_type = type(e).__name__
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR if not isinstance(e, ValueError) else status.HTTP_400_BAD_REQUEST 
            return Response({
                "error": f"{error_type}: {str(e)}",
                "detail": f"请检查存储路径配置: {EXPERIMENT_STORAGE_ROOT}"
            }, status=status_code)