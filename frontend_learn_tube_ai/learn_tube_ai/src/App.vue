--- START FILE: frontend_learn_tube_ai\learn_tube_ai\src\App.vue ---
<!-- FILE: src/App.vue - REFACTORED TO USE PINIA VIA notebookData FOR NOTEBOOK PROPS -->
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
      </div>
      <div class="right-pane notebook-area">
        <Notebook 
          :key="currentContentIdForPages"
          :currentContentId="notebookData.currentContentId"
          :rawTranscriptText="notebookData.rawTranscriptText"
          :transcriptSegments="notebookData.transcriptSegments"
          :currentVideoTime="appCurrentVideoTime"
          :analysisForOverview="notebookData.analysisForOverview"
          :currentTitleForOverview="notebookData.currentTitle" 
          :isLoadingState="notebookData.isLoadingState"
          :errorState="notebookData.errorState"
          :showTranscriptPasteFallbackState="notebookData.showTranscriptPasteFallbackState"
          :currentVideoIdForFallback="notebookData.currentVideoIdForFallback"
          :currentVideoUrlForFallback="notebookData.currentVideoUrlForFallback"
          @transcript-segment-clicked="handleTranscriptSegmentClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'; // Removed onMounted if not used
import Notebook from './components/Notebook.vue'; 
import { useContentStore } from './stores/contentStore';

const contentStore = useContentStore(); 

const notebookData = computed(() => {
  const isActive = contentStore.activeMode; 
  const ytData = contentStore.youtubeData;   
  const txtData = contentStore.textData;   
  const dataFromGetter = contentStore.dataForNotebook; 
  
  console.log(
    `App.vue: notebookData computed. ActiveMode: ${isActive}, ` +
    `VideoID from ytData: ${ytData.video_id}, Text Title: ${txtData.title}. ` + // Using ytData.video_id for logging
    `Getter returned:`, 
    JSON.parse(JSON.stringify(dataFromGetter))
  );
  return dataFromGetter; 
});

const currentVideoIdForPlayer = computed(() => {
    const id = notebookData.value.videoIdForPlayer; 
    console.log('App.vue: currentVideoIdForPlayer computed. ID:', id);
    return id;
});

const currentContentIdForPages = computed(() => contentStore.currentContentId);

const defaultEmbedSrc = 'https://www.youtube.com/embed/?enablejsapi=1&origin=' + encodeURIComponent(window.location.origin);

const youtubePlayer = ref(null); 
const youtubePlayerReady = ref(false);
const appCurrentVideoTime = ref(0); // This remains local for player time updates passed to Notebook
const timeUpdateInterval = ref(null);

const currentVideoEmbedUrl = computed(() => { 
  if (currentVideoIdForPlayer.value) {
    return `https://www.youtube.com/embed/${currentVideoIdForPlayer.value}?enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}`;
  }
  return defaultEmbedSrc; 
});

// REMOVED: handleVideoProcessed function, as this logic is now handled by VideoProcessor updating Pinia store

watch(currentVideoIdForPlayer, (newId, oldId) => { 
  console.log(`App.vue (Pinia): Player Video ID WATCHER. New ID: '${newId}', Old ID: '${oldId}', Player Ready: ${youtubePlayerReady.value}`);
  if (newId && newId !== oldId) { 
    console.log(`App.vue (Pinia): Watcher condition MET for loading player (newId && newId !== oldId). New ID: ${newId}`);
    youtubePlayerReady.value = false; 
    loadYoutubeAPIAndPlayer();
  } else if (!newId && oldId) { 
    console.log(`App.vue (Pinia): Watcher condition MET for destroying player (!newId and oldId existed). Old ID: ${oldId}`);
    destroyYoutubePlayer();
    appCurrentVideoTime.value = 0;
  } else if (newId && newId === oldId && !youtubePlayerReady.value) {
    console.log(`App.vue (Pinia): Watcher condition MET for re-attempting player load (newId === oldId but not ready). New ID: ${newId}`);
    loadYoutubeAPIAndPlayer(); 
  }
  else {
     console.log(`App.vue (Pinia): Player WATCHER - Condition for load/destroy NOT MET. newId: '${newId}', oldId: '${oldId}', Player Ready: ${youtubePlayerReady.value}`);
  }
});

const onPlayerReady = (event) => { 
  if (event.target && typeof event.target.getPlayerState === 'function') {
    youtubePlayer.value = event.target; 
    youtubePlayerReady.value = true;
    console.log("App.vue: YouTube Player is Ready. Video ID:", currentVideoIdForPlayer.value);
    if (typeof youtubePlayer.value.unMute === 'function' && typeof youtubePlayer.value.mute === 'function' && typeof youtubePlayer.value.isMuted === 'function') {
        const initiallyMuted = youtubePlayer.value.isMuted();
        youtubePlayer.value.mute(); 
        setTimeout(() => { 
            if (youtubePlayer.value && !initiallyMuted) { youtubePlayer.value.unMute(); }
        }, 50);
    }
  } else { 
    console.error("App.vue: onPlayerReady event target is not a valid player.");
    youtubePlayerReady.value = false; 
  }
};

