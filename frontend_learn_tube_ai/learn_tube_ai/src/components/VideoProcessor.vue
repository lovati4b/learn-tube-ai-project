<!-- FILE: src/components/VideoProcessor.vue - PHASE 1 CHANGES -->
<template>
  <div class="video-processor">
    <h2>Learn From Video</h2>
    <div class="input-area">
      <input type="text" v-model="videoUrl" placeholder="Enter YouTube Video URL" />
      <button @click="processVideo" :disabled="isLoading">
        {{ isLoading ? 'Processing...' : 'Process Video' }}
      </button>
    </div>
    <div v-if="error" class="error-message">
      <p>Error: {{ error }}</p>
      <p v-if="errorDetails">Details: {{ errorDetails }}</p>
    </div>
    
    <div class="overview-main-content">
      <div v-if="analysisResult" class="results-area">
        <h3>Analysis Results:</h3>
        <p><strong>Status:</strong> {{ analysisResult.message }} ({{ analysisResult.status }})</p>
        <p><strong>Video ID:</strong> {{ analysisResult.video_id || analysisResult.video_url }}</p>
        <div v-if="analysisResult.analysis">
          <h4>Table of Contents:</h4>
          <ul v-if="analysisResult.analysis.table_of_contents && analysisResult.analysis.table_of_contents.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.table_of_contents" :key="'toc-'+index">
              {{ item.title }} (approx. {{ item.timestamp_seconds }}s)
            </li>
          </ul> <p v-else>No table of contents generated.</p>
          <h4>Key Terms:</h4>
          <ul v-if="analysisResult.analysis.key_terms && analysisResult.analysis.key_terms.length > 0">
            <li v-for="(item, index) in analysisResult.analysis.key_terms" :key="'term-'+index">
              <strong>{{ item.term }}:</strong> {{ item.definition }}
            </li>
          </ul> <p v-else>No key terms generated.</p>
          <h4>Logical Flow:</h4>
          <pre v-if="analysisResult.analysis.logical_flow">{{ analysisResult.analysis.logical_flow }}</pre>
          <p v-else>No logical flow generated.</p>
          
          <!-- Removed duplicated COPY content for cleaner default view -->
        </div>
      </div>
      <div v-else-if="!isLoading && !error" class="no-results-placeholder">
         <p><i>Process a video to see results here.</i></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoProcessor',
  data() {
    return {
      videoUrl: '', // Point #6: Default to empty
      analysisResult: null, // Point #7: Default to null
      isLoading: false,
      error: null,
      errorDetails: null,
      // Keep your extensive mock data for analysisResult commented out here if you want for quick testing
      /*
      analysisResult_MOCK: { 
          message: "Mock data for layout testing", status: 200, video_id: "mockID_SB", 
          analysis: {
              table_of_contents: Array(20).fill(null).map((_,i) => ({title: `Mock Table of Contents Item ${i+1} - This title is made longer to ensure it wraps and contributes to the overall height of the list.`, timestamp_seconds: i*10})),
              key_terms: Array(15).fill(null).map((_,i) => ({term: `Mock Key Term ${i+1}`, definition: `This is a detailed mock definition for the key term number ${i+1}. We need this definition to be sufficiently long, perhaps spanning multiple lines, to adequately test the scrolling behavior of the results area when many such key terms and their comprehensive definitions are displayed. This helps ensure that the overflow-y: auto property is triggered correctly, demonstrating the layout solution.`})),
              logical_flow: "This is the beginning of a very long mock logical flow. It's designed to be extensive enough to absolutely require scrolling within its designated container. ".repeat(30) + 
                            "\n\nParagraph breaks are included to further simulate real content structure. Each paragraph adds to the total scrollable height. The goal is to verify that the 'results-scroll-area' div, styled with 'overflow-y: auto' and appropriate flex properties (or absolute positioning as per our last fix), correctly activates its scrollbar when this content exceeds its allocated viewport. ".repeat(15) + 
                            "\n\nIf scrolling works here, and also in the 'Ask AI' and 'My Notes' tabs, then the core layout issues concerning dynamic content height and scrolling are resolved. This specific mock data for VideoProcessor aims to be unambiguously taller than any reasonable screen height for the results area. ".repeat(10) + 
                            "End of the verbose mock logical flow."
          }
      },
      */
    };
  },
  methods: { /* ... Your full working processVideo method ... */ 
    async processVideo() {
      // (Keep your full processVideo method here as it was when working)
      console.log("processVideo method called. URL:", this.videoUrl);
      if (!this.videoUrl.trim()) { this.error = 'Please enter a YouTube Video URL.'; /*...*/ return; }
      this.isLoading = true; this.analysisResult = null; this.error = null; this.errorDetails = null;
      try {
        const response = await fetch('http://localhost:5000/api/process_video', {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', },
          body: JSON.stringify({ video_url: this.videoUrl }),
        });
        const rawText = await response.text(); let data;
        try { data = JSON.parse(rawText); } catch (e) {
          this.error = "Failed to parse server response."; this.errorDetails = `Server sent: ${rawText.substring(0, 200)}...`;
          this.isLoading = false; return;
        }
        if (!response.ok) {
          this.error = data.error || `Server error: ${response.status}`;
          this.errorDetails = data.details || (typeof data.message === 'string' ? data.message : JSON.stringify(data));
        } else { this.analysisResult = data; }
      } catch (e) {
        this.error = 'Failed to connect to the server or network error.'; this.errorDetails = e.message;
      } finally { this.isLoading = false; }
    }
  },
};
</script>

