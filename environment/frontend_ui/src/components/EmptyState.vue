<!-- src/components/EmptyState.vue  -->
<template>
    <div class="empty-state">
      <div class="illustration">
        <svg xmlns="http://www.w3.org/2000/svg"  viewBox="0 0 96 96" aria-hidden="true">
          <path fill="#64748B" d="M48 16a32 32 0 1 0 0 64 32 32 0 0 0 0-64Zm0 8a24 24 0 0 1 24 24c0 6.1-3.9 11.4-9.6 14.4l-14-14a2 2 0 0 0-2.8 0l-14 14C27.9 59.4 24 54.1 24 48A24 24 0 0 1 48 24Z"/>
          <path fill="#94A3B8" d="m62.4 62.4-14-14a2 2 0 0 0-2.8 0l-14 14C27.9 59.4 24 54.1 24 48a24 24 0 1 1 48 0c0 6.1-3.9 11.4-9.6 14.4Z"/>
          <circle cx="48" cy="48" r="6" fill="#E2E8F0"/>
        </svg>
      </div>
      
      <div class="content">
        <h3 class="title">无选中实验</h3>
        <p class="description">
          请从左侧列表选择实验，或创建新的仿真实验 
        </p>
      </div>
    </div>
  </template>
   
  <style scoped>
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 2rem;
    text-align: center;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    border: 1px dashed rgba(255,255,255,0.1);
    margin: 16px;
  }
   
  .illustration {
    width: 160px;
    height: 160px;
    margin-bottom: 1.5rem;
    opacity: 0.8;
  }
   
  .title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #E2E8F0;
    margin-bottom: 0.5rem;
  }
   
  .description {
    color: #94A3B8;
    max-width: 360px;
    line-height: 1.5;
    margin-bottom: 1.5rem;
  }
  </style>