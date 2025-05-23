<!-- FILE: src/components/Notebook.vue - USING v-bind FOR PROPS -->
<template>
  <div class="notebook-container">
    <nav class="notebook-nav">
      <button @click="activePageKey = 'overview'" :class="{ active: activePageKey === 'overview' }">Overview</button>
      <button @click="activePageKey = 'full_transcript'" :class="{ active: activePageKey === 'full_transcript' }">Transcript</button>
      <button @click="activePageKey = 'ask_ai'" :class="{ active: activePageKey === 'ask_ai' }">Ask AI</button>
      <button @click="activePageKey = 'my_notes'" :class="{ active: activePageKey === 'my_notes' }">My Notes</button>
    </nav>
    <div class="notebook-content">
      <div class="dynamic-component-wrapper"> 
        <KeepAlive>
          <component 
            :is="currentPageComponent"
            v-bind="currentPageProps"
            @video-processed="onVideoProcessedInPage" 
            @segment-clicked="onSegmentClickedInPage"
          />
        </KeepAlive>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed} from 'vue';
import VideoProcessor from './VideoProcessor.vue'; 
import AskAiPage from './AskAiPage.vue';
import MyNotesPage from './MyNotesPage.vue';
import FullTranscriptPage from './FullTranscriptPage.vue';

const props = defineProps({
  rawTranscriptText: { type: String, default: '' },
  transcriptSegments: { type: Array, default: () => [] },
  currentVideoTime: { type: Number, default: 0 }
  // activeSegmentIdInApp prop was removed from App.vue, so it's removed here too
});

const componentsMap = {
  overview: VideoProcessor,
  full_transcript: FullTranscriptPage,
  ask_ai: AskAiPage,
  my_notes: MyNotesPage
};
const activePageKey = ref('overview'); 
const currentPageComponent = computed(() => componentsMap[activePageKey.value] || null);

// Create a computed property to bundle props for the dynamic component
const currentPageProps = computed(() => {
  // Only pass props if the component is FullTranscriptPage or VideoProcessor (or others that need them)
  // AskAiPage and MyNotesPage in their current state don't use these transcript-related props directly
  if (activePageKey.value === 'full_transcript' || activePageKey.value === 'overview') { // Overview might use them later
    return {
      rawTranscriptText: props.rawTranscriptText,
      transcriptSegments: props.transcriptSegments,
      currentVideoTime: props.currentVideoTime
    };
  }
  return {}; // Return empty object for components that don't need these props
});

const emit = defineEmits(['video-processed', 'transcript-segment-clicked']); 
const onVideoProcessedInPage = (payload) => { emit('video-processed', payload); };
const onSegmentClickedInPage = (startTime) => { emit('transcript-segment-clicked', startTime); };
</script>

<style scoped>
/* STYLES ARE THE SAME as the last working version */
.notebook-container { display: flex; flex-direction: column; width: 100%; height: 100%; overflow: hidden; }
.notebook-nav { display: flex; flex-wrap: wrap; gap: 5px; padding-bottom: 10px; margin-bottom: 10px; border-bottom: 2px solid #ddd; flex-shrink: 0; }
.notebook-nav button { padding: 8px 15px; border: 1px solid #ccc; background-color: #f0f0f0; color: #333; cursor: pointer; border-radius: 4px; font-size: 0.9em; transition: background-color 0.2s, color 0.2s;}
.notebook-nav button:hover { background-color: #e0e0e0; }
.notebook-nav button.active { background-color: #42b983; color: white; border-color: #36a374; font-weight: bold; }
.notebook-content { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; padding: 0; min-height: 0; }
.dynamic-component-wrapper { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; padding: 15px 20px; background-color: #ffffff; border-radius: 4px; border: 1px solid #e0e0e0;}
</style>