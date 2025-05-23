<!-- FILE: src/App.vue - OPTIMIZED TIME UPDATES -->
<template>
  <div id="app-container">
    <header>
      <h1>LearnTube AI Notebook</h1>
    </header>
    <div class="main-layout">
      <div class="left-pane">
        <div class="video-player-area">
          <div id="youtube-player"></div>
          <iframe v-if="!youtubePlayerReady && currentVideoEmbedUrl !== defaultEmbedSrc" 
                  width="100%" height="100%"
                  :src="currentVideoEmbedUrl"
                  title="YouTube video player fallback"
                  frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen>
          </iframe> 
           <div v-if="!currentVideoIdForPlayer && !youtubePlayerReady" class="video-placeholder-text">
            No video loaded
          </div>
        </div>
        <!-- Small transcript area previously here is removed -->
      </div>
      <div class="right-pane notebook-area">
        <Notebook 
          :rawTranscriptText="appRawTranscriptText"
          :transcriptSegments="appTranscriptSegments"
          :currentVideoTime="appCurrentVideoTime"
          @video-processed="handleVideoProcessed" 
          @transcript-segment-clicked="handleTranscriptSegmentClick"
        />
        <!-- Pass currentVideoTime -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'; // nextTick removed if not used here
import Notebook from './components/Notebook.vue'; 

const appRawTranscriptText = ref(''); 
const appTranscriptSegments = ref([]); 
const currentVideoIdForPlayer = ref(''); 
const defaultEmbedSrc = 'https://www.youtube.com/embed/?enablejsapi=1&origin=' + encodeURIComponent(window.location.origin);

const youtubePlayer = ref(null); 
const youtubePlayerReady = ref(false);
const appCurrentVideoTime = ref(0); // This is passed as prop
const timeUpdateInterval = ref(null);
// appActiveSegmentId is no longer needed here; FullTranscriptPage handles its own active state

const currentVideoEmbedUrl = computed(() => { 
  if (currentVideoIdForPlayer.value) {
    return `https://www.youtube.com/embed/${currentVideoIdForPlayer.value}?enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}`;
  }
  return defaultEmbedSrc; 
});

const handleVideoProcessed = (analysisResult) => {
  console.log("App.vue received video-processed event:", analysisResult);
  const newVideoId = analysisResult?.video_id || '';

  appRawTranscriptText.value = analysisResult?.transcript_text || 
                               (analysisResult?.error ? `Error: ${analysisResult.error}\nDetails: ${analysisResult.details || ''}` : 'Transcript data not available.');
  appTranscriptSegments.value = (analysisResult?.segments && Array.isArray(analysisResult.segments)) ? analysisResult.segments : [];

  if (currentVideoIdForPlayer.value !== newVideoId) {
    currentVideoIdForPlayer.value = newVideoId; 
  } else if (newVideoId && (!youtubePlayer.value || !youtubePlayerReady.value)) {
    loadYoutubeAPIAndPlayer(); 
  } else if (!newVideoId) { 
    currentVideoIdForPlayer.value = ''; 
  }
};

watch(currentVideoIdForPlayer, (newId, oldId) => { 
  if (newId) {
    youtubePlayerReady.value = false; 
    loadYoutubeAPIAndPlayer();
  } else {
    destroyYoutubePlayer();
    appRawTranscriptText.value = 'Transcript will appear here once a video is processed...';
    appTranscriptSegments.value = [];
    appCurrentVideoTime.value = 0;
  }
});

const onPlayerReady = (event) => { 
  if (event.target && typeof event.target.getPlayerState === 'function') {
    youtubePlayer.value = event.target; 
    youtubePlayerReady.value = true;
    console.log("App.vue: YouTube Player is Ready for video:", currentVideoIdForPlayer.value);
  } else { youtubePlayerReady.value = false; }
};

const onPlayerStateChange = (event) => { 
  if (event.data === YT.PlayerState.PLAYING) { startCurrentTimeUpdates(); } 
  else { stopCurrentTimeUpdates(); }
};

const loadYoutubeAPIAndPlayer = () => { 
  if (!currentVideoIdForPlayer.value) { destroyYoutubePlayer(); return; }
  if (typeof window.YT === 'undefined' || typeof window.YT.Player === 'undefined') {
    if (document.getElementById('youtube-iframe-api')) { return; }
    const tag = document.createElement('script'); tag.id = 'youtube-iframe-api'; tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    if (firstScriptTag && firstScriptTag.parentNode) { firstScriptTag.parentNode.insertBefore(tag, firstScriptTag); } 
    else { document.head.appendChild(tag); }
    window.onYouTubeIframeAPIReady = () => { createPlayer(); };
  } else { createPlayer(); }
};

