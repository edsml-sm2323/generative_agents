from asyncio.log import logger
import json
import logging
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
BASE_DIR = settings.BASE_DIR

CACHE_KEY = 'experiment_list'
CACHE_TIMEOUT = 60 * 5  # 优化缓存时间为5分钟

class ExperimentListView(APIView):
    """
    实验列表视图（支持公共和个性化实验查询）{废弃接口}
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
        operation_description="获取公共实验列表（白名单内实验）（支持公共和个性化实验查询）{废弃接口}",
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
                description="仿真代码位置，用于加载特定仿真环境",
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


class VideoHLSView(APIView):
    """
    HLS视频切片生成服务接口{废弃接口}
    访问示例：GET /api/hls/generate/?video_path=/media/videos/source.mp4&segment_duration=10
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="获取视频切片并通过 HLS 协议播放{废弃接口}",
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


class ExperimentCreateView(APIView):
    """
    创建或修改实验
    包括设置人物、描述、行为、地图等
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "创建/修改实验（目前可修改实验名称和人物背景）。\n"
            "此接口允许用户创建新的实验背景，包括实验代人物设置。\n"
            "请确保提供所有必需的字段，以便系统能够正确处理请求。\n"
            "###附加注解：每次实验需要提供如下的目录结构，并且json文件中的字段也有一部分个性化的(作为模板文件)，\n"
            "目前项目结构提供的接口只能修改人物背景(地图的话:可能的方案是，准备几套所需要的UI（目前默认the_ville），修改项目源代码提供给用户选择功能）\n"
            "```\n"
            ".\n"
            "├── environment\n"
            "│   └── 0.json  # 当前仿真环境的状态信息\n"
            "├── personas\n"
            "│   ├── Isabella Rodriguez\n"
            "│   │   └── bootstrap_memory\n"
            "│   │       ├── associative_memory\n"
            "│   │       │   ├── embeddings.json  # 角色的嵌入向量\n"
            "│   │       │   ├── kw_strength.json  # 关键词强度数据\n"
            "│   │       │   └── nodes.json  # 记忆中的节点信息\n"
            "│   │       ├── scratch.json  # 角色的临时记忆\n"
            "│   │       └── spatial_memory.json  # 角色的空间记忆\n"
            "│   ├── Klaus Mueller\n"
            "│   │   └── bootstrap_memory\n"
            "│   │       ├── associative_memory\n"
            "│   │       │   ├── embeddings.json  # 角色的嵌入向量\n"
            "│   │       │   ├── kw_strength.json  # 关键词强度数据\n"
            "│   │       │   └── nodes.json  # 记忆中的节点信息\n"
            "│   │       ├── scratch.json  # 角色的临时记忆\n"
            "│   │       └── spatial_memory.json  # 角色的空间记忆\n"
            "│   └── Maria Lopez\n"
            "│       └── bootstrap_memory\n"
            "│           ├── associative_memory\n"
            "│           │   ├── embeddings.json  # 角色的嵌入向量\n"
            "│           │   ├── kw_strength.json  # 关键词强度数据\n"
            "│           │   └── nodes.json  # 记忆中的节点信息\n"
            "│           ├── scratch.json  # 角色的临时记忆\n"
            "│           └── spatial_memory.json  # 角色的空间记忆\n"
            "└── reverie\n"
            "    └── meta.json  # 仿真元数据\n"
            "```\n"

            "请求体应包含实验名称代码和一个人物数组，每个人物应包含以下详细信息："
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'sim_code': openapi.Schema(type=openapi.TYPE_STRING, description="实验代码"),
                'characters': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description="人物名称"),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="人物的名字"),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="人物的姓氏"),
                            'age': openapi.Schema(type=openapi.TYPE_INTEGER, description="人物的年龄"),
                            'daily_plan_req': openapi.Schema(type=openapi.TYPE_STRING, description="人物的日常计划"),
                            'innate': openapi.Schema(type=openapi.TYPE_STRING, description="人物的天性"),
                            'learned': openapi.Schema(type=openapi.TYPE_STRING, description="人物的学习经验"),
                            'currently': openapi.Schema(type=openapi.TYPE_STRING, description="人物当前的状态"),
                            'lifestyle': openapi.Schema(type=openapi.TYPE_STRING, description="人物的生活方式"),
                            'living_area': openapi.Schema(type=openapi.TYPE_STRING, description="人物的居住区域"),
                            'coordinates_x':openapi.Schema(type=openapi.TYPE_INTEGER, description="人物初始x坐标(50-200吧(目前ui中的i位置对应未知))"),
                            'coordinates_y':openapi.Schema(type=openapi.TYPE_INTEGER, description="人物初始y坐标(50-200吧(目前ui中的i位置对应未知))"),
                        }
                    ),
                    description="人物设置，包括每个人物的详细信息"
                ),
            },
        ),
        responses={
            200: openapi.Response(description="实验创建或修改成功"),
            400: openapi.Response(description="参数验证失败，确保所有必需字段均已提供"),
        }
    )
    def post(self, request):
        """
        创建或修改实验
        """
        # 获取参数
        sim_code = request.data.get('sim_code')
        characters = request.data.get('characters')

        if not sim_code:
            return Response({"error": "sim_code are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 创建实验目录
        experiment_dir = os.path.join(EXPERIMENT_STORAGE_ROOT, sim_code)
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)

        # 创建环境目录
        environment_dir = os.path.join(experiment_dir, 'environment')
        if not os.path.exists(persona_dir):
            os.makedirs(persona_dir)
        # 创建初始位置
        experiment_coordinates_path = os.path.join(environment_dir, '0.json')
        coordinates_data = {
            character.get('name'): {
                "maze": "the_ville",
                "x": character.get('coordinates_x', random.randint(50, 200)),
                "y": character.get('coordinates_y', random.randint(50, 200)),
            }
            for character in characters if character.get('name')  # 过滤掉没有名字的角色
        }
        # 写入数据到文件
        with open(experiment_coordinates_path, 'w') as f:
            json.dump(coordinates_data, f, indent=4)

        # 复制其他所需文件
        temp_storage_path = settings.EXPERIMENT_TEMPLATES_STORAGE_ROOT
        temp_associative_memory_path = os.path.join(temp_storage_path,'associative_memory')
        temp_reverie_path = os.path.join(temp_storage_path, 'reverie')
        copyanything(temp_reverie_path,os.path.join(experiment_dir, 'reverie'))

        # 为每个角色创建文件夹和修改 scratch.json
        for character in characters:
            character_name = character.get('name')
            if not character_name:
                continue  # 如果角色名字不存在，跳过这个角色

            # 为每个角色创建目录
            persona_dir = os.path.join(experiment_dir, 'personas', character_name)
            if not os.path.exists(persona_dir):
                os.makedirs(persona_dir)

            # 创建 bootstrap_memory 目录
            bootstrap_memory_dir = os.path.join(persona_dir, 'bootstrap_memory')
            if not os.path.exists(bootstrap_memory_dir):
                os.makedirs(bootstrap_memory_dir)

            # 复制/创建 scratch.json
            scratch_file_path = os.path.join(bootstrap_memory_dir, 'scratch.json')
            scratch_data = {
                "vision_r": 8,
                "att_bandwidth": 8,
                "retention": 8,
                "curr_time": None,
                "curr_tile": None,
                "daily_plan_req": character.get('daily_plan_req', ""),
                "name": character_name,
                "first_name": character.get('first_name', ""),
                "last_name": character.get('last_name', ""),
                "age": character.get('age', 0),
                "innate": character.get('innate', ""),
                "learned": character.get('learned', ""),
                "currently": character.get('currently', ""),
                "lifestyle": character.get('lifestyle', ""),
                "living_area": character.get('living_area', ""),
                "concept_forget": 100,
                "daily_reflection_time": 180,
                "daily_reflection_size": 5,
                "overlap_reflect_th": 4,
                "kw_strg_event_reflect_th": 10,
                "kw_strg_thought_reflect_th": 9,
                "recency_w": 1,
                "relevance_w": 1,
                "importance_w": 1,
                "recency_decay": 0.995,
                "importance_trigger_max": 150,
                "importance_trigger_curr": 150,
                "importance_ele_n": 0,
                "thought_count": 5,
                "daily_req": [],
                "f_daily_schedule": [],
                "f_daily_schedule_hourly_org": [],
                "act_address": None,
                "act_start_time": None,
                "act_duration": None,
                "act_description": None,
                "act_pronunciatio": None,
                "act_event": [character_name, None, None],
                "act_obj_description": None,
                "act_obj_pronunciatio": None,
                "act_obj_event": [None, None, None],
                "chatting_with": None,
                "chat": None,
                "chatting_with_buffer": {},
                "chatting_end_time": None,
                "act_path_set": False,
                "planned_path": []
            }

            with open(scratch_file_path, 'w') as f:
                json.dump(scratch_data, f)

            # 为每个角色创建空间记忆文件：（以下仅做为模板），尚不全面
            locations = {
                "the Ville": {
                    "Oak Hill College": {
                        "hallway": [],
                        "library": [
                            "library sofa",
                            "library table",
                            "bookshelf"
                        ],
                        "classroom": [
                            "blackboard",
                            "classroom podium",
                            "classroom student seating"
                        ]
                    },
                    "Dorm for Oak Hill College": {
                        "garden": [
                            "dorm garden"
                        ],
                        "woman's bathroom": [
                            "toilet",
                            "shower",
                            "bathroom sink"
                        ],
                        "common room": [
                            "common room sofa",
                            "pool table",
                            "common room table"
                        ],
                        "man's bathroom": [
                            "shower",
                            "bathroom sink",
                            "toilet"
                        ]
                    },
                    "The Willows Market and Pharmacy": {
                        "store": [
                            "grocery store shelf",
                            "behind the grocery counter",
                            "grocery store counter",
                            "pharmacy store shelf",
                            "pharmacy store counter",
                            "behind the pharmacy counter"
                        ]
                    },
                    "Harvey Oak Supply Store": {
                        "supply store": [
                            "supply store product shelf",
                            "behind the supply store counter",
                            "supply store counter"
                        ]
                    },
                    "Johnson Park": {
                        "park": [
                            "park garden"
                        ]
                    },
                    "The Rose and Crown Pub": {
                        "pub": [
                            "shelf",
                            "refrigerator",
                            "bar customer seating",
                            "behind the bar counter",
                            "kitchen sink",
                            "cooking area",
                            "microphone"
                        ]
                    },
                    "Hobbs Cafe": {
                        "cafe": [
                            "refrigerator",
                            "cafe customer seating",
                            "cooking area",
                            "kitchen sink",
                            "behind the cafe counter",
                            "piano"
                        ]
                    }
                }
            }
            # 根据角色兴趣选择场所
            spatial_memory_data = {}
            for location, areas in locations['the Ville'].items():
                character_items = {}
                for area, items in areas.items():
                    # 随机选择一些物品，或者根据个性来决定，目前随机
                    num_items = random.randint(1, 3)  # 选择1到3个物品
                    chosen_items = random.sample(items, num_items)
                    character_items[area] = chosen_items
                spatial_memory_data[location] = character_items
            spatial_memory_path = os.path.join(bootstrap_memory_dir,'spatial_memory.json')
            with open(spatial_memory_path, 'w') as f:
                json.dump(spatial_memory_data, f)
            copyanything(temp_associative_memory_path,os.path.join(bootstrap_memory_dir,'associative_memory'))
        # 执行 实验
        try:
            rs = ReverieServer("No Fork",sim_code,isCreate= True)
            rs.open_server()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing experiment: {e}")
            return Response({"error": f"Error executing experiment: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Experiment created successfully."}, status=status.HTTP_200_OK)

class ExperimentStartView(APIView):
    """
    启动实验并执行外部 Bash 脚本(通过原项目中的自动化脚本启动，暂时无法监控)
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="启动实验并执行外部脚本(通过原项目中的自动化脚本启动，暂时无法监控)",
        manual_parameters=[
            openapi.Parameter('sim_code', openapi.IN_QUERY, description="实验代码", type=openapi.TYPE_STRING),
            openapi.Parameter('target', openapi.IN_QUERY, description="目标实验", type=openapi.TYPE_STRING),
            openapi.Parameter('steps', openapi.IN_QUERY, description="实验步骤数", type=openapi.TYPE_INTEGER),
            openapi.Parameter('ui', openapi.IN_QUERY, description="是否启用UI", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('port', openapi.IN_QUERY, description="端口号", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="实验启动成功"),
            400: openapi.Response(description="参数验证失败"),
        }
    )
    def post(self, request):
        """
        启动实验并执行 Bash 脚本
        """
        # 获取参数
        sim_code = request.GET.get('sim_code')
        target = request.GET.get('target')
        steps = request.GET.get('steps')
        ui = request.GET.get('ui', False)
        port = request.GET.get('port', 8000)  # 默认端口

        if not sim_code or not target:
            return Response({"error": "sim_code and target are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 获取脚本路径，确保它在容器或环境中正确执行
        backend_script_path = os.path.join(settings.ROOT_DIR, "run_backend_automatic.sh")

        # 检查脚本文件是否存在
        if not os.path.exists(backend_script_path):
            return Response({"error": "Bash script not found."}, status=status.HTTP_404_NOT_FOUND)

        # 准备 Bash 脚本的参数
        bash_command = [
            'bash', backend_script_path,  # 使用绝对路径调用 Bash 脚本
            '--origin', sim_code, 
            '--target', target, 
            '--steps', str(steps),
            '--ui', str(ui).lower(),  # False 会被转换为 "false"
            '--port', str(port)
        ]

        # 执行 Bash 脚本
        try:
            logging.info(f"Running command: {' '.join(bash_command)}")
            subprocess.run(bash_command, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error executing bash script: {e}")
            return Response({"error": f"Error executing bash script: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Experiment started successfully."}, status=status.HTTP_200_OK)

    

class ExperimentStatusView(APIView):
    """
    查询实验状态（是否跑完流程），仅在原项目中i添加一个字段用于记录，返回 no started/ running/ finished
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="查询实验状态（是否跑完流程），仅在原项目中i添加一个字段用于记录，返回 no started/ running/ finished",
        manual_parameters=[
            openapi.Parameter('sim_code', openapi.IN_QUERY, description="实验代码", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="返回实验状态"),
            400: openapi.Response(description="参数验证失败"),
        }
    )
    def get(self, request):
        """
        查询实验状态
        """
        sim_code = request.GET.get('sim_code')
        if not sim_code:
            return Response({"error": "sim_code is required."}, status=status.HTTP_400_BAD_REQUEST)

        experiment_file_path = f'{EXPERIMENT_STORAGE_ROOT }/{sim_code}/reverie/meta.json'
        if not os.path.exists(experiment_file_path):
            return Response({"error": "Experiment not found."}, status=status.HTTP_404_NOT_FOUND)

        with open(experiment_file_path, 'r') as f:
            experiment_data = json.load(f)

        return Response({"status": experiment_data.get('running_status', 'not started')}, status=status.HTTP_200_OK)

class ExperimentDetailView(APIView):
    """
    获取实验详细数据（人物的行为、语言等）(返回jsong格式的集合，每个人物对应一个字段)
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description=(
            "获取实验详细数据（人物的行为、语言等）(返回jsong格式的集合，每个人物对应一个字段)下面是示例(其中只有部分可用)：\n"
            "```json\n"
            "{\n"
            "  \"vision_r\": 8,  # 视觉分辨率\n"
            "  \"att_bandwidth\": 8,  # 注意力带宽\n"
            "  \"retention\": 8,  # 记忆保留能力\n"
            "  \"curr_time\": null,  # 当前时间\n"
            "  \"curr_tile\": null,  # 当前所在的瓷砖\n"
            "  \"daily_plan_req\": \"Klaus Mueller goes to the library at Oak Hill College early in the morning, spends his days writing, and eats at Hobbs Cafe.\",  # 日常计划\n"
            "  \"name\": \"Klaus Mueller\",  # 人物全名\n"
            "  \"first_name\": \"Klaus\",  # 名字\n"
            "  \"last_name\": \"Mueller\",  # 姓氏\n"
            "  \"age\": 20,  # 年龄\n"
            "  \"innate\": \"kind, inquisitive, passionate\",  # 天性\n"
            "  \"learned\": \"Klaus Mueller is a student at Oak Hill College studying sociology. He is passionate about social justice and loves to explore different perspectives.\",  # 学习经验\n"
            "  \"currently\": \"Klaus Mueller is writing a research paper on the effects of gentrification in low-income communities.\",  # 当前状态\n"
            "  \"lifestyle\": \"Klaus Mueller goes to bed around 11pm, awakes up around 7am, eats dinner around 5pm.\",  # 生活方式\n"
            "  \"living_area\": \"the Ville:Dorm for Oak Hill College:Klaus Mueller's room\",  # 居住区域\n"
            "  \"concept_forget\": 100,  # 概念遗忘阈值\n"
            "  \"daily_reflection_time\": 180,  # 每日反思时间（秒）\n"
            "  \"daily_reflection_size\": 5,  # 每日反思的大小\n"
            "  \"overlap_reflect_th\": 4,  # 重叠反思阈值\n"
            "  \"kw_strg_event_reflect_th\": 10,  # 关键词存储事件反思阈值\n"
            "  \"kw_strg_thought_reflect_th\": 9,  # 关键词存储思考反思阈值\n"
            "  \"recency_w\": 1,  # 最近性权重\n"
            "  \"relevance_w\": 1,  # 相关性权重\n"
            "  \"importance_w\": 1,  # 重要性权重\n"
            "  \"recency_decay\": 0.99,  # 最近性衰减系数\n"
            "  \"importance_trigger_max\": 150,  # 最大重要性触发\n"
            "  \"importance_trigger_curr\": 150,  # 当前重要性触发\n"
            "  \"importance_ele_n\": 0,  # 重要性元素数量\n"
            "  \"thought_count\": 5,  # 思考计数\n"
            "  \"daily_req\": [],  # 每日需求\n"
            "  \"f_daily_schedule\": [],  # 完整的每日时间表\n"
            "  \"f_daily_schedule_hourly_org\": [],  # 每小时组织的每日时间表\n"
            "  \"act_address\": null,  # 当前活动地址\n"
            "  \"act_start_time\": null,  # 活动开始时间\n"
            "  \"act_duration\": null,  # 活动持续时间\n"
            "  \"act_description\": null,  # 活动描述\n"
            "  \"act_pronunciatio\": null,  # 活动发音\n"
            "  \"act_event\": [\"Klaus Mueller\", null, null],  # 当前活动事件\n"
            "  \"act_obj_description\": null,  # 活动对象描述\n"
            "  \"act_obj_pronunciatio\": null,  # 活动对象发音\n"
            "  \"act_obj_event\": [null, null, null],  # 活动对象事件\n"
            "  \"chatting_with\": null,  # 当前聊天对象\n"
            "  \"chat\": null,  # 聊天内容\n"
            "  \"chatting_with_buffer\": {},  # 聊天缓冲区\n"
            "  \"chatting_end_time\": null,  # 聊天结束时间\n"
            "  \"act_path_set\": false,  # 活动路径是否设置\n"
            "  \"planned_path\": []  # 计划路径\n"
            "}\n"
            "```\n"
        ),
        manual_parameters=[
            openapi.Parameter('sim_code', openapi.IN_QUERY, description="实验代码", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="返回实验详细数据"),
            400: openapi.Response(description="参数验证失败"),
        }
    )
    def get(self, request):
        """
        获取实验详细数据
        """
        sim_code = request.GET.get('sim_code')
        if not sim_code:
            return Response({"error": "sim_code is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 目标实验路径
        experiment_dir = os.path.join(EXPERIMENT_STORAGE_ROOT, sim_code, 'personas')

        # 检查路径是否存在
        if not os.path.exists(experiment_dir):
            return Response({"error": "Experiment not found."}, status=status.HTTP_404_NOT_FOUND)

        # 存储所有 bootstrap_memory/scratch.json 文件内容的集合
        scratch_data_collection = []

        # 遍历子目录
        for subdir, dirs, files in os.walk(experiment_dir):
            for file in files:
                # 如果是 bootstrap_memory/scratch.json 文件
                if file == 'scratch.json':
                    scratch_file_path = os.path.join(subdir, file)
                    try:
                        # 读取 scratch.json 文件
                        with open(scratch_file_path, 'r') as f:
                            scratch_data = json.load(f)
                            scratch_data_collection.append(scratch_data)
                    except Exception as e:
                        return Response({"error": f"Error reading {scratch_file_path}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 返回集合数据
        return Response({
            "scratch_data_collection": scratch_data_collection
        }, status=status.HTTP_200_OK)


class ExperimentStopView(APIView):
    """
    终止实验
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="终止实验（目前该接口仅仅更改状态记录中的值——改为finished，无法终止通过start接口启动的实验）",
        manual_parameters=[
            openapi.Parameter('sim_code', openapi.IN_QUERY, description="实验代码", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="实验终止成功"),
            400: openapi.Response(description="参数验证失败"),
        }
    )
    def post(self, request):
        """
        终止实验
        """
        sim_code = request.GET.get('sim_code')
        if not sim_code:
            return Response({"error": "sim_code is required."}, status=status.HTTP_400_BAD_REQUEST)

        experiment_file_path = f'{EXPERIMENT_STORAGE_ROOT }/{sim_code}/reverie/meta.json'
        if not os.path.exists(experiment_file_path):
            return Response({"error": "Experiment not found."}, status=status.HTTP_404_NOT_FOUND)

        with open(experiment_file_path, 'r') as f:
            experiment_data = json.load(f)

        # 更新实验状态为已终止
        experiment_data['status'] = 'stopped'
        with open(experiment_file_path, 'w') as f:
            json.dump(experiment_data, f)

        return Response({"message": "Experiment stopped successfully."}, status=status.HTTP_200_OK)

