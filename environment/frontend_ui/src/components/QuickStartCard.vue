<!-- QuickStartCard.vue  -->
<template>
    <div class="quick-start-card">
      <h3 class="header">
        <span class="icon">🚀</span>
        快速入门 
      </h3>
      <ol class="step-list">
        <li v-for="(step, index) in steps" :key="index">
          <span class="step-number">{{ index + 1 }}</span>
          {{ step }}
        </li>
      </ol>
      <button @click="$emit('create')" class="create-button">
        新建实验 
      </button>
    </div>
  </template>
   
  <script setup>
  const steps = [
    '点击下方按钮创建新实验',
    '在编辑面板配置智能体参数',
    '设置环境初始状态与规则',
    '启动实验并观察交互过程'
  ]
  </script>
   
  <style scoped>
  .quick-start-card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
   
  .create-button {
    background: #3b82f6;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    margin-top: 1rem;
  }
  </style>