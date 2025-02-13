<template>
  <div class="speed-control">
    <label>播放速度:</label>
    <select 
      :value="modelValue"
      @change="handleSpeedChange($event.target.value)" 
    >
      <option 
        v-for="speed in speedOptions"
        :key="speed"
        :value="speed"
      >
        {{ speed }}x 
      </option>
    </select>
  </div>
</template>
 
<script setup>
import { defineProps, defineEmits } from 'vue'
 
const emit = defineEmits(['update:modelValue'])
 
const props = defineProps({
  modelValue: {
    type: Number,
    default: 1.0 
  }
})
 
const speedOptions = [0.5, 1.0, 1.5, 2.0]
 
const handleSpeedChange = (value) => {
  const numValue = parseFloat(value)
  emit('update:modelValue', numValue)
}
</script>
 
<style scoped>
.speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255,255,255,0.1);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: background 0.3s ease;
}
 
select {
  background: none;
  border: none;
  color: white;
  padding: 0.2rem 0.5rem;
  cursor: pointer;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg'  viewBox='0 0 24 24' fill='white'%3e%3cpath d='M7 10l5 5 5-5z'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.2rem center;
  padding-right: 1.5rem;
}
 
select:hover {
  background-color: rgba(255,255,255,0.1);
}
 
select:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style>