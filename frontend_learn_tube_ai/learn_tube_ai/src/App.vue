<!-- FILE: src/App.vue -->
<template>
  <div id="app-container">
    <header>
      <h1>LearnTube AI Notebook</h1>
    </header>
    <div class="main-layout">
      <div class="left-pane">
        <div class="video-player-area">
          <p style="margin-top:0; margin-bottom: 5px;">[Video Player Area]</p>
          <iframe width="100%" height="315"
                  src="https://www.youtube.com/embed/dQw4w9WgXcQ"
                  title="YouTube video player"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen>
          </iframe>
        </div>
        <div class="transcript-area">
          <p style="margin-top:0; margin-bottom: 5px;">[Transcript Area]</p>
          <!-- Added class "main-transcript-textarea" for focus styling -->
          <textarea class="main-transcript-textarea" rows="15" style="width: 100%; font-family: monospace; font-size: 12px;" placeholder="Transcript will appear here..." readonly></textarea>
        </div>
      </div>
      <div class="right-pane notebook-area">
        <Notebook />
      </div>
    </div>
  </div>
</template>

<script setup>
import Notebook from './components/Notebook.vue';
</script>

<style scoped>
#app-container {
  max-width: 100%;
  padding: 0;
  font-weight: normal;
  display: flex;
  flex-direction: column;
  flex-grow: 1; 
  min-height: 100vh; 
}

header {
  text-align: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
  padding: 1rem 0.5rem;
  flex-shrink: 0; 
}
header h1 { font-size: 2em; color: #2c3e50; }

.main-layout {
  display: flex;
  flex-direction: row; 
  gap: 0.75rem;
  flex-grow: 1; 
  overflow: hidden; 
  padding: 0;
  align-items: stretch; 
  min-height: 0; 
}

.left-pane {
  flex: 1; 
  display: flex;
  flex-direction: column; 
  gap: 0.75rem;
  min-width: 0; 
  padding: 0.5rem;
  overflow: hidden;
  min-height: 0; 
}

.right-pane.notebook-area {
  flex: 1; 
  display: flex;
  flex-direction: column; 
  min-width: 0; 
  overflow: hidden; 
  min-height: 0; 
  /* background-color: lightcoral; */ /* <<< REMOVED DEBUG COLOR */
  /* Background will come from Notebook.vue's .dynamic-component-wrapper or can be set here if desired */
  /* Example for AliceBlue background for the whole pane: */
  /* background-color: #f0f8ff;  */
}

.video-player-area {
  background-color: #f0f0f0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-align: center;
  flex-shrink: 0; 
}
.video-player-area p { font-weight: bold; color: #555; }

.transcript-area {
  background-color: #f9f9f9;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  flex-grow: 1; 
  display: flex;
  flex-direction: column; 
  overflow: hidden; 
  min-height: 0; 
}
.transcript-area p { font-weight: bold; color: #555; flex-shrink: 0; }

.main-transcript-textarea { /* Style for the main transcript textarea */
  flex-grow: 1; 
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  resize: none;
  overflow-y: auto; 
  /* width: 100% and font-family/size are still inline for this specific one */
  transition: border-color 0.2s, box-shadow 0.2s; /* For smooth focus */
}
.main-transcript-textarea:focus {
  border-color: #FFD700; /* Gold/Yellow */
  box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.4); /* Subtle glow */
  outline: none; /* Remove default browser outline */
}
</style>