<!-- FILE: src/components/Notebook.vue - EXACT VERSION TO USE -->
<template>
  <div class="notebook-container">
    <nav class="notebook-nav">
      <button 
        @click="activePageKey = 'overview'" 
        :class="{ active: activePageKey === 'overview' }">
        Overview
      </button>
      <button 
        @click="activePageKey = 'ask_ai'" 
        :class="{ active: activePageKey === 'ask_ai' }">
        Ask AI
      </button>
      <button 
        @click="activePageKey = 'my_notes'" 
        :class="{ active: activePageKey === 'my_notes' }">
        My Notes
      </button>
    </nav>

    <div class="notebook-content">
      <div class="dynamic-component-wrapper"> 
        <KeepAlive>
          <component :is="currentPageComponent" />
        </KeepAlive>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import VideoProcessor from './VideoProcessor.vue'; 
import AskAiPage from './AskAiPage.vue';
import MyNotesPage from './MyNotesPage.vue';

const componentsMap = {
  overview: VideoProcessor,
  ask_ai: AskAiPage,
  my_notes: MyNotesPage
};
const activePageKey = ref('overview');
const currentPageComponent = computed(() => {
  return componentsMap[activePageKey.value] || null;
});
</script>

<style scoped>
.notebook-container {
  display: flex;
  flex-direction: column;
  width: 100%; 
  height: 100%; 
  overflow: hidden; 
}

.notebook-nav {
  display: flex;
  flex-wrap: wrap; 
  gap: 5px; 
  padding-bottom: 10px;
  margin-bottom: 10px; 
  border-bottom: 2px solid #ddd; 
  flex-shrink: 0; 
}
.notebook-nav button { padding: 8px 15px; border: 1px solid #ccc; background-color: #f0f0f0; color: #333; cursor: pointer; border-radius: 4px; font-size: 0.9em; transition: background-color 0.2s, color 0.2s;}
.notebook-nav button:hover { background-color: #e0e0e0; }
.notebook-nav button.active { background-color: #42b983; color: white; border-color: #36a374; font-weight: bold; }

.notebook-content { 
  flex-grow: 1; 
  overflow: hidden; 
  display: flex; 
  flex-direction: column; 
  padding: 0; 
  min-height: 0; 
}

.dynamic-component-wrapper { 
  flex-grow: 1;         
  display: flex;          
  flex-direction: column; 
  overflow: hidden;       
  min-height: 0;          
  padding: 15px 20px;     
  background-color: #ffffff; 
  border-radius: 4px;       
  border: 1px solid #e0e0e0;
}
</style>