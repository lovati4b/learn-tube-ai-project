<!-- FILE: src/components/Notebook.vue - COMPLETE WITH ENHANCED LOGGING -->
<template>
  <div class="notebook-container">
    <nav class="notebook-nav">
      <button @click="setActivePage('overview')" :class="{ active: activePageKey === 'overview' }">Overview</button>
      <button @click="setActivePage('full_transcript')" :class="{ active: activePageKey === 'full_transcript' }">Transcript</button>
      <button @click="setActivePage('ask_ai')" :class="{ active: activePageKey === 'ask_ai' }">Ask AI</button>
      <button @click="setActivePage('my_notes')" :class="{ active: activePageKey === 'my_notes' }">My Notes</button>
    </nav>
    <div class="notebook-content">
      <div class="dynamic-component-wrapper"> 
        <KeepAlive>
          <component 
            :is="currentPageComponent"
            v-bind="currentPageProps" 
            @video-processed="onVideoProcessedInPage" 
            @segment-clicked="onSegmentClickedInPage"
            @explain-text-requested="handleExplainTextRequestFromPage" 
            @explanation-query-handled="onExplanationQueryHandled"
          />
        </KeepAlive>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import VideoProcessor from './VideoProcessor.vue'; 
import AskAiPage from './AskAiPage.vue';
import MyNotesPage from './MyNotesPage.vue';
import FullTranscriptPage from './FullTranscriptPage.vue';

const props = defineProps({
  rawTranscriptText: { type: String, default: '' },
  transcriptSegments: { type: Array, default: () => [] },
  currentVideoTime: { type: Number, default: 0 }
});

const emit = defineEmits(['video-processed', 'transcript-segment-clicked', 'explain-text-requested']); 

const componentsMap = {
  overview: VideoProcessor,
  full_transcript: FullTranscriptPage,
  ask_ai: AskAiPage,
  my_notes: MyNotesPage
};

const activePageKey = ref('overview'); 
const textToPassToAskAI = ref(null); 

const currentPageComponent = computed(() => componentsMap[activePageKey.value] || null);

const currentPageProps = computed(() => {
  let pageProps = {};
  // Pass transcript data to Overview and FullTranscriptPage by default
  // Other pages like MyNotes won't use them even if passed (Vue handles unused props gracefully)
  // AskAiPage uses a specific prop for explained text.
  pageProps.rawTranscriptText = props.rawTranscriptText;
  pageProps.transcriptSegments = props.transcriptSegments;
  pageProps.currentVideoTime = props.currentVideoTime;
  
  if (activePageKey.value === 'ask_ai' && textToPassToAskAI.value) {
    pageProps.textForExplanation = textToPassToAskAI.value;
  }
  
  console.log(`Notebook.vue: For activePageKey '${activePageKey.value}', computed currentPageProps:`, JSON.parse(JSON.stringify(pageProps)));
  return pageProps;
});

const onVideoProcessedInPage = (payload) => { emit('video-processed', payload); };
const onSegmentClickedInPage = (startTime) => { emit('transcript-segment-clicked', startTime); };

const handleExplainTextRequestFromPage = (selectedText) => {
  console.log("Notebook.vue: 'explain-text-requested' caught from page, text:", `"${selectedText}"`);
  textToPassToAskAI.value = selectedText; 
  activePageKey.value = 'ask_ai';        
};

const onExplanationQueryHandled = () => {
  console.log("Notebook.vue: 'explanation-query-handled' caught from AskAiPage.");
  textToPassToAskAI.value = null; 
};

const setActivePage = (pageKey) => {
    if (componentsMap[pageKey]) {
        activePageKey.value = pageKey;
        if (pageKey !== 'ask_ai' && textToPassToAskAI.value) {
           textToPassToAskAI.value = null;
        }
    }
};
</script>

<style scoped>
/* STYLES ARE THE SAME as your last working version */
.notebook-container { display: flex; flex-direction: column; width: 100%; height: 100%; overflow: hidden; }
.notebook-nav { display: flex; flex-wrap: wrap; gap: 5px; padding-bottom: 10px; margin-bottom: 10px; border-bottom: 2px solid #ddd; flex-shrink: 0; }
.notebook-nav button { padding: 8px 15px; border: 1px solid #ccc; background-color: #f0f0f0; color: #333; cursor: pointer; border-radius: 4px; font-size: 0.9em; transition: background-color 0.2s, color 0.2s;}
.notebook-nav button:hover { background-color: #e0e0e0; }
.notebook-nav button.active { background-color: #42b983; color: white; border-color: #36a374; font-weight: bold; }
.notebook-content { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; padding: 0; min-height: 0; }
.dynamic-component-wrapper { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; padding: 15px 20px; background-color: #ffffff; border-radius: 4px; border: 1px solid #e0e0e0;}
</style>