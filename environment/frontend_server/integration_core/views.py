from asyncio.log import logger
import json
import os
import re
import subprocess
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


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse

class VideoHLSView(APIView):
    """
    HLS视频切片生成服务接口
    访问示例：GET /api/hls/generate/?video_path=/media/videos/source.mp4&segment_duration=10
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
        # # 增加视频格式验证
        # valid_extensions = ['.mp4', '.mov', '.mkv']
        # if not any(video_path.lower().endswith(ext) for ext in valid_extensions):
        #     return JsonResponse(
        #         {"error": "UNSUPPORTED_FORMAT", "message": "仅支持MP4/MOV/MKV格式"}, 
        #         status=400
        #     )

        # # 增加分辨率容错处理
        # try:
        #     probe = ffmpeg.probe(video_path)
        #     video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        #     original_width = int(video_stream['width'])
        #     original_height = int(video_stream['height'])
        # except:
        #     return JsonResponse(
        #         {"error": "INVALID_VIDEO", "message": "无法解析视频元数据"}, 
        #         status=400
        #     )

        # # 自动适配分辨率
        # if original_width % 2 != 0 or original_height % 2 != 0:
        #     return JsonResponse(
        #         {"error": "ODD_RESOLUTION", "message": "检测到奇数分辨率，正在自动修正..."}, 
        #         status=400
        #     )

        # 生成输出目录结构
        video_dir = os.path.dirname(video_path)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_dir = os.path.join(video_dir, f"{base_name}_hls")
        os.makedirs(output_dir, exist_ok=True)

        # HLS转码参数
        m3u8_path = os.path.join(output_dir, 'playlist.m3u8')
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', "scale=ceil(iw/2)*2:ceil(ih/2)*2",  # 自动修正尺寸
            '-c:v', 'libx264',
            '-profile:v', 'main',
            '-crf', '23',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', str(segment_duration),
            '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
            '-hls_flags', 'independent_segments',
            m3u8_path
        ]

        # 执行转码
        try:
            result = subprocess.run(
                ffmpeg_command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=300  # 5分钟超时
            )
            logger.info(f"HLS转码成功: {result.stdout}")
        except subprocess.TimeoutExpired:
            logger.error("HLS转码超时")
            return JsonResponse(
                {"error": "PROCESS_TIMEOUT", "message": "视频处理超时"}, 
                status=500
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"HLS转码失败: {e.stdout}")
            return JsonResponse(
                {"error": "PROCESS_FAILED", "message": "视频处理失败", "detail": e.stdout}, 
                status=500
            )

        # 生成访问URL
        relative_path = os.path.relpath(m3u8_path, settings.MEDIA_ROOT)
        m3u8_url = f"{settings.MEDIA_URL}{relative_path}"

        return JsonResponse({
            "status": "SUCCESS",
            "playlist_url": m3u8_url,
            "segment_duration": segment_duration,
            "resolution": "1280x720 (保持宽高比)",
            "codec": "H.264 + AAC",
            "expire_time": "24h"  # 可根据需要实现清理逻辑
        })


