from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from integration_core.views import ExperimentListView, PhaserGameEmbedView, VideoHLSView  # 引入 ExperimentListView 视图集

urlpatterns = [    
    path('experiments/', ExperimentListView.as_view(),  name='experiment_list'),
    path('phaserVideo',PhaserGameEmbedView.as_view(),name='phaserVideo'),
    path('hlsVideo',VideoHLSView.as_view(), name='hlsVideo')
]