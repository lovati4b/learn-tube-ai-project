<template>
  <div class="notebook-page my-notes-page"> <!-- Root of MyNotesPage component -->
    <h3 class="page-title">My Notes</h3>
    <p class="page-subtitle"><i>Your space for notes, ideas, and questions on this video.</i></p>

    <!-- This container holds the textarea and will grow -->
    <div class="notes-editor-container">
      <textarea
        class="notes-textarea"
        placeholder="Start typing your notes here..."
        v-model="userNotes">
      </textarea>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const userNotes = ref('');
</script>

<style scoped>
/* Root div of this component. It's a child of .dynamic-component-wrapper */
.notebook-page.my-notes-page {
  display: flex; /* Makes this a flex container for its children (title, content) */
  flex-direction: column; /* Stack children vertically */
  flex-grow: 1; /* IMPORTANT: Allows this page to fill .dynamic-component-wrapper */
  min-height: 0; /* CRITICAL: Allows this page to be constrained by its parent's height */
  overflow: hidden; /* Safeguard: Clips its own children if they try to overflow this page */

  width: 100%; /* Original: Good */
  padding: 0; /* Original: Good */
  box-sizing: border-box; /* Original: Good */
  font-size: 16px; /* Original: Good */
  line-height: 1.7; /* Original: Good */
  color: #333; /* Original: Good */
}

/* Title and Subtitle are fixed-height elements at the top of the page */
.page-title {
  flex-shrink: 0;
  margin-bottom: 0.25em; color: var(--color-heading); font-weight: 600; font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em;
}
.page-subtitle {
  flex-shrink: 0;
  font-size: 0.9em; color: #777; margin-top: 0; margin-bottom: 1.5em;
}

/* This container holds the textarea. It's the part that needs to grow. */
.notes-editor-container {
  display: flex; /* Makes this a flex container for the textarea */
  flex-direction: column;
  flex-grow: 1; /* IMPORTANT: This makes the content area take up remaining vertical space */
  min-height: 0; /* CRITICAL: Allows this container to be constrained by .my-notes-page */
  /* overflow: hidden; */ /* Not strictly needed if textarea is only child and handles its own overflow */
}

/* The textarea itself will handle its scrolling */
.notes-textarea {
  flex-grow: 1; /* Takes all available space within .notes-editor-container */
  overflow-y: auto; /* Textarea's native scrollbar */
  /* min-height: 0; */ /* Usually not needed for textarea with flex-grow, it behaves well */
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 15px;
  resize: none;
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  color: inherit;
}
</style>