<!-- src/components/Controls/AsyncButton.vue  -->
<template>
  <button 
    class="async-button"
    :class="[variant, { loading }]"
    :disabled="loading"
    @click="handleClick"
  >
    <span class="button-content">
      <progress-spinner 
        v-if="loading"
        :size="16"
        :stroke-width="2"
        class="spinner"
      />
      <slot />
    </span>
  </button>
</template>
 
<script setup>
import { ref, defineProps, defineEmits } from 'vue'
 
const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: v => ['primary', 'secondary'].includes(v)
  },
  disabled: Boolean 
})
 
const emit = defineEmits(['click'])
const loading = ref(false)
 
const handleClick = async (e) => {
  if (props.disabled  || loading.value)  return 
  loading.value  = true 
  try {
    await emit('click', e)
  } finally {
    loading.value  = false 
  }
}
</script>
 
<style scoped>
.async-button {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}
 
.primary {
  background: #3B82F6;
  color: white;
}
 
.primary:hover:not(:disabled) {
  background: #2563EB;
}
 
.secondary {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #E2E8F0;
}
 
.secondary:hover:not(:disabled) {
  background: rgba(255,255,255,0.15);
}
 
:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
 
.button-content {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}
 
.spinner {
  animation: spin 1s linear infinite;
}
 
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>