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
          <textarea rows="15" style="width: 100%; font-family: monospace; font-size: 12px;" placeholder="Transcript will appear here..." readonly></textarea>
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
  flex-grow: 1; /* If #app-container is itself a flex child of body or #app */
  min-height: 100vh; /* Base height */
}

header {
  text-align: center;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
  padding: 1rem 0.5rem;
  flex-shrink: 0; /* Header has fixed height */
}
header h1 { font-size: 2em; color: #2c3e50; }

.main-layout {
  display: flex;
  flex-direction: row; /* Left and Right panes side-by-side */
  gap: 0.75rem;
  flex-grow: 1; /* Takes remaining vertical space in #app-container */
  overflow: hidden; /* IMPORTANT: Constrains children (panes) */
  padding: 0;
  align-items: stretch;
  min-height: 0; /* Allows .main-layout to shrink if necessary, complements flex-grow */
}

.left-pane {
  flex: 1; /* Takes 1 part of available width */
  display: flex;
  flex-direction: column; /* Stacks video and transcript vertically */
  gap: 0.75rem;
  min-width: 0; /* Allows shrinking below content width */
  padding: 0.5rem;
  overflow: hidden; /* Constrains its children */
  min-height: 0; /* Allows it to be constrained by .main-layout's height */
}

.right-pane.notebook-area {
  flex: 1; /* Takes 1 part of available width */
  display: flex;
  flex-direction: column; /* Notebook component will be stacked vertically (nav, content) */
  min-width: 0; /* Allows shrinking below content width */
  overflow: hidden; /* Constrains Notebook component */
  min-height: 0; /* Allows it to be constrained by .main-layout's height */
  background-color: lightcoral; /* For debugging if it's still short */
}

.video-player-area {
  background-color: #f0f0f0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  text-align: center;
  flex-shrink: 0; /* Fixed height element */
}
.video-player-area p { font-weight: bold; color: #555; }

.transcript-area {
  background-color: #f9f9f9;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  flex-grow: 1; /* Takes remaining space in .left-pane */
  display: flex;
  flex-direction: column; /* Stacks its <p> and <textarea> */
  overflow: hidden; /* Constrains the textarea */
  min-height: 0; /* Critical */
}
.transcript-area p { font-weight: bold; color: #555; flex-shrink: 0; }
.transcript-area textarea {
  flex-grow: 1; /* Takes remaining space in .transcript-area */
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 8px;
  resize: none;
  overflow-y: auto; /* Textarea handles its own scroll */
}
</style>