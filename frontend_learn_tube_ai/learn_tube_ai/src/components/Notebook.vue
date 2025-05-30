<!-- START FILE: frontend_learn_tube_ai\learn_tube_ai\src\components\Notebook.vue --- REFACTORED FOR PINIA -->
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
            v-if="currentPageComponent"
            :key="activePageKey"
            :is="currentPageComponent"
            v-bind="currentPageProps" 
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
import { ref, computed, watch} from 'vue';
// No need to import useContentStore here unless Notebook directly interacts with it,
// for now, it gets all necessary data via props from App.vue.
import VideoProcessor from './VideoProcessor.vue'; 
import AskAiPage from './AskAiPage.vue';
import MyNotesPage from './MyNotesPage.vue';
import FullTranscriptPage from './FullTranscriptPage.vue';

const props = defineProps({
  // Props coming from App.vue (derived from Pinia store's dataForNotebook getter)
  currentContentId: { type: [String, null], default: null }, // <<<<<<< ADD THIS LINE
  rawTranscriptText: { type: String, default: '' },
  transcriptSegments: { type: Array, default: () => [] },
  currentVideoTime: { type: Number, default: 0 },
  analysisForOverview: { type: Object, default: null },
  currentTitleForOverview: { type: String, default: '' },
  isLoadingState: { type: Boolean, default: false },
  errorState: { type: Object, default: null },
  showTranscriptPasteFallbackState: { type: Boolean, default: false },
  currentVideoIdForFallback: { type: String, default: null },
  currentVideoUrlForFallback: { type: String, default: null },
});

// <<< --- ADD THIS WATCHER --- >>>
watch(() => props.currentContentId, (newVal, oldVal) => {
  console.log(`Notebook.vue PROPS WATCHER for currentContentId: New='${newVal}', Old='${oldVal}'`);
}, { immediate: true }); // immediate:true to see its initial value

// <<< --- ADD THIS WATCHER --- >>>
watch(() => props.rawTranscriptText, (newVal, oldVal) => {
  console.log(`Notebook.vue PROPS WATCHER: rawTranscriptText changed. New: "${newVal ? newVal.substring(0,30)+'...' : 'EMPTY'}", Old: "${oldVal ? oldVal.substring(0,30)+'...' : 'EMPTY'}"`);
});

watch(() => props.analysisForOverview, (newVal, oldVal) => {
  console.log(`Notebook.vue PROPS WATCHER: analysisForOverview changed. New is null? ${!newVal}, Old is null? ${!oldVal}`);
  if (newVal) {
    console.log('Notebook.vue PROPS WATCHER: New analysisForOverview:', JSON.parse(JSON.stringify(newVal)));
  }
}, { deep: true }); // Use deep watch for objects

watch(() => props.transcriptSegments, (newVal, oldVal) => {
  console.log(`Notebook.vue PROPS WATCHER: transcriptSegments changed. New length: ${newVal?.length}, Old length: ${oldVal?.length}`);
}, { deep: true });
// <<< --- END OF ADDED WATCHER --- >>>

const emit = defineEmits(['transcript-segment-clicked', 'explain-text-requested']); 
// REMOVED 'video-processed' emit, as VideoProcessor will handle store updates.

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
  let pageProps = {
    // Common props for most pages
    currentContentId: props.currentContentId, // <<< PASS IT DOWN
    rawTranscriptText: props.rawTranscriptText,
    transcriptSegments: props.transcriptSegments,
    currentVideoTime: props.currentVideoTime, // For FullTranscriptPage and potentially others
  };
  
  // Specific props for VideoProcessor (Overview page)
  if (activePageKey.value === 'overview') {
    pageProps.analysisForOverview = props.analysisForOverview;
    pageProps.currentTitleForOverview = props.currentTitleForOverview;
    pageProps.isLoadingState = props.isLoadingState;
    pageProps.errorState = props.errorState;
    pageProps.showTranscriptPasteFallbackState = props.showTranscriptPasteFallbackState;
    pageProps.currentVideoIdForFallback = props.currentVideoIdForFallback;
    pageProps.currentVideoUrlForFallback = props.currentVideoUrlForFallback;
  }
  
  // Specific props for AskAiPage
  if (activePageKey.value === 'ask_ai' && textToPassToAskAI.value) {
    pageProps.textForExplanation = textToPassToAskAI.value;
  }
  
   // <<< --- ADD THIS DETAILED LOG --- >>>
  console.log(
    `Notebook.vue: activePageKey='${activePageKey.value}'. Preparing currentPageProps:`, 
    JSON.parse(JSON.stringify(pageProps)) // Deep copy for logging complex objects
  );
  // <<< --- END OF ADDED LOG --- >>>

  return pageProps;
});

// onVideoProcessedInPage is REMOVED - VideoProcessor updates store directly
const onSegmentClickedInPage = (startTime) => { emit('transcript-segment-clicked', startTime); };

const handleExplainTextRequestFromPage = (selectedText) => {
  textToPassToAskAI.value = selectedText; 
  activePageKey.value = 'ask_ai';        
};

const onExplanationQueryHandled = () => {
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
/* STYLES REMAIN THE SAME */
.notebook-container { display: flex; flex-direction: column; width: 100%; height: 100%; overflow: hidden; }
.notebook-nav { display: flex; flex-wrap: wrap; gap: 5px; padding-bottom: 10px; margin-bottom: 10px; border-bottom: 2px solid #ddd; flex-shrink: 0; }
.notebook-nav button { padding: 8px 15px; border: 1px solid #ccc; background-color: #f0f0f0; color: #333; cursor: pointer; border-radius: 4px; font-size: 0.9em; transition: background-color 0.2s, color 0.2s;}
.notebook-nav button:hover { background-color: #e0e0e0; }
.notebook-nav button.active { background-color: #42b983; color: white; border-color: #36a374; font-weight: bold; }
.notebook-content { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; padding: 0; min-height: 0; }
.dynamic-component-wrapper { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; padding: 15px 20px; background-color: #ffffff; border-radius: 4px; border: 1px solid #e0e0e0;}
</style>
<!-- END FILE: frontend_learn_tube_ai\learn_tube_ai\src\components\Notebook.vue --- REFACTORED FOR PINIA -->