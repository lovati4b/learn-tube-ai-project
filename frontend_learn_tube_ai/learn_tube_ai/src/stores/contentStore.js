import { defineStore } from 'pinia';

export const useContentStore = defineStore('content', {
  state: () => ({
    activeMode: 'youtube', // 'youtube' or 'text'
    
    // Data for YouTube Video Mode
    youtubeData: {
      video_id: null,
      video_url: null,
      title: '',
      transcript_text: '',
      segments: [],
      analysis: null,
      isLoading: false, // To track loading state for this specific mode
      error: null,      // To store error specific to this mode
      showFallback: false, // For transcript paste fallback
    },

    // Data for Analyze My Text Mode
    textData: {
      id: null, // A unique ID if this text is saved/processed
      title: '',
      original_text: '', // The full text pasted by the user
      // `segments` might not be directly applicable or could be paragraphs
      // For now, let's assume analysis will be on original_text
      analysis: null,
      isLoading: false, // To track loading state for this specific mode
      error: null,      // To store error specific to this mode
    },

    // Shared loading/error for initial processing before mode is fully determined
    // Or we can rely on mode-specific isLoading flags
    globalIsLoading: false, 
    globalError: null,
  }),

  getters: {
    // Provides the data object for the currently active mode
    currentActiveDataPackage: (state) => {
      if (state.activeMode === 'youtube') {
        return state.youtubeData;
      } else if (state.activeMode === 'text') {
        return state.textData;
      }
      return null; // Or a default empty structure
    },

    // Provides data formatted for the Notebook/pages
    // This getter will be used by App.vue to pass props to Notebook.vue
    dataForNotebook: (state) => {
      let rawText = '';
      let segments = [];
      let currentAnalysis = null;
      let title = '';
      let isLoading = false;
      let error = null;
      let showFallback = false;
      let videoId = null;
      let videoUrl = null;

      if (state.activeMode === 'youtube') {
        rawText = state.youtubeData.transcript_text;    // Check for typos here
        segments = state.youtubeData.segments;          // Check for typos here
        currentAnalysis = state.youtubeData.analysis;   // Check for typos here
        title = state.youtubeData.title;              // Check for typos here
        isLoading = state.youtubeData.isLoading;      // Check for typos here
        error = state.youtubeData.error;              // Check for typos here
        showFallback = state.youtubeData.showFallback;  // Check for typos here
        videoId = state.youtubeData.video_id;         // Check for typos here
        videoUrl = state.youtubeData.video_url;       // Check for typos here
      
        // TEMPORARY DEBUG LOG INSIDE THE GETTER
      console.log('[Pinia Getter] dataForNotebook: In youtube mode. state.youtubeData:', JSON.parse(JSON.stringify(state.youtubeData)));
      console.log('[Pinia Getter] dataForNotebook: In youtube mode. Local vars set to:', { rawText, segmentsLength: segments?.length, currentAnalysisIsNotNull: !!currentAnalysis, title });
      }
      
      else if (state.activeMode === 'text') {
        rawText = state.textData.original_text;
        // For custom text, 'segments' might be different (e.g., paragraphs)
        // or not used in the same way. For now, pass empty or handle later.
        segments = []; // Or derive paragraphs if needed by FullTranscriptPage
        currentAnalysis = state.textData.analysis;
        title = state.textData.title;
        isLoading = state.textData.isLoading;
        error = state.textData.error;
      }

      return {
        // Props for Notebook's children
        rawTranscriptText: rawText,
        transcriptSegments: segments,
        analysisForOverview: currentAnalysis, // For VideoProcessor (Overview page)
        currentTitle: title,
        // Feedback for VideoProcessor (Overview page)
        isLoadingState: isLoading || state.globalIsLoading,
        errorState: error || state.globalError,
        showTranscriptPasteFallbackState: showFallback,
        currentVideoIdForFallback: state.youtubeData.video_id, // For fallback form
        currentVideoUrlForFallback: state.youtubeData.video_url, // For fallback form
         // Props for App.vue player
        videoIdForPlayer: state.activeMode === 'youtube' ? state.youtubeData.video_id : null,
      };
    },
  },

  actions: {
    setActiveMode(mode) {
      console.log('[Pinia] Action: setActiveMode, New mode:', mode);
      if (['youtube', 'text'].includes(mode)) {
        this.activeMode = mode;
        // When switching modes, clear global errors/loading that might be stale
        this.globalIsLoading = false;
        this.globalError = null;
      }
    },

    // Action to call when starting a new video processing operation
    startProcessingVideo(videoUrl) {
      console.log('[Pinia] Action: startProcessingVideo, URL:', videoUrl);
      this.activeMode = 'youtube'; // Ensure mode is correct
      this.youtubeData = { // Reset youtube data
        video_id: null, video_url: videoUrl, title: '', transcript_text: '',
        segments: [], analysis: null, isLoading: true, error: null, showFallback: false,
      };
      this.textData.isLoading = false; // Ensure other mode isn't loading
      this.textData.error = null;
      this.globalIsLoading = true; // Or use youtubeData.isLoading
      this.globalError = null;
    },

    // Action to call when starting a new custom text processing operation
    startProcessingText(customTitle, customTextContent) {
      console.log('[Pinia] Action: startProcessingText, Title:', customTitle);
      this.activeMode = 'text'; // Ensure mode is correct
      this.textData = { // Reset text data
        id: null, title: customTitle, original_text: customTextContent, 
        analysis: null, isLoading: true, error: null,
      };
      this.youtubeData.isLoading = false; // Ensure other mode isn't loading
      this.youtubeData.error = null;
      this.youtubeData.showFallback = false;
      this.globalIsLoading = true; // Or use textData.isLoading
      this.globalError = null;
    },
    
    // Action to handle successfully processed data (from video or text)
    setProcessedData(source, data) {
      console.log('[Pinia] Action: setProcessedData, Source:', source, 'Data:', data);
      this.globalIsLoading = false;
      if (source === 'youtube_video') {
        this.youtubeData = {
          video_id: data.video_id,
          video_url: data.video_url,
          title: data.title,
          transcript_text: data.transcript_text,
          segments: data.segments || [],
          analysis: data.analysis,
          isLoading: false,
          error: null,
          showFallback: false,
        };
      } else if (source === 'custom_text') {
        this.textData = {
          id: data.id, // Ensure backend provides this
          title: data.title,
          original_text: data.original_text, // Ensure backend provides or VideoProcessor sends this
          analysis: data.analysis,
          isLoading: false,
          error: null,
        };
      }
    },

    // Action to handle errors during processing
    setProcessingError(source, errorData) {
      console.error('[Pinia] Action: setProcessingError, Source:', source, 'Error Data:', errorData);
      this.globalIsLoading = false;
      const errorPayload = {
        message: errorData.error || 'An unknown error occurred.',
        details: errorData.details || '',
      };

      if (source === 'youtube_video') {
        this.youtubeData.isLoading = false;
        this.youtubeData.error = errorPayload;
        // Handle fallback specific logic
        if (errorData.showFallback && errorData.video_id) {
            this.youtubeData.showFallback = true;
            this.youtubeData.video_id = errorData.video_id; // Keep for fallback form
            this.youtubeData.video_url = errorData.video_url; // Keep for fallback form
        }
      } else if (source === 'custom_text') {
        this.textData.isLoading = false;
        this.textData.error = errorPayload;
      } else { // Generic error if source isn't clear
        this.globalError = errorPayload;
      }
    },

    // Action for when fallback transcript processing starts
    startProcessingFallbackTranscript() {
        console.log('[Pinia] Action: startProcessingFallbackTranscript');
        if (this.activeMode !== 'youtube') this.activeMode = 'youtube';
        this.youtubeData.isLoading = true; // Specific loading for this part
        this.youtubeData.error = null; // Clear previous error
        this.youtubeData.showFallback = true; // Keep fallback UI visible
    },

    // Action to clear fallback state
    clearFallbackState() {
        this.youtubeData.showFallback = false;
        // Optionally clear specific error that led to fallback if it's not needed anymore
        // if (this.youtubeData.error && this.youtubeData.error.message.includes("fetched automatically")) {
        //   this.youtubeData.error = null;
        // }
    }
  },
});
