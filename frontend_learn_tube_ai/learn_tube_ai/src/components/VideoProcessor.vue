<!-- START FILE: frontend_learn_tube_ai\learn_tube_ai\src\components\VideoProcessor.vue --- REFACTORED FOR PINIA -->
<template>
  <div class="video-processor">
    <div class="main-title-container">
      <h2 class="main-title-text">Learn From Video / Analyze Text</h2>
      <button v-if="!inputAreaVisible" @click="revealInputArea" class="reopen-input-button" title="New Input or Change Source">
        ➕ New Input
      </button>
    </div>

    <div v-if="inputAreaVisible" class="input-section-wrapper">
      <div class="input-controls-header">
        <div class="input-mode-selector">
          <label :class="{active: contentStore.activeMode === 'youtube'}" @click="setInputMode('youtube')">
            <input type="radio" value="youtube" :checked="contentStore.activeMode === 'youtube'" name="inputModeRadio"/>
            YouTube URL
          </label>
          <label :class="{active: contentStore.activeMode === 'text'}" @click="setInputMode('text')">
            <input type="radio" value="text" :checked="contentStore.activeMode === 'text'" name="inputModeRadio"/>
            Analyze My Text
          </label>
        </div>
        <button @click="hideInputArea" class="hide-input-button" title="Hide Input Options">
          ✖️ Hide
        </button>
      </div>

      <div v-if="contentStore.activeMode === 'youtube'" class="input-area youtube-url-area">
        <input type="text" v-model="videoUrlInput" placeholder="Enter YouTube Video URL" @keyup.enter="handleProcessVideoUrl" />
        <button @click="handleProcessVideoUrl" :disabled="isProcessingYoutube || !videoUrlInput.trim()">
          {{ isProcessingYoutube ? 'Processing...' : 'Process Video' }}
        </button>
      </div>

      <div v-if="contentStore.activeMode === 'text'" class="input-area paste-text-area">
        <input type="text" v-model="customTextTitleInput" placeholder="Title for this text (optional)" class="title-input"/>
        <textarea v-model="customTextInput" placeholder="Paste your article, notes, or any text here..." rows="10" class="text-paste-input"></textarea>
        <button @click="handleProcessPastedText" :disabled="isProcessingText || !customTextInput.trim()">
          {{ isProcessingText ? 'Processing...' : 'Process My Text' }}
        </button>
      </div>
    </div>

    <!-- Feedback Display Area from Pinia Store -->
    <div v-if="currentErrorFeedback.text && !currentLoadingState" 
        :class="['feedback-box', currentErrorFeedback.type === 'error' ? 'error-box' : 'info-box']">
      <p><strong>{{ currentErrorFeedback.type === 'error' ? 'Error' : 'Info' }}:</strong> {{ currentErrorFeedback.text }}</p>
      <p v-if="currentErrorFeedback.details" class="details-toggle" @click="showErrorDetails = !showErrorDetails">
        {{ showErrorDetails ? 'Hide' : 'Show' }} technical details
      </p>
      <p v-if="currentErrorFeedback.details && showErrorDetails" class="technical-details">
        <em>Details: {{ currentErrorFeedback.details }}</em>
      </p>
      <div v-if="props.showTranscriptPasteFallbackState" class="transcript-fallback-input-area">
        <hr class="fallback-divider">
        <p class="fallback-prompt">You can often find the transcript on YouTube (click "..." then "Show transcript") and paste it here to continue:</p>
        <textarea v-model="pastedTranscriptForFallbackInput" placeholder="Paste full transcript text here..." rows="8"></textarea>
        <button @click="handleProcessPastedFallbackTranscript" :disabled="isProcessingFallback || !pastedTranscriptForFallbackInput.trim()">
          {{ isProcessingFallback ? 'Processing...' : 'Use This Transcript' }}
        </button>
      </div>
    </div>
    
    <!-- Results Area from Pinia Store (via props from App.vue -> Notebook.vue) -->
    <div class="overview-main-content">
      <div v-if="!currentLoadingState && currentAnalysisData" class="results-area">
        <h3>Analysis Results:</h3>
        <p><strong>Status:</strong> {{ currentAnalysisData.message || (contentStore.activeMode === 'youtube' ? contentStore.youtubeData.title : contentStore.textData.title ? 'Analysis complete' : 'Ready') }}</p>
        <p v-if="currentContentIdOrTitle">
          <strong>Content ID/Title:</strong> {{ currentContentIdOrTitle }}
        </p>
        <div v-if="props.analysisForOverview">
          <h4>Table of Contents:</h4> <ul v-if="props.analysisForOverview.table_of_contents && props.analysisForOverview.table_of_contents.length > 0"><li v-for="(item, index) in props.analysisForOverview.table_of_contents" :key="'toc-'+index">{{ item.title }} <span v-if="item.timestamp_seconds !== undefined">(approx. {{ item.timestamp_seconds }}s)</span></li></ul><p v-else>No table of contents generated.</p>
          <h4>Key Terms:</h4> <ul v-if="props.analysisForOverview.key_terms && props.analysisForOverview.key_terms.length > 0"><li v-for="(item, index) in props.analysisForOverview.key_terms" :key="'term-'+index"><strong>{{ item.term }}:</strong> {{ item.definition }}</li></ul><p v-else>No key terms generated.</p>
          <h4>Logical Flow:</h4> <pre v-if="props.analysisForOverview.logical_flow">{{ props.analysisForOverview.logical_flow }}</pre><p v-else>No logical flow generated.</p>
          <h4>Summary:</h4> <p v-if="props.analysisForOverview.summary">{{ props.analysisForOverview.summary }}</p><p v-else>No summary generated.</p>
        </div>
      </div>
      <div v-else-if="!currentLoadingState && !currentAnalysisData && !currentErrorFeedback.text" class="no-results-placeholder">
        <p><i>Use the input above to process a video or analyze text.</i></p>
      </div>
      <div v-if="currentLoadingState" class="loading-spinner-container">
        <div class="spinner"></div> 
        <p>{{ currentLoadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useContentStore } from '../stores/contentStore';

const props = defineProps({
    analysisForOverview: { type: Object, default: null },
    currentTitleForOverview: { type: String, default: '' },
    isLoadingState: { type: Boolean, default: false },
    errorState: { type: Object, default: null }, 
    showTranscriptPasteFallbackState: { type: Boolean, default: false },
    currentVideoIdForFallback: { type: String, default: null },
    currentVideoUrlForFallback: { type: String, default: null },
});

const contentStore = useContentStore();

// Local component state for inputs - these will now be synced with the store
const videoUrlInput = ref('');
const customTextTitleInput = ref('');
const customTextInput = ref('');
const pastedTranscriptForFallbackInput = ref('');
    
const inputAreaVisible = ref(true);
const showErrorDetails = ref(false); 

// Computed properties to reflect Pinia state for this component's logic/UI
const isProcessingYoutube = computed(() => contentStore.activeMode === 'youtube' && contentStore.youtubeData.isLoading && !contentStore.youtubeData.showFallback);
const isProcessingText = computed(() => contentStore.activeMode === 'text' && contentStore.textData.isLoading);
const isProcessingFallback = computed(() => contentStore.activeMode === 'youtube' && contentStore.youtubeData.isLoading && contentStore.youtubeData.showFallback);
    
const currentLoadingState = computed(() => props.isLoadingState || contentStore.globalIsLoading);

const currentErrorFeedback = computed(() => {
  if (props.errorState) {
    return { 
      type: props.errorState.message && props.errorState.message.toLowerCase().includes("fetched automatically") ? 'info' : 'error',
      text: props.errorState.message, 
      details: props.errorState.details 
    };
  }
  return { text: null, type: 'info', details: '' }; // Ensure type is always defined
});
    
const currentAnalysisData = computed(() => props.analysisForOverview);

const currentContentIdOrTitle = computed(() => {
  // This prop currentTitleForOverview comes from contentStore.dataForNotebook.currentTitle
  if (contentStore.activeMode === 'youtube') {
    return contentStore.youtubeData.video_id || props.currentTitleForOverview;
  } else if (contentStore.activeMode === 'text') {
    return props.currentTitleForOverview || (contentStore.textData.id ? `Text ID: ${contentStore.textData.id}` : '');
  }
  return props.currentTitleForOverview;
});

const currentLoadingMessage = computed(() => {
  if (isProcessingFallback.value) return 'Processing Pasted Transcript...';
  if (isProcessingYoutube.value) return 'Processing Video...';
  if (isProcessingText.value) return 'Processing Text...';
  if (currentLoadingState.value) return 'Loading...'; 
  return '';
});

// Sync local inputs with store data
watch(() => contentStore.activeMode, (newMode) => {
  console.log("VideoProcessor: activeMode changed to", newMode);
  if (newMode === 'youtube') {
    videoUrlInput.value = contentStore.youtubeData.video_url || '';
  } else if (newMode === 'text') {
    customTextTitleInput.value = contentStore.textData.title || '';
    customTextInput.value = contentStore.textData.original_text || '';
  }
}, { immediate: true }); // immediate: true to run on component mount/setup

watch(() => contentStore.youtubeData.video_url, (newUrl) => {
  if (contentStore.activeMode === 'youtube') {
    videoUrlInput.value = newUrl || '';
    console.log("VideoProcessor: youtubeData.video_url changed, updated videoUrlInput to:", videoUrlInput.value);
  }
});

watch(() => contentStore.textData.title, (newTitle) => {
  if (contentStore.activeMode === 'text') {
    customTextTitleInput.value = newTitle || '';
    console.log("VideoProcessor: textData.title changed, updated customTextTitleInput to:", customTextTitleInput.value);
  }
});

watch(() => contentStore.textData.original_text, (newText) => {
  if (contentStore.activeMode === 'text') {
    customTextInput.value = newText || '';
    console.log("VideoProcessor: textData.original_text changed, updated customTextInput.");
  }
});

function setInputMode(mode) {
  console.log("VideoProcessor: setInputMode called with", mode);
  if (contentStore.activeMode !== mode) {
    contentStore.setActiveMode(mode);
  }
}

async function handleProcessVideoUrl() {
  if (!videoUrlInput.value.trim() || isProcessingYoutube.value) {
    console.warn("VideoProcessor: ProcessVideoUrl called but input empty or already processing.");
    return;
  }
  console.log("VideoProcessor: handleProcessVideoUrl with URL:", videoUrlInput.value);
  contentStore.startProcessingVideo(videoUrlInput.value);
  inputAreaVisible.value = false; 
  await sendRequestToBackend('http://localhost:5000/api/process_video', { video_url: videoUrlInput.value }, 'youtube_video');
}

async function handleProcessPastedText() {
  if (!customTextInput.value.trim() || isProcessingText.value) {
    console.warn("VideoProcessor: ProcessPastedText called but input empty or already processing.");
    return;
  }
  console.log("VideoProcessor: handleProcessPastedText with Title:", customTextTitleInput.value);
  contentStore.startProcessingText(customTextTitleInput.value.trim(), customTextInput.value); // Pass trimmed title
  inputAreaVisible.value = false;
  await sendRequestToBackend('http://localhost:5000/api/process_custom_text', { 
    custom_text: customTextInput.value,
    title: customTextTitleInput.value.trim() || 'Custom Text Analysis' 
  }, 'custom_text');
}

async function handleProcessPastedFallbackTranscript() {
  if (!pastedTranscriptForFallbackInput.value.trim() || isProcessingFallback.value) return;
  console.log("VideoProcessor: handleProcessPastedFallbackTranscript for videoId:", props.currentVideoIdForFallback);
  contentStore.startProcessingFallbackTranscript(); 
  await sendRequestToBackend('http://localhost:5000/api/process_video_with_custom_transcript', { 
    video_id: props.currentVideoIdForFallback, 
    video_url: props.currentVideoUrlForFallback, 
    custom_transcript_text: pastedTranscriptForFallbackInput.value,
  }, 'youtube_video'); 
}

async function sendRequestToBackend(endpoint, payload, source) {
  // This function remains as it was, making sure it calls
  // contentStore.setProcessedData or contentStore.setProcessingError
  // based on the outcome.
  console.log(`VideoProcessor: sendRequestToBackend. Endpoint: ${endpoint}, Source: ${source}`);
  try {
    const response = await fetch(endpoint, { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, 
      body: JSON.stringify(payload) 
    });
    const rawText = await response.text();
    let data;
    try { data = JSON.parse(rawText); } 
    catch (e) {
      console.error("VideoProcessor: Failed to parse server response:", rawText);
      contentStore.setProcessingError(source, { 
        error: "Failed to parse server response.", 
        details: `Server response was not valid JSON. Status: ${response.status}`
      });
      if (source !== 'youtube_video_fallback') inputAreaVisible.value = true;
      return; 
    }

    if (!response.ok) {
      console.error(`VideoProcessor: Server error ${response.status} for ${source}:`, data);
      let errorData = {
        error: data.error || `Server error (${response.status})`,
        details: data.details || JSON.stringify(data),
        video_id: data.video_id, 
        video_url: data.video_url, 
        // Logic for showing fallback is now primarily in the store based on error from backend
        showFallback: source === 'youtube_video' && data.video_id && (response.status === 422 || (data.error && data.error.toLowerCase().includes("transcript"))),
      };
      contentStore.setProcessingError(source, errorData);
      if (!errorData.showFallback) { // If not showing fallback, make input visible again
        inputAreaVisible.value = true;
      }
    } else { 
      console.log(`VideoProcessor: Success for ${source}:`, data);
      if (source === 'youtube_video' && contentStore.youtubeData.showFallback) {
          contentStore.clearFallbackState(); // Clear fallback state on successful processing
      }
      // Ensure original_text is passed for custom_text source if store needs it from here
      const processedPayload = source === 'custom_text' ? { ...data, original_text: payload.custom_text } : data;
      contentStore.setProcessedData(source, processedPayload);
      // inputAreaVisible.value = false; // Keep this commented if we want inputs to stay visible after success
    }
  } catch (e) {
    console.error(`VideoProcessor: Network or client-side error for ${source}:`, e);
    contentStore.setProcessingError(source, { error: 'Network error or failed to connect.', details: e.message });
    inputAreaVisible.value = true; 
  }
}
    
const revealInputArea = () => { inputAreaVisible.value = true; };
const hideInputArea = () => { inputAreaVisible.value = false; };

// Initial sync of inputs on component setup if mode is already set
// (Handled by immediate:true on activeMode watcher)
</script>


<style scoped>
/* STYLES REMAIN THE SAME */
.video-processor { width: 100%; flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; margin:0; padding:0; text-align:left; box-sizing: border-box;}
.main-title-container { display: flex; justify-content: space-between; align-items: center; padding: 0 0 10px 0; margin: 0 0 0.75em 0; border-bottom: 1px solid #eee; flex-shrink: 0; }
.main-title-container h2 { font-size: 1.5em; font-weight: 600; color: var(--color-heading); margin:0; text-align: left; }
.reopen-input-button { padding: 6px 12px; font-size: 0.85em; border: 1px solid #6c757d; background-color: #f8f9fa; color: #495057; border-radius: 5px; cursor: pointer; margin-left: auto; flex-shrink: 0; font-weight: 500;}
.reopen-input-button:hover { background-color: #e9ecef; }
.input-section-wrapper { flex-shrink: 0; margin-bottom: 15px; }
.input-controls-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.input-mode-selector { display: flex; justify-content: center; gap: 15px; padding: 0; flex-grow: 1; justify-content: center; }
.input-mode-selector label { cursor: pointer; font-size: 0.95em; padding: 6px 12px; border: 1px solid transparent; border-radius: 6px; transition: background-color 0.2s, border-color 0.2s; }
.input-mode-selector input[type="radio"] { margin-right: 6px; vertical-align: middle; }
.input-mode-selector label.active { background-color: #e0eef8; border-color: #b4d7f0; font-weight: 500; }
.input-mode-selector label:not(.active):hover { background-color: #f0f0f0; }
.hide-input-button { padding: 4px 8px; font-size: 0.9em; border: 1px solid #adb5bd; background-color: #f8f9fa; color: #495057; border-radius: 4px; cursor: pointer; margin-left: 10px; flex-shrink: 0;}
.hide-input-button:hover { background-color: #e2e6ea; }
.input-area { display: flex; gap: 10px; padding: 15px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; flex-shrink: 0; }
.youtube-url-area { flex-direction: row; align-items: center; }
.youtube-url-area input { flex-grow: 1; padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; }
.paste-text-area { flex-direction: column; }
.title-input { padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; font-size: 1em; margin-bottom:10px; }
.text-paste-input { padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; font-size: 0.95em; min-height: 120px; resize: vertical; font-family: 'Menlo', 'Consolas', monospace; }
.input-area button { padding: .375rem .75rem; font-size: 1rem; line-height: 1.5; border-radius: .25rem; color: white; border: none; cursor: pointer; font-weight: 500; transition: background-color .15s ease-in-out; }
.youtube-url-area button { background-color: #28a745; } .youtube-url-area button:hover { background-color: #218838; }
.paste-text-area button { background-color: #007bff; align-self: flex-end; margin-top: 5px; } .paste-text-area button:hover { background-color: #0069d9; }
.input-area button:disabled { background-color: #6c757d; }
.feedback-box { padding: 1rem; margin:0 0 15px 0; border-radius: .25rem; font-size: 0.95em; flex-shrink: 0;}
.feedback-box p { margin: 0 0 0.5rem 0; } .feedback-box p:last-child { margin-bottom: 0;} .feedback-box strong { font-weight: 600;}
.error-box { color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; }
.info-box { color: #0c5460; background-color: #d1ecf1; border: 1px solid #bee5eb; }
.details-toggle { font-size: 0.85em; color: #0056b3; cursor: pointer; text-decoration: underline; margin-top: 5px !important; }
.technical-details { font-size: 0.8em; color: #555; background-color: #f9f9f9; border: 1px dashed #ddd; padding: 8px; margin-top: 8px !important; border-radius: 4px; max-height: 100px; overflow-y: auto; word-break: break-all;}
.transcript-fallback-input-area { margin-top: 1rem; padding-top: 1rem; }
.fallback-divider { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(12, 84, 96, 0.3), rgba(0, 0, 0, 0)); margin-bottom: 1rem; }
.fallback-prompt { font-weight: 500; margin-bottom: .5rem; font-size: 0.95em; }
.transcript-fallback-input-area textarea { width: 100%; box-sizing: border-box; min-height: 100px; padding: 8px; border: 1px solid #ced4da; border-radius: .25rem; margin-bottom: 10px; font-family: 'Menlo', 'Consolas', monospace; font-size: 0.9em; }
.transcript-fallback-input-area button { display: block; margin-left: auto; padding: .375rem .75rem; background-color: #0069d9; color: white; }
.transcript-fallback-input-area button:hover { background-color: #0056b3; } .transcript-fallback-input-area button:disabled { background-color: #aaa; }
.overview-main-content { display: flex; flex-direction: column; flex-grow: 1; min-height: 0; overflow: hidden; position: relative; }
.results-area { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; padding: 15px 25px; background-color: #fff; font-size: 16px; line-height: 1.7; color: #333; }
.no-results-placeholder { position: absolute; top:0; left:0; right:0; bottom:0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px; font-style: italic; background-color: #fff; }
.loading-spinner-container { position: absolute; top:0; left:0; right:0; bottom:0; display:flex; flex-direction: column; align-items: center; justify-content: center; background-color: rgba(255,255,255,0.8); z-index: 10;}
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom:10px;}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.results-area h3, .results-area h4 { margin-top: 1.5em; margin-bottom: 0.6em; color: var(--color-heading); font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
.results-area h3:first-of-type { margin-top: 0; } .results-area p { margin-bottom: 0.75em; }
.results-area ul { list-style-type: disc; padding-left: 25px; margin-bottom: 1em; }
.results-area li { margin-bottom: 0.5em; } .results-area li strong { color: #1a1a1a; font-weight: 600; }
.results-area pre { white-space: pre-wrap; word-wrap: break-word; background-color: #fdfdfd; padding: 15px; border: 1px solid #eee; font-family: 'Courier New', Courier, monospace; font-size: 0.95em; line-height: 1.6; border-radius: 4px; margin-bottom: 1em; color: #222; }
</style>
<!-- END FILE: frontend_learn_tube_ai\learn_tube_ai\src\components\VideoProcessor.vue --- REFACTORED FOR PINIA -->