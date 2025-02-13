<template>
  <div class="simulation-player">
    <iframe 
      :src="playerUrl"
      frameborder="0"
      allowfullscreen
      class="simulation-frame"
    ></iframe>

    <div class="control-overlay">
      <button @click="togglePlayback">{{ isPlaying ? '暂停' : '播放' }}</button>
      <input type="range" v-model="playbackSpeed" min="0.5" max="3" step="0.5">
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  experimentId: {
    type: String,
    required: true
  }
})

const playerUrl = computed(() => 
  `/api/stanford-town/player/${props.experimentId}` 
)

const isPlaying = ref(true)
const playbackSpeed = ref(1.0)

const togglePlayback = () => {
  isPlaying.value  = !isPlaying.value 
  // 调用播放器控制API
}
</script>