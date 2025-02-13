<template>
  <teleport to="body">
    <transition name="modal-fade">
      <div 
        v-if="modelValue"
        class="modal-mask"
        @click.self="handleClose" 
      >
        <div class="modal-wrapper">
          <div class="modal-container">
            <!-- 头部 -->
            <div class="modal-header">
              <h2 class="modal-title">
                {{ isEditMode ? '编辑实验配置' : '新建实验' }}
              </h2>
              <button 
                class="close-btn"
                @click="handleClose"
                aria-label="关闭"
              >
                &times;
              </button>
            </div>
 
            <!-- 表单主体 -->
            <form 
              @submit.prevent="handleSubmit" 
              class="experiment-form"
            >
              <div class="form-grid">
                <!-- 实验名称 -->
                <div class="form-item" :class="{ error: v$.name.$error }">
                  <label for="name">实验名称</label>
                  <input 
                    id="name"
                    v-model.trim="formData.name" 
                    type="text"
                    placeholder="请输入实验名称"
                    @blur="v$.name.$touch()"
                  >
                  <span class="error-msg" v-if="v$.name.$error">
                    请输入2-50个字符的名称 
                  </span>
                </div>
 
                <!-- 实验描述 -->
                <div class="form-item" :class="{ error: v$.description.$error }">
                  <label for="description">实验描述</label>
                  <textarea 
                    id="description"
                    v-model.trim="formData.description" 
                    rows="3"
                    placeholder="请输入实验描述..."
                    @blur="v$.description.$touch()"
                  ></textarea>
                  <span class="error-msg" v-if="v$.description.$error">
                    描述不能超过500个字符 
                  </span>
                </div>
 
                <!-- 持续时间 -->
                <div class="form-item">
                  <label for="duration">持续时间（小时）</label>
                  <input 
                    id="duration"
                    v-model.number="formData.duration" 
                    type="number"
                    min="1"
                    max="720"
                    step="1"
                  >
                </div>
 
                <!-- 环境参数 -->
                <div class="form-item">
                  <label>环境参数</label>
                  <div class="param-grid">
                    <div 
                      v-for="(param, index) in formData.params"  
                      :key="index"
                      class="param-item"
                    >
                      <input 
                        v-model.trim="param.key" 
                        placeholder="参数名"
                        class="param-input"
                      >
                      <span class="separator">:</span>
                      <input 
                        v-model.trim="param.value" 
                        placeholder="参数值"
                        class="param-input"
                      >
                      <button 
                        type="button"
                        class="remove-param"
                        @click="removeParam(index)"
                      >
                        &times;
                      </button>
                    </div>
                    <button 
                      type="button"
                      class="add-param"
                      @click="addParam"
                    >
                      + 添加参数 
                    </button>
                  </div>
                </div>
              </div>
 
              <!-- 表单操作 -->
              <div class="form-actions">
                <button 
                  type="button"
                  class="cancel-btn"
                  @click="handleClose"
                  :disabled="isSubmitting"
                >
                  取消 
                </button>
                <button 
                  type="submit"
                  class="submit-btn"
                  :disabled="v$.$invalid || isSubmitting"
                >
                  <span v-if="isSubmitting" class="submit-loading"></span>
                  {{ isSubmitting ? '提交中...' : '确认提交' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>
 
<script setup>
import { ref, reactive, watch, defineProps, defineEmits } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, maxLength, minLength } from '@vuelidate/validators'
 
const props = defineProps({
  modelValue: Boolean,
  isEditMode: Boolean,
  initialData: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      duration: 24,
      params: [{ key: '', value: '' }]
    })
  }
})
 
const emit = defineEmits(['submit', 'update:modelValue'])
 
// 表单数据 
const formData = reactive({
  name: '',
  description: '',
  duration: 24,
  params: [{ key: '', value: '' }]
})
 
// 验证规则 
const rules = {
  name: {
    required,
    minLength: minLength(2),
    maxLength: maxLength(50)
  },
  description: {
    maxLength: maxLength(500)
  }
}
 
const v$ = useVuelidate(rules, formData)
 
// 表单状态 
const isSubmitting = ref(false)
 
// 同步初始数据 
watch(() => props.initialData,  (newVal) => {
  Object.assign(formData,  JSON.parse(JSON.stringify(newVal))) 
}, { immediate: true })
 
// 参数操作 
const addParam = () => {
  formData.params.push({  key: '', value: '' })
}
 
const removeParam = (index) => {
  formData.params.splice(index,  1)
}
 
// 表单提交 
const handleSubmit = async () => {
  v$.value.$touch()
  if (v$.value.$invalid) return 
 
  try {
    isSubmitting.value  = true 
    await emit('submit', {
      ...formData,
      params: formData.params.filter(p  => p.key  && p.value) 
    })
    handleClose()
  } finally {
    isSubmitting.value  = false 
  }
}
 
// 关闭处理 
const handleClose = () => {
  emit('update:modelValue', false)
  resetForm()
}
 
// 重置表单 
const resetForm = () => {
  v$.value.$reset()
  Object.assign(formData,  {
    name: '',
    description: '',
    duration: 24,
    params: [{ key: '', value: '' }]
  })
}
</script>
 
<style scoped>
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: opacity 0.3s ease;
}
 
.modal-wrapper {
  max-width: 90%;
  width: 600px;
}
 
.modal-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
  padding: 20px;
}
 
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
 
.modal-title {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}
 
.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s;
}
 
.close-btn:hover {
  color: #e74c3c;
}
 
.experiment-form {
  display: grid;
  gap: 1.5rem;
}
 
.form-grid {
  display: grid;
  gap: 1rem;
}
 
.form-item {
  display: grid;
  gap: 0.5rem;
}
 
label {
  font-weight: 500;
  color: #34495e;
}
 
input, textarea {
  padding: 0.75rem;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  transition: border-color 0.3s;
}
 
input:focus, textarea:focus {
  border-color: #3498db;
  outline: none;
}
 
.error input, .error textarea {
  border-color: #e74c3c;
}
 
.error-msg {
  color: #e74c3c;
  font-size: 0.85rem;
}
 
.param-grid {
  display: grid;
  gap: 0.5rem;
}
 
.param-item {
  display: grid;
  grid-template-columns: 1fr 20px 1fr 30px;
  gap: 0.5rem;
  align-items: center;
}
 
.param-input {
  padding: 0.5rem;
}
 
.separator {
  text-align: center;
}
 
.remove-param {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 1.2rem;
}
 
.add-param {
  width: fit-content;
  background: #f8f9fa;
  border: 1px dashed #bdc3c7;
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
}
 
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
 
.submit-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.3s;
}
 
.submit-btn {
  background: #3498db;
  color: white;
  border: none;
}
 
.submit-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}
 
.cancel-btn {
  background: none;
  border: 1px solid #bdc3c7;
  color: #2c3e50;
}
 
.submit-loading {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}
 
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
 
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s;
}
 
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>