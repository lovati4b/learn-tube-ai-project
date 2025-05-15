<!-- FILE: src/components/VideoProcessor.vue - FULL CONTENT, MYNOTES-STYLE LAYOUT -->
<template>
  <div class="video-processor"> <!-- Root: flex-grow:1 -->
    <h2>Learn From Video</h2>
    <div class="input-area"> <!-- Fixed header -->
      <input type="text" v-model="videoUrl" placeholder="Enter YouTube Video URL" />
      <button @click="processVideo" :disabled="isLoading">
        {{ isLoading ? 'Processing...' : 'Process Video' }}
      </button>
    </div>
    <div v-if="error" class="error-message"> <!-- Fixed header -->
      <p>Error: {{ error }}</p>
      <p v-if="errorDetails">Details: {{ errorDetails }}</p>
    </div>
    
    <!-- This div will now be the main content area that grows -->
    <div class="overview-main-content">
      <div v-if="analysisResult" class="results-area"> <!-- This div scrolls -->
        <h3>Analysis Results:</h3>
        <p><strong>Status:</strong> {{ analysisResult.message }} ({{ analysisResult.status }})</p>
        <p><strong>Video ID:</strong> {{ analysisResult.video_id || analysisResult.video_url }}</p>
        
        <div v-if="analysisResult.analysis">
          <h4>Table of Contents:</h4>
          <ul v-if="analysisResult.analysis.table_of_contents && analysisResult.analysis.table_of_contents.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.table_of_contents" :key="index">
              {{ item.title }} (approx. {{ item.timestamp_seconds }}s)
            </li>
          </ul>
          <p v-else>No table of contents generated.</p>

          <h4>Key Terms:</h4>
          <ul v-if="analysisResult.analysis.key_terms && analysisResult.analysis.key_terms.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.key_terms" :key="index">
              <strong>{{ item.term }}:</strong> {{ item.definition }}
            </li>
          </ul>
          <p v-else>No key terms generated.</p>

          <h4>Logical Flow:</h4>
          <pre v-if="analysisResult.analysis.logical_flow">{{ analysisResult.analysis.logical_flow }}</pre>
          <p v-else>No logical flow generated.</p>

          <!-- Duplicate for testing scroll -->
          <h4>COPY: Table of Contents:</h4>
          <ul v-if="analysisResult.analysis.table_of_contents && analysisResult.analysis.table_of_contents.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.table_of_contents" :key="index">
              {{ item.title }} (approx. {{ item.timestamp_seconds }}s) [COPY]
            </li>
          </ul>
          <p v-else>No table of contents generated. [COPY]</p>
          <h4>COPY: Key Terms:</h4>
          <ul v-if="analysisResult.analysis.key_terms && analysisResult.analysis.key_terms.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.key_terms" :key="index">
              <strong>{{ item.term }}:</strong> {{ item.definition }} [COPY]
            </li>
          </ul>
          <p v-else>No key terms generated. [COPY]</p>
          <h4>COPY: Logical Flow:</h4>
          <pre v-if="analysisResult.analysis.logical_flow">{{ analysisResult.analysis.logical_flow }} [COPY]</pre>
          <p v-else>No logical flow generated. [COPY]</p>
        </div>
      </div>
      <div v-else-if="!isLoading && !error" class="no-results-placeholder">
         <p><i>Process a video to see results here.</i></p>
      </div>
    </div>
  </div>
</template>

<script>
// Using your provided full script
export default {
  name: 'VideoProcessor',
  data() {
    return {
      videoUrl: '',
      analysisResult: null,
      isLoading: false,
      error: null,
      errorDetails: null,
    };
  },
  methods: {
    async processVideo() {
      console.log("processVideo method called. URL:", this.videoUrl);
      if (!this.videoUrl.trim()) {
        this.error = 'Please enter a YouTube Video URL.';
        this.errorDetails = null; this.analysisResult = null;
        return;
      }
      this.isLoading = true; this.analysisResult = null; this.error = null; this.errorDetails = null;
      try {
        const response = await fetch('http://localhost:5000/api/process_video', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', },
          body: JSON.stringify({ video_url: this.videoUrl }),
        });
        const rawText = await response.text();
        let data;
        try { data = JSON.parse(rawText); } catch (e) {
          this.error = "Failed to parse server response."; this.errorDetails = `Server sent: ${rawText.substring(0, 200)}...`;
          this.analysisResult = null; this.isLoading = false; return;
        }
        if (!response.ok) {
          this.error = data.error || `Server error: ${response.status}`;
          this.errorDetails = data.details || (typeof data.message === 'string' ? data.message : JSON.stringify(data));
          this.analysisResult = null;
        } else {
          this.analysisResult = data; this.error = null; this.errorDetails = null;
        }
      } catch (e) {
        this.error = 'Failed to connect to the server or network error.'; this.errorDetails = e.message;
        this.analysisResult = null;
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped>
.video-processor { /* Root */
  width: 100%; 
  flex-grow: 1; 
  margin: 0;   
  padding: 0; 
  text-align: left; 
  box-sizing: border-box; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden; 
  min-height: 0; 
}
.video-processor > h2 { /* Fixed header */
  padding: 0 0 10px 0; 
  margin: 0 0 0.75em 0; 
  font-size: 1.5em; 
  font-weight: 600;
  color: var(--color-heading);
  border-bottom: 1px solid #eee;
  flex-shrink:0;
}
.input-area { /* Fixed header */
  display: flex; gap: 10px; margin-bottom: 15px; padding: 15px; 
  background-color: #f9f9f9; border-bottom: 1px solid #eee; flex-shrink: 0; 
}
.input-area input { flex-grow: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
.input-area button { padding: 10px 15px; background-color: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; }
.input-area button:disabled { background-color: #aaa; cursor: not-allowed; }

.error-message { /* Fixed header */
  color: red; background-color: #ffe0e0; border: 1px solid red; 
  padding: 10px 15px; margin-bottom:15px; border-radius: 4px; flex-shrink: 0; 
}
.error-message p { margin: 0; }
.error-message p + p { margin-top: 5px; }

.overview-main-content { /* NEW: This div will grow, like .notes-editor-container */
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden; /* It clips the .results-area if necessary */
  /* background-color: #e6ffe6; */ /* Optional: for debugging bounds */
}

.results-area { /* This div scrolls */
  flex-grow: 1; /* Grows within .overview-main-content */
  overflow-y: auto;
  min-height: 0; 
  padding: 15px 25px; 
  background-color: #fff; 
  font-size: 16px; 
  line-height: 1.7; 
  color: #333; 
}
/* Rest of .results-area child styles are the same */
.results-area h3, .results-area h4 { margin-top: 1.5em; margin-bottom: 0.6em; color: var(--color-heading); font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
.results-area h3:first-of-type { margin-top: 0; }
.results-area p { margin-bottom: 0.75em; }
.results-area ul { list-style-type: disc; padding-left: 25px; margin-bottom: 1em; }
.results-area li { margin-bottom: 0.5em; }
.results-area li strong { color: #1a1a1a; font-weight: 600; }
.results-area pre { white-space: pre-wrap; word-wrap: break-word; background-color: #fdfdfd; padding: 15px; border: 1px solid #eee; font-family: 'Courier New', Courier, monospace; font-size: 0.95em; line-height: 1.6; border-radius: 4px; margin-bottom: 1em; color: #222; }

.no-results-placeholder {
    flex-grow: 1; 
    display: flex; 
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 0; 
    text-align: center;
    color: #888;
    padding: 20px;
    font-style: italic;
}
</style>