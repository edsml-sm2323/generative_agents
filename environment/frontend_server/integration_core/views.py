import json
import os
import re
from django.core.cache  import cache
from rest_framework.views  import APIView
from rest_framework.response  import Response
from rest_framework import status
from rest_framework.permissions  import AllowAny
from drf_yasg.utils  import swagger_auto_schema
from drf_yasg import openapi
from django.conf  import settings

from global_methods import *

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
        

# ========================
# 新增 Phaser 游戏接口模块 
# ========================
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import re
from django.conf import settings

class PhaserGameEmbedView(APIView):
    """
    Phaser3 游戏嵌入接口 
    支持动态配置游戏参数，允许通过 iframe 嵌入 
    """
    permission_classes = [AllowAny]

    # Swagger 文档配置 
    @swagger_auto_schema(
        operation_description="获取 Phaser3 游戏嵌入接口",
        manual_parameters=[
            openapi.Parameter(
                'sim_code',
                openapi.IN_QUERY,
                description="仿真代码，用于加载特定仿真环境",
                type=openapi.TYPE_STRING,
                default=''
            ),
            openapi.Parameter(
                'step',
                openapi.IN_QUERY,
                description="仿真步数，用于选择不同阶段",
                type=openapi.TYPE_INTEGER,
                default=0
            )
        ],
        responses={
            200: openapi.Response(
                description="游戏界面HTML",
                content={'text/html': {}}
            ),
            400: openapi.Response(
                description="参数验证失败",
                examples={"application/json": {"error": "Invalid width value"}}
            )
        }
    )
    @method_decorator(xframe_options_exempt)
    def get(self, request):
        """
        核心逻辑：
        1. 参数验证与处理 
        2. 安全头设置 
        3. 动态模板渲染 
        """
        # 参数验证
        params = self._validate_params(request)
        if isinstance(params, Response):
            return params

        sim_code = params['sim_code']
        step = int(params['step'])
        persona_names = []
        persona_names_set = set()
        for i in find_filenames(f"storage/{sim_code}/personas", ""): 
          x = i.split("/")[-1].strip()
          if x[0] != ".": 
            persona_names += [[x, x.replace(" ", "_")]]
            persona_names_set.add(x)

        persona_init_pos = []
        file_count = []
        for i in find_filenames(f"storage/{sim_code}/environment", ".json"):
          x = i.split("/")[-1].strip()
          if x[0] != ".": 
            file_count += [int(x.split(".")[0])]
        curr_json = f'storage/{sim_code}/environment/{str(max(file_count))}.json'
        with open(curr_json) as json_file:  
          persona_init_pos_dict = json.load(json_file)
          for key, val in persona_init_pos_dict.items(): 
            if key in persona_names_set: 
              persona_init_pos += [[key, val["x"], val["y"]]]

        context = {"sim_code": sim_code,
                   "step": step,
                   "persona_names": persona_names,
                   "persona_init_pos": persona_init_pos, 
                   "mode": "replay"}
        template = "home/home.html"
        response = render(request, template, context)
        response['X-Frame-Options'] = 'ALLOWALL'  # 允许 iframe 嵌入
        response['Content-Security-Policy'] = "frame-ancestors 'self' *"  # 更细粒度的 CSP 头
        return response

    def _validate_params(self, request):
        """增强型参数验证"""
        validator = {
            'sim_code': lambda x: isinstance(x, str) and len(x) > 0,
            'step': lambda x: x.isdigit() and int(x) >= 0  # 修改 step 的验证规则
        }

        errors = {}
        params = {
            'sim_code': request.GET.get('sim_code', ''),
            'step': request.GET.get('step', 0)
        }

        for field, check in validator.items():
            try:
                if not check(params[field]):
                    errors[field] = f"Invalid {field} value"
            except (ValueError, TypeError):
                errors[field] = f"Invalid {field} format"

        if errors:
            return Response(
                {"error": "参数校验失败", "details": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        return params


import os
import subprocess
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

class VideoHLSView(APIView):
    """
    获取视频切片并通过 HLS 协议播放接口
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="获取视频切片并通过 HLS 协议播放",
        manual_parameters=[
            openapi.Parameter(
                'video_path',
                openapi.IN_QUERY,
                description="视频文件路径，用于切割和生成 HLS 流",
                type=openapi.TYPE_STRING,
                default='path/to/video.mp4'
            ),
            openapi.Parameter(
                'segment_duration',
                openapi.IN_QUERY,
                description="每个视频切片的时长，单位秒（默认10秒）",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ],
        responses={
            200: openapi.Response(
                description="HLS 播放器嵌入信息",
                content={'text/html': {}}
            ),
            400: openapi.Response(
                description="参数验证失败",
                examples={"application/json": {"error": "Invalid video path"}}
            )
        }
    )
    def get(self, request):
        """
        核心逻辑：
        1. 参数验证与处理 
        2. 使用 FFmpeg 将视频切割成 .ts 文件并生成 .m3u8 播放列表
        3. 动态模板渲染，生成可以嵌入 iframe 的 HLS 播放器
        """
        # 参数验证
        video_path = request.GET.get('video_path')
        segment_duration = int(request.GET.get('segment_duration', 10))

        if not video_path or not os.path.exists(video_path):
            return JsonResponse({"error": "Invalid video path"}, status=400)

        # 生成视频切片并创建 HLS 播放列表
        base_path = os.path.dirname(video_path)
        video_name = os.path.basename(video_path).split('.')[0]
        hls_output_dir = os.path.join(base_path, f"{video_name}_hls")
        if not os.path.exists(hls_output_dir):
            os.makedirs(hls_output_dir)

        m3u8_file = os.path.join(hls_output_dir, f"{video_name}.m3u8")

        # 使用 ffmpeg 将视频切割成 .ts 文件，并生成 .m3u8 播放列表
        ffmpeg_command = [
            'ffmpeg', 
            '-i', video_path, 
            '-c:v', 'libx264', 
            '-c:a', 'aac', 
            '-strict', 'experimental', 
            '-f', 'segment', 
            '-segment_list', m3u8_file, 
            '-segment_time', str(segment_duration), 
            '-segment_format', 'mpegts', 
            os.path.join(hls_output_dir, f'{video_name}_%03d.ts')
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": "Video processing failed", "details": str(e)}, status=500)

        # 构建上下文并渲染模板
        context = {
            'hls_playlist_url': f"{settings.MEDIA_URL}{hls_output_dir}/{video_name}.m3u8",
            'hls_files': self.get_hls_files(hls_output_dir)
        }

        # 返回 HLS 播放器 HTML 嵌入
        response = render(request, 'hls_player.html', context)
        return response

    def get_hls_files(self, hls_dir):
        """返回所有切割的视频文件"""
        ts_files = [f for f in os.listdir(hls_dir) if f.endswith('.ts')]
        ts_files.sort()  # 按文件名排序
        return ts_files

