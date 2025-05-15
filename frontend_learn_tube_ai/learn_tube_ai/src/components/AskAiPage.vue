<!-- FILE: src/components/AskAiPage.vue - STEP A -->
<template>
  <div class="notebook-page ask-ai-page"> <!-- Root: flex-grow:1 -->
    <h3 class="page-title">Ask the AI (Step A Test)</h3>
    <!-- <p class="page-subtitle"><i>Subtitle if needed</i></p> -->
    
    <!-- This div is the main content area that grows between title and input -->
    <div class="ask-ai-main-content-area">
      <!-- This div is for the chat history and should scroll -->
      <div class="chat-history-placeholder-scroller" ref="chatHistoryScroller_A">
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 1</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 2</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 3</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 4</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 5</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 6</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 7</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 8</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 9</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 10</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 11</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 12</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 13</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 14</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 15</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 16</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 17</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 18</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 19</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 20</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 21</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 22</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 23</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 24</p>
        <p style="background: lightskyblue; margin-bottom: 5px; padding: 5px;">Test Line 25</p>
      </div>
    </div>

    <!-- Original Chat Input Area -->
    <div class="chat-input-area">
      <textarea
        class="chat-input"
        v-model="userInput_A"
        placeholder="Type your question here..."
        @keydown.enter="handleEnterKey_A"
      ></textarea>
      <button @click="sendMessage_A" :disabled="!userInput_A.trim()" class="send-button">
        Send
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'; // Keep nextTick, onMounted, onUpdated for later if needed

// Minimal script for this step - just to make input work, no actual message sending logic yet
const userInput_A = ref('');

// Placeholder - real sendMessage and handleEnterKey will be restored later
const sendMessage_A = () => {
  console.log("Send clicked (Step A):", userInput_A.value);
  userInput_A.value = '';
};
const handleEnterKey_A = (event) => {
  if (event.shiftKey) { return; }
  event.preventDefault();
  sendMessage_A();
};
</script>

<style scoped>
/* Root style - must be identical to MyNotesPage's working root */
.notebook-page.ask-ai-page { 
  width: 100%;
  flex-grow: 1; 
  padding: 0; 
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden; 
  min-height: 0;
  font-size: 15px; /* Adjusted from MyNotes for consistency with original AskAI */
  line-height: 1.6; 
  /* color from var(--color-text) or #333 */
}

.page-title { /* Style for the title */
  margin-bottom: 0.75em; 
  color: var(--color-heading); 
  font-weight: 600; 
  font-size: 1.4em; /* Original AskAI title size */
  border-bottom: 1px solid #eee; 
  padding-bottom: 0.3em;
  flex-shrink: 0; /* Title is fixed height */
}

/* This is the main container that grows, holding the history and input */
/* This structure is key: Page -> Title (fixed) -> MainContent (grows) -> InputArea (fixed) */
/* No, this model is wrong for this step.
   Page -> Title (fixed) -> SCROLLING_HISTORY (grows) -> InputArea (fixed)
   We need an intermediate wrapper that grows, THEN the history grows within THAT, like MyNotes
*/

/* CORRECTED STRUCTURE: Page (grows) -> Title (fixed) -> CONTENT_WRAPPER (grows) -> InputArea (fixed) */
/* Inside CONTENT_WRAPPER: HISTORY_SCROLLER (grows) */

.ask-ai-main-content-area { /* This mimics .notes-editor-container */
  flex-grow: 1;           /* Takes space between title and input area */
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;         /* It clips/constrains the history scroller */
  background-color: #f0f0f0; /* Temp bg to see its bounds */
}

.chat-history-placeholder-scroller { /* This mimics .notes-textarea (but is a div) */
  flex-grow: 1;                 /* Takes all space in .ask-ai-main-content-area */
  overflow-y: auto;             /* THIS should scroll */
  min-height: 0;
  padding: 10px;
  background-color: #f9f9f9;    /* Original chat history bg */
  border: 1px solid #e0e0e0;    /* Original chat history border */
  border-radius: 4px;           /* Original chat history border-radius */
}

/* Chat Input Area - copied from original AskAiPage.vue */
.chat-input-area { 
  display: flex; 
  gap: 10px; 
  align-items: flex-start; 
  padding: 10px; 
  border-top: 1px solid #e0e0e0; 
  background-color: #fff; 
  flex-shrink: 0; /* Input area is fixed height */
}
.chat-input { 
  flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px; 
  resize: none; font-family: inherit; font-size: 1em; line-height: 1.4; 
  min-height: 40px; max-height: 120px; overflow-y: auto; 
}
.send-button { 
  padding: 10px 18px; background-color: #42b983; color: white; border: none; 
  border-radius: 6px; cursor: pointer; font-size: 1em; height: 40px; align-self: flex-end; 
}
.send-button:disabled { background-color: #aaa; }
</style>