const createPlayer = () => { 
  if (!currentVideoIdForPlayer.value) return;
  destroyYoutubePlayer(); 
  const playerDiv = document.getElementById('youtube-player');
  if (!playerDiv) { console.error("App.vue: Target div #youtube-player not found."); return; }
  playerDiv.innerHTML = ''; 
  try {
    youtubePlayer.value = new window.YT.Player('youtube-player', {
      videoId: currentVideoIdForPlayer.value,
      playerVars: { 'playsinline': 1, 'controls': 1, 'modestbranding': 1, 'rel': 0, 'origin': window.location.origin },
      events: { 'onReady': onPlayerReady, 'onStateChange': onPlayerStateChange }
    });
  } catch (e) { console.error("App.vue: Error creating YT.Player:", e); youtubePlayerReady.value = false; }
};

const destroyYoutubePlayer = () => { 
  stopCurrentTimeUpdates(); 
  if (youtubePlayer.value && typeof youtubePlayer.value.destroy === 'function') {
    try { youtubePlayer.value.destroy(); } catch (e) { console.error("App.vue: Error destroying YT player:", e); }
  }
  youtubePlayer.value = null; youtubePlayerReady.value = false; 
  const playerDiv = document.getElementById('youtube-player');
  if (playerDiv) { playerDiv.innerHTML = ''; }
};

const startCurrentTimeUpdates = () => {
  if (timeUpdateInterval.value) clearInterval(timeUpdateInterval.value);
  timeUpdateInterval.value = setInterval(() => {
    if (youtubePlayer.value && typeof youtubePlayer.value.getCurrentTime === 'function' && youtubePlayer.value.getPlayerState() === YT.PlayerState.PLAYING) {
      appCurrentVideoTime.value = youtubePlayer.value.getCurrentTime();
      // updateAppActiveSegment() is removed - FullTranscriptPage handles its own highlighting based on appCurrentVideoTime prop
    }
  }, 500); // <<< Changed to 500ms (or try 750ms)
};
const stopCurrentTimeUpdates = () => {
  if (timeUpdateInterval.value) clearInterval(timeUpdateInterval.value);
  timeUpdateInterval.value = null;
};

onUnmounted(() => { 
  destroyYoutubePlayer(); 
  window.onYouTubeIframeAPIReady = null; 
});

const handleTranscriptSegmentClick = (startTime) => { 
  if (youtubePlayer.value && youtubePlayerReady.value && typeof youtubePlayer.value.seekTo === 'function') {
    youtubePlayer.value.seekTo(parseFloat(startTime), true); 
    if (typeof youtubePlayer.value.playVideo === 'function') { youtubePlayer.value.playVideo(); }
  } else if (!youtubePlayerReady.value && currentVideoIdForPlayer.value) {
    loadYoutubeAPIAndPlayer(); 
  }
};

// updateAppActiveSegment and appActiveSegmentId ref are removed.
// isActiveSegment is also removed from App.vue.
</script>

<style scoped>
/* STYLES ARE THE SAME as the version where left pane only had video player */
#app-container { max-width: 100%; padding: 0; font-weight: normal; display: flex; flex-direction: column; flex-grow: 1; min-height: 100vh; }
header { text-align: center; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding: 1rem 0.5rem; flex-shrink: 0; background-color: #fff; position: sticky; top: 0; z-index: 10; }
header h1 { font-size: 2em; color: #2c3e50; margin: 0; }
.main-layout { display: flex; flex-direction: row; gap: 0.75rem; flex-grow: 1; overflow: hidden; padding: 0.5rem; align-items: stretch; min-height: 0; }
.left-pane { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; min-height: 0; }
.right-pane.notebook-area { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; min-height: 0; }
.video-player-area {
  background-color: #000000; 
  border: 1px solid #ddd;
  border-radius: 8px;
  flex-shrink: 0; /* <<< CHANGED from flex-grow:1 - Prevents vertical resizing */
  overflow: hidden; 
  position: relative; 
  width: 100%; /* Takes full width of left-pane's content box */
  height: 315px; /* <<< ADDED - Explicit fixed height */
  /* display: flex; align-items: center; justify-content: center; */ /* Optional now */
}

#youtube-player,
.video-player-area iframe { 
  position: absolute; 
  top: 0; 
  left: 0;
  width: 100%; 
  height: 100%; /* Fills the .video-player-area's explicit height */
  border: none; 
  border-radius: 7px; 
}
.video-placeholder-text { 
  /* This text will likely be hidden behind the player once it loads */
  position: absolute; top: 50%; left: 50%; 
  transform: translate(-50%, -50%);
  color: #777; /* Darker for better visibility on black if player fails */
  font-style: italic; 
}
</style>