<style scoped>
/* Styles are the same as the last version where VideoProcessor page layout was working */
.video-processor { display: flex; flex-direction: column; flex-grow: 1; min-height: 0; overflow: hidden; width: 100%; margin: 0; padding: 0; text-align: left; box-sizing: border-box;}
.video-processor > h2 { flex-shrink: 0; padding: 0 0 10px 0; margin: 0 0 0.75em 0; font-size: 1.5em; font-weight: 600; color: var(--color-heading); border-bottom: 1px solid #eee;}
.input-area { flex-shrink: 0; display: flex; gap: 10px; margin-bottom: 15px; padding: 15px; background-color: #f9f9f9; border-bottom: 1px solid #eee;}
.input-area input { flex-grow: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
.input-area button { padding: 10px 15px; background-color: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; }
.input-area button:disabled { background-color: #aaa; cursor: not-allowed; }
.error-message { flex-shrink: 0; color: red; background-color: #ffe0e0; border: 1px solid red; padding: 10px 15px; margin-bottom:15px; border-radius: 4px;}
.error-message p { margin: 0; } .error-message p + p { margin-top: 5px; }
.overview-main-content { display: flex; flex-direction: column; flex-grow: 1; min-height: 0; overflow: hidden; position: relative; }
.results-area { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; padding: 15px 25px; background-color: #fff; font-size: 16px; line-height: 1.7; color: #333; }
.results-area h3, .results-area h4 { margin-top: 1.5em; margin-bottom: 0.6em; color: var(--color-heading); font-weight: 600; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
.results-area h3:first-of-type { margin-top: 0; } .results-area p { margin-bottom: 0.75em; }
.results-area ul { list-style-type: disc; padding-left: 25px; margin-bottom: 1em; }
.results-area li { margin-bottom: 0.5em; } .results-area li strong { color: #1a1a1a; font-weight: 600; }
.results-area pre { white-space: pre-wrap; word-wrap: break-word; background-color: #fdfdfd; padding: 15px; border: 1px solid #eee; font-family: 'Courier New', Courier, monospace; font-size: 0.95em; line-height: 1.6; border-radius: 4px; margin-bottom: 1em; color: #222; }
.no-results-placeholder { position: absolute; top:0; left:0; right:0; bottom:0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #888; padding: 20px; font-style: italic; background-color: #fff; }
</style>