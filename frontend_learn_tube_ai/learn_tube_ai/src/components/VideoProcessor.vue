<!-- FILE: src/components/VideoProcessor.vue - IMPROVED ERROR/FALLBACK & PASTE TEXT MODE -->
<template>
  <div class="video-processor">
    <h2>Learn From Video / Analyze Text</h2>

    <div class="input-mode-selector" v-if="!showTranscriptPasteFallback">
      <label :class="{active: inputMode === 'youtube'}">
        <input type="radio" value="youtube" v-model="inputMode" @change="clearPrimaryError" />
        YouTube URL
      </label>
      <label :class="{active: inputMode === 'text'}">
        <input type="radio" value="text" v-model="inputMode" @change="clearPrimaryError" />
        Analyze My Text
      </label>
    </div>

    <!-- YouTube URL Input -->
    <div v-if="inputMode === 'youtube' && !showTranscriptPasteFallback" class="input-area youtube-url-area">
      <input type="text" v-model="videoUrl" placeholder="Enter YouTube Video URL" @keyup.enter="processVideoUrl" />
      <button @click="processVideoUrl" :disabled="isLoading || !videoUrl.trim()">
        {{ isLoading && currentOperation === 'video' ? 'Processing Video...' : 'Process Video' }}
      </button>
    </div>

    <!-- General Paste Text Input -->
    <div v-if="inputMode === 'text' && !showTranscriptPasteFallback" class="input-area paste-text-area">
      <input type="text" v-model="customTextTitle" placeholder="Title for this text (optional)" class="title-input"/>
      <textarea v-model="customText" placeholder="Paste your article, notes, or any text here..." rows="10" class="text-paste-input"></textarea>
      <button @click="processPastedText" :disabled="isLoading || !customText.trim()">
        {{ isLoading && currentOperation === 'text' ? 'Processing...' : 'Process My Text' }}
      </button>
    </div>

    <!-- Feedback Display Area (Error or Fallback Prompt) -->
    <div v-if="feedbackMessage.text && !isLoading" 
         :class="['feedback-box', feedbackMessage.type === 'error' ? 'error-box' : 'info-box']">
      <p><strong>{{ feedbackMessage.type === 'error' ? 'Error' : 'Info' }}:</strong> {{ feedbackMessage.text }}</p>
      <p v-if="feedbackMessage.details" class="details-toggle" @click="showErrorDetails = !showErrorDetails">
        {{ showErrorDetails ? 'Hide' : 'Show' }} technical details
      </p>
      <p v-if="feedbackMessage.details && showErrorDetails" class="technical-details">
        <em>Details: {{ feedbackMessage.details }}</em>
      </p>
      
      <div v-if="showTranscriptPasteFallback" class="transcript-fallback-input-area">
        <hr class="fallback-divider">
        <p class="fallback-prompt">You can often find the transcript on YouTube (click "..." then "Show transcript") and paste it here to continue:</p>
        <textarea v-model="pastedTranscriptForFallback" placeholder="Paste full transcript text here..." rows="8"></textarea>
        <button @click="processPastedFallbackTranscript" :disabled="isLoadingPastingTranscript || !pastedTranscriptForFallback.trim()">
          {{ isLoadingPastingTranscript ? 'Processing...' : 'Use This Transcript' }}
        </button>
      </div>
    </div>
    
    <!-- Results Area -->
    <div class="overview-main-content">
      <div v-if="analysisResult && !feedbackMessage.text" class="results-area"> <!-- Hide results if there's feedback -->
        <h3>Analysis Results:</h3>
        <p><strong>Status:</strong> {{ analysisResult.message }}</p>
        <p v-if="analysisResult.video_id || (analysisResult.title && inputModeUsedForLastSuccess === 'text')">
          <strong>Content ID/Title:</strong> {{ analysisResult.video_id || analysisResult.title }}
        </p>
        <div v-if="analysisResult.analysis">
          <!-- ... (Table of Contents, Key Terms, etc. - same as before) ... -->
          <h4>Table of Contents:</h4>
          <ul v-if="analysisResult.analysis.table_of_contents && analysisResult.analysis.table_of_contents.length > 0"><li v-for="(item, index) in analysisResult.analysis.table_of_contents" :key="'toc-'+index">{{ item.title }} <span v-if="item.timestamp_seconds !== undefined">(approx. {{ item.timestamp_seconds }}s)</span></li></ul><p v-else>No table of contents generated.</p>
          <h4>Key Terms:</h4>
          <ul v-if="analysisResult.analysis.key_terms && analysisResult.analysis.key_terms.length > 0"><li v-for="(item, index) in analysisResult.analysis.key_terms" :key="'term-'+index"><strong>{{ item.term }}:</strong> {{ item.definition }}</li></ul><p v-else>No key terms generated.</p>
          <h4>Logical Flow:</h4>
          <pre v-if="analysisResult.analysis.logical_flow">{{ analysisResult.analysis.logical_flow }}</pre><p v-else>No logical flow generated.</p>
          <h4>Summary:</h4>
          <p v-if="analysisResult.analysis.summary">{{ analysisResult.analysis.summary }}</p><p v-else>No summary generated.</p>
        </div>
      </div>
      <div v-else-if="!isLoading && !analysisResult && !feedbackMessage.text" class="no-results-placeholder">
         <p><i>{{ inputMode === 'youtube' ? 'Process a video' : 'Analyze text' }} to see results here.</i></p>
      </div>
       <div v-if="isLoading" class="loading-spinner-container">
        <div class="spinner"></div> 
        <p>{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoProcessor',
  emits: ['video-processed'], 
  data() {
    return {
      inputMode: 'youtube', 
      videoUrl: '', 
      videoUrlForFallback: '', 
      videoIdForFallback: '',  
      customText: '',
      customTextTitle: '',
      pastedTranscriptForFallback: '',
      analysisResult: null, 
      isLoading: false,
      isLoadingPastingTranscript: false, 
      
      feedbackMessage: { type: '', text: '', details: '' }, // Consolidated feedback
      showErrorDetails: false, // For toggling technical details

      showTranscriptPasteFallback: false, 
      currentOperation: '', 
      inputModeUsedForLastSuccess: 'youtube',
    };
  },
  computed: {
      loadingMessage() { /* ... same as before ... */ }
  },
  methods: {
    clearPrimaryErrorAndResults() { // More descriptive name
      this.feedbackMessage = { type: '', text: '', details: '' };
      this.showErrorDetails = false;
      this.analysisResult = null;
      this.showTranscriptPasteFallback = false;
      this.videoUrlForFallback = '';
      this.videoIdForFallback = '';
      this.pastedTranscriptForFallback = '';
      // Clear results for App.vue as well if mode changes significantly
      this.$emit('video-processed', { isLoading: false, video_id: '', transcript_text:'', segments:[], analysis: null});
    },
    async processVideoUrl() {
      if (!this.videoUrl.trim()) {
        this.feedbackMessage = { type: 'error', text: 'Please enter a YouTube Video URL.', details: '' };
        this.showTranscriptPasteFallback = false;
        this.$emit('video-processed', { video_id: '', error: this.feedbackMessage.text, transcript_text: '', segments: [] });
        return;
      }
      this.currentOperation = 'video';
      await this.sendRequest('http://localhost:5000/api/process_video', { video_url: this.videoUrl });
    },
    async processPastedText() {
      if (!this.customText.trim()) {
        this.feedbackMessage = { type: 'error', text: 'Please paste some text to analyze.', details: '' };
        this.showTranscriptPasteFallback = false;
        this.$emit('video-processed', { video_id: this.customTextTitle || 'custom_text', error: this.feedbackMessage.text, transcript_text: '', segments: [] });
        return;
      }
      this.currentOperation = 'text';
      await this.sendRequest('http://localhost:5000/api/process_custom_text', { 
        custom_text: this.customText,
        title: this.customTextTitle.trim() || 'Custom Text Analysis' 
      });
    },
    async processPastedFallbackTranscript() {
      if (!this.pastedTranscriptForFallback.trim()) {
        // Keep existing feedback message, just update details if needed
        this.feedbackMessage.details = (this.feedbackMessage.details || '') + "\nAttempted to use fallback with empty text.";
        return;
      }
      this.currentOperation = 'fallback';
      this.isLoadingPastingTranscript = true; 
      await this.sendRequest('http://localhost:5000/api/process_video_with_custom_transcript', { 
        video_id: this.videoIdForFallback,
        video_url: this.videoUrlForFallback,
        custom_transcript_text: this.pastedTranscriptForFallback,
      }, true); 
      this.isLoadingPastingTranscript = false;
    },
    async sendRequest(endpoint, payload, isFallback = false) {
      this.isLoading = !isFallback; 
      this.analysisResult = null;
      this.feedbackMessage = { type: '', text: '', details: '' }; // Clear previous feedback
      this.showErrorDetails = false;

      if (!isFallback) {
          this.showTranscriptPasteFallback = false; 
          this.videoUrlForFallback = ''; this.videoIdForFallback = '';
      }
      
      this.$emit('video-processed', { isLoading: true, video_id: payload.video_id || (this.inputMode === 'youtube' ? this.videoUrl : (payload.title || '')) });

      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(payload),
        });
        const rawText = await response.text();
        let data;
        try { data = JSON.parse(rawText); } catch (e) {
          this.feedbackMessage = { type: 'error', text: "Failed to parse server response.", details: `The server's response was not in the expected JSON format.`};
          this.$emit('video-processed', { error: this.feedbackMessage.text, details: this.feedbackMessage.details, video_id: payload.video_id });
          return; 
        }

        if (!response.ok) {
          this.feedbackMessage = { type: 'error', text: data.error || `Server error: ${response.status}`, details: data.details || JSON.stringify(data) };
          
          if (this.inputMode === 'youtube' && !isFallback && data.video_id && (response.status === 422 || data.error?.toLowerCase().includes("transcript"))) {
            this.showTranscriptPasteFallback = true;
            this.videoUrlForFallback = payload.video_url; 
            this.videoIdForFallback = data.video_id;
            this.pastedTranscriptForFallback = ''; 
            // Change feedback type to 'info' for the fallback prompt
            this.feedbackMessage.type = 'info';
            this.feedbackMessage.text = `Transcript for video ID '${data.video_id}' could not be fetched automatically.`;
            // Emit current error state but also indicate fallback is available
            this.$emit('video-processed', { ...data, ...this.feedbackMessage, showFallback: true, transcript_text:'', segments:[] });
          } else {
             this.$emit('video-processed', { ...data, ...this.feedbackMessage, transcript_text: (this.inputMode === 'text' ? payload.custom_text : ''), segments:[] });
          }
        } else {
          this.analysisResult = data;
          this.inputModeUsedForLastSuccess = data.video_id?.includes("custom_") || data.title && this.inputMode === 'text' ? 'text' : 'youtube';
          if (isFallback) { this.showTranscriptPasteFallback = false; } // Hide fallback on success
          this.$emit('video-processed', this.analysisResult);
        }
      } catch (e) {
        this.feedbackMessage = { type: 'error', text: 'Failed to connect to the server or network error.', details: e.message };
        this.$emit('video-processed', { ...this.feedbackMessage, video_id: payload.video_id });
      } finally {
        this.isLoading = false;
        if (isFallback) this.isLoadingPastingTranscript = false;
      }
    }
  },
  watch: {
      inputMode(newMode, oldMode) {
          if (newMode !== oldMode) {
              this.clearPrimaryErrorAndResults();
          }
      }
  }
};
</script>