const onPlayerStateChange = (event) => { 
  if (event.data === window.YT?.PlayerState?.PLAYING) { startCurrentTimeUpdates(); } 
  else { stopCurrentTimeUpdates(); }
};

const loadYoutubeAPIAndPlayer = () => { 
  if (!currentVideoIdForPlayer.value) { destroyYoutubePlayer(); return; }
  if (typeof window.YT === 'undefined' || typeof window.YT.Player === 'undefined') {
    if (document.getElementById('youtube-iframe-api')) { console.log("App.vue: YT API script already injected, waiting..."); return; }
    const tag = document.createElement('script'); tag.id = 'youtube-iframe-api'; tag.src = "https://www.youtube.com/iframe_api";
    const firstScriptTag = document.getElementsByTagName('script')[0];
    if (firstScriptTag && firstScriptTag.parentNode) { firstScriptTag.parentNode.insertBefore(tag, firstScriptTag); } 
    else { document.head.appendChild(tag); }
    window.onYouTubeIframeAPIReady = () => { console.log("App.vue: window.onYouTubeIframeAPIReady called."); createPlayer() ; };
    // Log was: console.log("App.vue: Creating new YT.Player with ID from store:", currentVideoIdForPlayer.value); // This log might be too early if API isn't ready
  } else { console.log("App.vue: YouTube Iframe API already loaded."); createPlayer(); }
};

const createPlayer = () => { 
  if (!currentVideoIdForPlayer.value) { console.error("App.vue: createPlayer called without currentVideoIdForPlayer."); return; }
  destroyYoutubePlayer(); 
  const playerDiv = document.getElementById('youtube-player');
  if (!playerDiv) { console.error("App.vue: Target div #youtube-player not found."); return; }
  playerDiv.innerHTML = ''; 
  try {
    // Log was: console.log("App.vue: Creating new YT.Player with ID:", currentVideoIdForPlayer.value);
    // More specific log moved to the watcher/loadYoutubeAPIAndPlayer for clarity on trigger point
    console.log("App.vue: Instantiating YT.Player with videoId:", currentVideoIdForPlayer.value);
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
    try { youtubePlayer.value.destroy(); console.log("App.vue: YouTube player destroyed.");} catch (e) { console.error("App.vue: Error destroying YT player:", e); }
  }
  youtubePlayer.value = null; youtubePlayerReady.value = false; 
  const playerDiv = document.getElementById('youtube-player');
  if (playerDiv) { playerDiv.innerHTML = ''; }
};

const startCurrentTimeUpdates = () => {
  if (timeUpdateInterval.value) clearInterval(timeUpdateInterval.value);
  timeUpdateInterval.value = setInterval(() => {
    if (youtubePlayer.value && typeof youtubePlayer.value.getCurrentTime === 'function' && 
        youtubePlayer.value.getPlayerState && youtubePlayer.value.getPlayerState() === window.YT?.PlayerState?.PLAYING) { 
      appCurrentVideoTime.value = youtubePlayer.value.getCurrentTime();
    }
  }, 500); 
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
  const targetTime = parseFloat(startTime);
  if (youtubePlayer.value && youtubePlayerReady.value && typeof youtubePlayer.value.seekTo === 'function') {
    youtubePlayer.value.seekTo(targetTime, true); 
    if (typeof youtubePlayer.value.playVideo === 'function') { youtubePlayer.value.playVideo(); }
    const iframe = youtubePlayer.value.getIframe();
    if (iframe && typeof iframe.focus === 'function') {iframe.focus();}
  } else if (!youtubePlayerReady.value && currentVideoIdForPlayer.value) {
    loadYoutubeAPIAndPlayer(); 
  }
};
</script>

<style scoped>
/* STYLES REMAIN THE SAME */
#app-container { max-width: 100%; padding: 0; font-weight: normal; display: flex; flex-direction: column; flex-grow: 1; min-height: 100vh; }
header { text-align: center; margin-bottom: 1rem; border-bottom: 1px solid #eee; padding: 1rem 0.5rem; flex-shrink: 0; background-color: #fff; position: sticky; top: 0; z-index: 10; }
header h1 { font-size: 2em; color: #2c3e50; margin: 0; }
.main-layout { display: flex; flex-direction: row; gap: 0.75rem; flex-grow: 1; overflow: hidden; padding: 0.5rem; align-items: stretch; min-height: 0; }
.left-pane { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; min-height: 0; }
.right-pane.notebook-area { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; min-height: 0; }
.video-player-area { background-color: #000000; border: 1px solid #ddd; border-radius: 8px; flex-shrink: 0; overflow: hidden; position: relative; width: 100%; height: 315px; }
#youtube-player, .video-player-area iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; border-radius: 7px; }
.video-placeholder-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #777; font-style: italic; }
</style>
