<!-- src/components/Controls/SpeedControl.vue  -->
<template>
  <div class="speed-control">
    <label class="speed-label">{{ formattedSpeed }}</label>
    <input 
      type="range"
      :min="min"
      :max="max"
      :step="step"
      class="slider"
      v-model="modelValue"
    />
  </div>
</template>
 
<script setup>
import { computed, defineProps, defineEmits } from 'vue'
 
const props = defineProps({
  modelValue: { type: Number, default: 1 },
  min: { type: Number, default: 0.5 },
  max: { type: Number, default: 3 },
  step: { type: Number, default: 0.1 }
})
 
const emit = defineEmits(['update:modelValue'])
 
const modelValue = computed({
  get: () => props.modelValue, 
  set: (v) => emit('update:modelValue', parseFloat(v))
})
 
const formattedSpeed = computed(() => {
  const value = Math.round(modelValue.value  * 10) / 10 
  return value % 1 === 0 ? `${value}x` : `${value.toFixed(1)}x` 
})
</script>
 
<style scoped>
.speed-control {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 120px;
}
 
.speed-label {
  min-width: 40px;
  text-align: center;
  font-size: 0.9em;
  color: #94A3B8;
}
 
.slider {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  outline: none;
  appearance: none;
}
 
.slider::-webkit-slider-thumb {
  appearance: none;
  width: 14px;
  height: 14px;
  background: #3B82F6;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}
 
.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}
</style>