<style scoped>
/* Root style, h2, overview-main-content, results-area, loading styles are same */
.video-processor { width: 100%; flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; margin:0; padding:0; text-align:left; box-sizing: border-box;}
.video-processor > h2 { flex-shrink: 0; padding: 0 0 10px 0; margin: 0 0 0.75em 0; font-size: 1.5em; font-weight: 600; color: var(--color-heading); border-bottom: 1px solid #eee; text-align: center;}

.input-mode-selector { display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; padding: 8px 0; flex-shrink: 0; /* border-bottom: 1px solid #eee; */ }
.input-mode-selector label { cursor: pointer; font-size: 0.95em; padding: 6px 12px; border: 1px solid transparent; border-radius: 6px; transition: background-color 0.2s, border-color 0.2s; }
.input-mode-selector input[type="radio"] { margin-right: 6px; vertical-align: middle; }
.input-mode-selector label.active { background-color: #e0eef8; border-color: #b4d7f0; font-weight: 500; }
.input-mode-selector label:not(.active):hover { background-color: #f0f0f0; }


.input-area { display: flex; gap: 10px; margin-bottom: 15px; padding: 15px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; flex-shrink: 0; }
.youtube-url-area { flex-direction: row; align-items: center; }
.youtube-url-area input { flex-grow: 1; padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; } /* Bootstrap-like */
.paste-text-area { flex-direction: column; }
.title-input { padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; font-size: 1em; margin-bottom:10px; }
.text-paste-input { padding: 10px; border: 1px solid #ced4da; border-radius: .25rem; font-size: 0.95em; min-height: 120px; resize: vertical; font-family: 'Menlo', 'Consolas', monospace; }

.input-area button { 
  padding: .375rem .75rem; /* Bootstrap-like padding */
  font-size: 1rem;
  line-height: 1.5;
  border-radius: .25rem;
  color: white; 
  border: none; 
  cursor: pointer; 
  font-weight: 500;
  transition: background-color .15s ease-in-out;
}
.youtube-url-area button { background-color: #28a745; /* Green */ }
.youtube-url-area button:hover { background-color: #218838; }
.paste-text-area button { background-color: #007bff; /* Blue */ align-self: flex-end; margin-top: 5px; }
.paste-text-area button:hover { background-color: #0069d9; }
.input-area button:disabled { background-color: #6c757d; /* Grey */ }


.feedback-box { /* Common styling for error and info boxes */
  padding: 1rem;
  margin:0 0 15px 0; 
  border-radius: .25rem;
  font-size: 0.95em;
  flex-shrink: 0;
}
.feedback-box p { margin: 0 0 0.5rem 0; } 
.feedback-box p:last-child { margin-bottom: 0;}
.feedback-box strong { font-weight: 600;}

.error-box { /* Specific for actual errors */
  color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; 
}
.info-box { /* For transcript fallback prompt */
  color: #0c5460; background-color: #d1ecf1; border: 1px solid #bee5eb;
}

.details-toggle {
  font-size: 0.85em;
  color: #0056b3; /* Link-like color */
  cursor: pointer;
  text-decoration: underline;
  margin-top: 5px !important; /* Ensure spacing */
}
.technical-details {
  font-size: 0.8em;
  color: #555;
  background-color: #f9f9f9;
  border: 1px dashed #ddd;
  padding: 8px;
  margin-top: 8px !important;
  border-radius: 4px;
  max-height: 100px;
  overflow-y: auto;
  word-break: break-all;
}

.transcript-fallback-input-area { margin-top: 1rem; padding-top: 1rem; }
.fallback-divider { border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(12, 84, 96, 0.3), rgba(0, 0, 0, 0)); margin-bottom: 1rem; }
.fallback-prompt { font-weight: 500; margin-bottom: .5rem; font-size: 0.95em; }
.transcript-fallback-input-area textarea { width: 100%; box-sizing: border-box; min-height: 100px; padding: 8px; border: 1px solid #ced4da; border-radius: .25rem; margin-bottom: 10px; font-family: 'Menlo', 'Consolas', monospace; font-size: 0.9em; }
.transcript-fallback-input-area button { display: block; margin-left: auto; padding: .375rem .75rem; background-color: #0069d9; /* Darker blue for this action */ color: white; }
.transcript-fallback-input-area button:hover { background-color: #0056b3; }
.transcript-fallback-input-area button:disabled { background-color: #aaa; }


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