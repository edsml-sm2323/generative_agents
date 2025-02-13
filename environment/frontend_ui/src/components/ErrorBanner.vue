<!-- src/components/Feedback/ErrorBanner.vue  -->
<template>
  <div class="error-banner">
    <div class="content">
      <icon name="warning" class="icon" />
      <span class="message">{{ message }}</span>
    </div>
    <button class="close-btn" @click="$emit('close')">
      <icon name="close" />
    </button>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

defineProps({
  message: { type: String, required: true }
})
</script>

<style scoped>
.error-banner {
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: #B91C1C;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
}

.close-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: inherit;
}

@media (prefers-color-scheme: dark) {
  .error-banner {
    background: rgba(127, 29, 29, 0.3);
    border-color: rgba(248, 113, 113, 0.2);
  }
}
</style>