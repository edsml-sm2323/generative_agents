<!-- AsyncButton.vue  -->
<template>
    <button 
      class="async-button"
      :class="[
        variantClass,
        { 'loading': loading }
      ]"
      :disabled="disabled || loading"
    >
      <span class="content">
        <slot v-if="!loading" name="default"></slot>
        <slot v-else name="loading"></slot>
      </span>
    </button>
  </template>
   
  <script setup>
import { computed, props, defineProps } from 'vue'

  defineProps({
    loading: Boolean,
    disabled: Boolean,
    variant: {
      type: String,
      default: 'primary',
      validator: v => ['primary', 'success', 'danger'].includes(v)
    }
  })
   
  const variantClass = computed(() => `variant-${props.variant}`) 
  </script>
   
  <style scoped>
  .async-button {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }
   
  .variant-primary { background: #2196F3; color: white; }
  .variant-success { background: #4CAF50; color: white; }
  .variant-danger { background: #f44336; color: white; }
   
  .async-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
   
  .async-button.loading  {
    position: relative;
    cursor: progress;
  }
   
  .async-button.loading::after  {
    content: "";
    display: inline-block;
    width: 1em;
    height: 1em;
    margin-left: 0.5em;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
   
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  </style>