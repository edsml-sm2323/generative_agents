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
            <!-- Header -->
            <div class="modal-header">
              <h2 class="modal-title">
                {{ isEditMode ? 'Edit experiment configuration' : 'New experiment' }}
              </h2>
              <button 
                class="close-btn"
                @click="handleClose"
                aria-label="Close"
              >
                &times;
              </button>
            </div>
 
            <!-- Form -->
            <form 
              @submit.prevent="handleSubmit" 
              class="experiment-form"
            >
              <div class="form-grid">
                <!-- Experiment Name -->
                <div class="form-item" :class="{ error: v$.name.$error }">
                  <label for="name"><b>Experiment Name:</b></label>
                  <input 
                    id="name"
                    v-model.trim="formData.name" 
                    type="text"
                    placeholder="Please enter the experiment name"
                    @blur="v$.name.$touch()"
                  >
                  <span class="error-msg" v-if="v$.name.$error">
                    Please enter a name of 2-50 characters
                  </span>
                </div>
 
                <!-- Experiment Description -->
                <div class="form-item" :class="{ error: v$.description.$error }">
                  <label for="description"><b>Experiment description:</b></label>
                  <textarea 
                    id="description"
                    v-model.trim="formData.description" 
                    rows="1"
                    placeholder="Please enter the experiment description..."
                    @blur="v$.description.$touch()"
                  ></textarea>
                  <span class="error-msg" v-if="v$.description.$error">
                    The description cannot exceed 500 characters
                  </span>
                </div>
 
                <!-- Duration and Step Length -->
                <div class="form-item">
                  <label for="duration"><b>Experiment steps:</b></label>
                  <input 
                    id="steps"
                    v-model.number="formData.duration" 
                    type="number"
                    min="1"
                    max="720"
                    step="1"
                    placeholder="步数"
                  >
                </div>
                
                <div class="form-item">
                  <label for="durationStep"><b>Experimental step length:</b></label>
                  <input 
                    id="durationStep"
                    v-model.number="formData.stepLength" 
                    type="number"
                    min="1"
                    max="720"
                    step="1"
                    placeholder="Each step corresponds to the number of seconds in the simulation experiment (eg: 10)"
                  >
                </div>
 
                <!-- Characters -->
                <div class="form-item">
                  <label><b>Experimental figure allocation</b></label>
                  <div class="character-grid">
                    <div 
                      v-for="(char, index) in formData.characters" 
                      :key="index"
                      class="character-card"
                    >
                      <div class="character-header">
                        <h4>Character{{ index + 1 }}</h4>
                        <button 
                          type="button"
                          class="remove-character"
                          @click="removeCharacter(index)"
                          v-if="formData.characters.length > 1"
                        >
                          &times;
                        </button>
                      </div>

                      <div class="character-form">
                        <!-- Name, Age, and Image -->
                        <div class="form-row">
                          <div class="form-col">
                            <label>Name *</label>
                            <div class="name-group">
                              <input 
                                v-model.trim="char.first_name" 
                                placeholder="First Name"
                                @blur="v$.characters.$each[index].first_name.$touch()"
                              >
                              <input 
                                v-model.trim="char.last_name" 
                                placeholder="Last Name"
                                @blur="v$.characters.$each[index].last_name.$touch()"
                              >
                            </div>
                          </div>
                          <div class="form-col">
                            <label>Age *</label>
                            <input 
                              type="number"
                              v-model.number="char.age" 
                              min="1"
                              max="120"
                              @blur="v$.characters.$each[index].age.$touch()"
                            >
                          </div>
                        </div>

                        <!-- Coordinates and Living Area -->
                        <div class="form-row">
                          <div class="form-col">
                            <label>Initial coordinate</label>
                            <div class="coordinate-group">
                              <input 
                                type="number"
                                v-model.number="char.coordinates_x" 
                                placeholder="x-coordinate"
                                min="50"
                                max="200"
                              >
                              <span class="separator"> , </span>
                              <input 
                                type="number"
                                v-model.number="char.coordinates_y" 
                                placeholder="y-coordinate"
                                min="50"
                                max="200"
                              >
                            </div>
                          </div>
                          <div class="form-col">
                            <label>Place</label>
                            <input v-model.trim="char.living_area"  placeholder="">
                          </div>
                        </div>

                        <hr/>
                        <!-- Image Selector -->
                        <div class="form-row">
                          <div class="form-col">
                            <label for="character-image-{{ index }}">Character image</label>
                            <select 
                              v-model="char.image" 
                              @change="updateCharacterImage(char)"
                            >
                              <option disabled value="">Select an image of a person</option>
                              <option 
                                v-for="(image, i) in imageOptions" 
                                :key="i" 
                                :value="image.name"
                              >
                                {{ image.name }}
                              </option>
                            </select>

                            <!-- Display selected image next to the dropdown -->
                            <div v-if="char.image" class="selected-image">
                              <img :src="char.image" alt="Selected character image" />
                            </div>
                          </div>
                        </div>

                        <!-- Background -->
                        <!-- Background -->
                        <div class="form-full">
                          <label>Personality, Currently, History</label><br/>
                          <textarea 
                            v-model.trim="char.personality" 
                            rows="2"
                            placeholder="Describe personality traits (e.g. Optimistic, Introverted, Adventurous)"
                          ></textarea>
                          <textarea 
                            v-model.trim="char.currently" 
                            rows="2"
                            placeholder="Current situation (e.g. Working as a freelance artist, exploring new technologies)"
                          ></textarea>
                          <textarea 
                            v-model.trim="char.history" 
                            rows="2"
                            placeholder="Background history (e.g. Grew up in a small town, studied fine arts in college)"
                          ></textarea>
                        </div>
                      </div>
                    </div>

                    <button 
                      type="button"
                      class="add-character"
                      @click="addCharacter"
                    >
                      + Add a character 
                    </button>
                  </div>
                </div>
              </div>
 
              <!-- Form Actions -->
              <div class="form-actions">
                <button 
                  type="button"
                  class="cancel-btn"
                  @click="handleClose"
                  :disabled="isSubmitting"
                >
                Cancel 
                </button>
                <button 
                  type="submit"
                  class="submit-btn"
                  :disabled="v$.$invalid || isSubmitting"
                >
                  <span v-if="isSubmitting" class="submit-loading"></span>
                  {{ isSubmitting ? 'Submitting...' : 'Confirm submission' }}
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
// Imports and Props
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
      params: [{ key: '', value: '' }],
      characters: [{ first_name: '', last_name: '', age: '', coordinates_x: '', coordinates_y: '', living_area: '', innate: '', learned: '', image: '' , personality: '', currently:'', history:''}]
    })
  }
})

