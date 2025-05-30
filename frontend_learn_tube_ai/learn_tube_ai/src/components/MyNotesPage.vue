<!-- FILE: src/components/MyNotesPage.vue - PHASE 1 CHANGES -->
<template>
  <div class="notebook-page my-notes-page">
    <h3 class="page-title">My Notes</h3>
    <p class="page-subtitle"><i>Your space for notes, ideas, and questions on this video.</i></p>
    
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
import { ref, defineProps, watch, onMounted, onActivated } from 'vue';

const props = defineProps({
  currentContentId: { type: [String, null], default: null }
});

const userNotes = ref('');
// This ref tracks the ID for which the current 'userNotes.value' is valid.
const notesCurrentlyForId = ref(null); 

function syncNotesStateWithContentId(newContentId) {
  // This function is called whenever the content ID might have changed.
  // It decides if notes should be cleared or (in the future) loaded.
  console.log(`MyNotesPage: syncNotesState. Current notes are for: '${notesCurrentlyForId.value}'. New incoming content ID: '${newContentId}'`);
  
  if (newContentId !== notesCurrentlyForId.value) {
    console.log(`MyNotesPage: Content ID mismatch or change detected. Clearing notes.`);
    userNotes.value = ''; // Clear current notes
    notesCurrentlyForId.value = newContentId; // Update what the (now empty) notes are for
    
    // Future enhancement:
    // if (newContentId) {
    //   // loadNotesFor(newContentId); 
    // }
  } else {
    console.log(`MyNotesPage: Content ID '${newContentId}' is the same as current '${notesCurrentlyForId.value}'. Notes preserved.`);
  }
}

onMounted(() => {
  console.log('MyNotesPage MOUNTED. Initial props.currentContentId:', props.currentContentId);
  syncNotesStateWithContentId(props.currentContentId);
});

onActivated(() => {
  // When tab is reactivated (due to KeepAlive)
  console.log('MyNotesPage ACTIVATED. Current props.currentContentId:', props.currentContentId);
  syncNotesStateWithContentId(props.currentContentId);
});

// Watch for direct changes to the prop while the component is active
watch(() => props.currentContentId, (newId, oldId) => {
  console.log(`MyNotesPage PROPS WATCHER: props.currentContentId changed from '${oldId}' to '${newId}'`);
  syncNotesStateWithContentId(newId); 
  // The oldId is also useful here if you need to save notes for oldId before clearing.
});
</script>


<style scoped>
.notebook-page.my-notes-page { 
  width: 100%; flex-grow: 1; padding: 0; box-sizing: border-box;
  display: flex; flex-direction: column; overflow: hidden; min-height: 0;
  font-size: 16px; line-height: 1.7; color: #333; 
}
.page-title { 
  margin-bottom: 0.25em; color: var(--color-heading); font-weight: 600; 
  font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; 
  flex-shrink: 0; 
}
.page-subtitle { 
  font-size: 0.9em; color: #777; margin-top: 0; margin-bottom: 1.5em; 
  flex-shrink: 0; 
}
.notes-editor-container {
  flex-grow: 1; display: flex; flex-direction: column; min-height: 0; 
}
.notes-textarea { 
  flex-grow: 1; overflow-y: auto; border: 1px solid #ccc; 
  border-radius: 4px; padding: 15px; resize: none; 
  font-family: inherit; font-size: inherit; line-height: inherit; color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s; /* For smooth focus */
}
/* Point #8: Yellow border on focus */
.notes-textarea:focus {
  border-color: #FFD700; /* Gold/Yellow */
  box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.4); /* Subtle glow */
  outline: none; /* Remove default browser outline */
}
</style>