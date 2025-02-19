<template>
  <div class="quick-start-card">
    <h3 class="header">
      <span class="icon">🚀</span>
      Quick Start Guide 
    </h3>
    <ol class="step-list">
      <li v-for="(step, index) in steps" :key="index">
        <span class="step-number">{{ index + 1 }}</span>
        {{ step }}
      </li>
    </ol>
    <button @click="$router.push('/test')" class="create-button">
      Play Video 
    </button>
  </div>
</template>

<script setup>
const steps = [
'Click the button below to create a new experiment',
'Configure the agent parameters in the editing panel',
'Set the initial state and rules for the environment',
'Start the experiment and observe the interaction process'
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