const emit = defineEmits(['submit', 'update:modelValue'])

const formData = reactive({
  name: '',
  description: '',
  duration: 10,
  stepLength: 10,
  params: [],
  characters: [{ first_name: '', last_name: '', age: '', coordinates_x: '', coordinates_y: '', living_area: '', innate: '', learned: '', image: '' ,  personality: '', currently:'', history:''}]
})

const imageOptions = ref([
  { name: 'Image 1', url: '/img/1.png' },
  { name: 'Image 2', url: '/img/2.png' },
  { name: 'Image 3', url: '/img/3.png' },
  { name: 'Image 4', url: '/img/4.png' },
  { name: 'Image 5', url: '/img/5.png' }
])

const rules = {
  name: {
    required,
    minLength: minLength(2),
    maxLength: maxLength(50)
  },
  description: {
    maxLength: maxLength(500)
  },
  characters: {
    required
  }
}

const v$ = useVuelidate(rules, formData)

const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (v$.$invalid) return

  isSubmitting.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  emit('submit', formData)
  handleClose()
}

const handleClose = () => {
  emit('update:modelValue', false)
}

const addCharacter = () => {
  formData.characters.push({
    first_name: '',
    last_name: '',
    age: '',
    coordinates_x: '',
    coordinates_y: '',
    living_area: '',
    innate: '',
    learned: '',
    image: ''
  })
}

const removeCharacter = (index) => {
  formData.characters.splice(index, 1)
}

const updateCharacterImage = (char) => {
  const selectedImage = imageOptions.value.find(image => image.name === char.image)
  if (selectedImage) {
    char.image = selectedImage.url
  } else {
    char.image = ''
  }
}

watch(() => props.isEditMode, () => {
  if (props.isEditMode && props.initialData) {
    formData.name = props.initialData.name
    formData.description = props.initialData.description
    formData.duration = props.initialData.duration
    formData.params = [...props.initialData.params]
    formData.characters = [...props.initialData.characters]
  }
}, { immediate: true })
</script>

<style scoped>
/* Modal and form layout adjustments */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease-in-out;
}

.modal-wrapper {
  width: 80%;
  max-width: 800px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transform: scale(0.95);
  animation: zoomIn 0.3s ease-out;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.character-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.character-card {
  width: 100%;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.character-card:hover {
  transform: translateY(-5px);
}

.character-form .form-row {
  display: flex;
  justify-content: space-between;
}

.form-col {
  width: 48%;
}

.form-col label {
  display: block;
  margin-bottom: 5px;
}

.add-character {
  background-color: #2ed573;
  color: white;
  border: none;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.add-character:hover {
  background-color: #27d369;
}

.submit-btn:disabled {
  background-color: grey;
}

.cancel-btn {
  background-color: #ccc;
  padding: 8px 16px;
  border-radius: 4px;
}

.remove-character {
  background-color: #ff4757;
  color: white;
  border: none;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 4px;
}

.remove-character:hover {
  background-color: #ff6b81;
}

select {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.selected-image img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}

@keyframes fadeIn {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes zoomIn {
  0% {
    transform: scale(0.95);
  }
  100% {
    transform: scale(1);
  }
}
</style>
