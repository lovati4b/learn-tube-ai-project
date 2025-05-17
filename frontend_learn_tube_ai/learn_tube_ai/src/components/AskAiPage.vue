<!-- FILE: src/components/AskAiPage.vue - PHASE 2 STYLING CHANGES -->
<template>
  <!-- ... TEMPLATE IS THE SAME AS THE LAST WORKING VERSION ... -->
  <div class="notebook-page ask-ai-page">
    <h3 class="page-title">Ask the AI</h3>
    <div class="ask-ai-growing-content-wrapper"> 
      <div class="chat-history-scroll-area" ref="chatHistoryContainer"> 
        <div v-for="(message, index) in messages" :key="index" 
             :class="['chat-message', message.sender === 'user' ? 'user-message' : 'ai-message']">
          <div class="message-bubble">
            <span class="sender-label">{{ message.sender === 'user' ? 'You' : 'AI Assistant' }}:</span>
            <p class="message-text">{{ message.text }}</p>
          </div>
        </div>
        <div v-if="messages.length === 0 && !isLoadingMessages" class="no-messages-placeholder">
          <p><i>Ask a question...</i></p>
        </div>
        <div v-if="isLoadingMessages" class="loading-placeholder">
            <p><i>Loading messages...</i></p>
        </div>
      </div>
    </div>
    <div class="chat-input-area">
      <textarea class="chat-input" v-model="userInput" placeholder="Type your question here..." @keydown.enter="handleEnterKey"></textarea>
      <button @click="sendMessage" :disabled="!userInput.trim() || isSending" class="send-button">
        {{ isSending ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script setup>
// ... SCRIPT IS THE SAME AS THE LAST WORKING VERSION ...
import { ref, nextTick, onMounted, onUpdated } from 'vue';
const messages = ref([]); // Defaulting to empty now
const userInput = ref('');
const chatHistoryContainer = ref(null);
const isLoadingMessages = ref(false); 
const isSending = ref(false); 
const scrollToBottom = () => { nextTick(() => { if (chatHistoryContainer.value) { chatHistoryContainer.value.scrollTop = chatHistoryContainer.value.scrollHeight; } }); };
onMounted(() => { scrollToBottom(); });
onUpdated(scrollToBottom);
const sendMessage = () => { const text = userInput.value.trim(); if (!text || isSending.value) return; isSending.value = true; messages.value.push({ sender: 'user', text: text }); userInput.value = ''; setTimeout(() => { messages.value.push({ sender: 'ai', text: `Mock AI response to: "${text}".` }); isSending.value = false; }, 800 + Math.random() * 700); };
const handleEnterKey = (event) => { if (event.shiftKey) { return; } event.preventDefault(); sendMessage(); };
</script>

<style scoped>
.notebook-page.ask-ai-page { 
  width: 100%; flex-grow: 1; display: flex; flex-direction: column;
  overflow: hidden; min-height: 0; padding: 0; box-sizing: border-box;
  font-size: 15px; line-height: 1.6;
}
.page-title { 
  margin-bottom: 0.75em; color: var(--color-heading); font-weight: 600; 
  font-size: 1.4em; border-bottom: 1px solid #eee; padding-bottom: 0.3em;
  flex-shrink: 0; 
}

.ask-ai-growing-content-wrapper { 
  flex-grow: 1; display: flex; flex-direction: column;
  min-height: 0; overflow: hidden; position: relative; 
  /* --- Phase 2 Change: Make wrapper blend with page --- */
  background-color: #ffffff; /* Make it white like the main page bg */
  border: none;             /* Remove border */
  border-radius: 0;         /* Remove radius */
  margin-bottom: 10px; 
}

.chat-history-scroll-area { 
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  overflow-y: auto; padding: 10px;
  /* Background is now effectively the white from .ask-ai-growing-content-wrapper */
}

.chat-message { margin-bottom: 12px; display: flex; }

/* User Message Bubble - Stays the Same */
.user-message { justify-content: flex-end; }
.user-message .message-bubble { 
  background-color: #DCF8C6; 
  border-bottom-right-radius: 5px;
  padding: 8px 12px; 
  border-radius: 15px; 
  max-width: 80%; 
  box-shadow: 0 1px 2px rgba(0,0,0,0.05); 
  line-height: 1.4; 
}
.user-message .sender-label { text-align: right; }

/* AI Message - Notebook Style (No Bubble) */
.ai-message { 
  justify-content: flex-start; 
  /* Optional: add a subtle left margin if needed for alignment */
  /* margin-left: 5px;  */
}
.ai-message .message-bubble { 
  background-color: transparent; /* <<< Phase 2 Change */
  border: none;                  /* <<< Phase 2 Change */
  box-shadow: none;              /* <<< Phase 2 Change */
  padding: 0;                    /* <<< Phase 2 Change: Padding will be on text/label */
  border-radius: 0;              /* <<< Phase 2 Change */
  max-width: 100%;               /* Can take more width if not a bubble */
  line-height: 1.4; 
}
.ai-message .sender-label {
  /* Keep sender label, but it won't be in a bubble */
  margin-bottom: 4px; /* Same */
  /* Optional: Different color or style for AI label if needed */
  /* color: #007bff; */
}
.ai-message .message-text {
  /* Ensure AI message text has some padding if bubble padding is removed */
  /* If sender-label is present, text might align well already. If not, add padding. */
  /* padding: 2px 0; */ /* Example if sender label is above */
  margin:0; /* Base */
}


.message-bubble .sender-label { /* Common for both user and AI if not overridden */
  font-weight: bold; font-size: 0.8em; display: block;  color: #555; 
}
.message-bubble .message-text { /* Common for both user and AI if not overridden */
  margin: 0; white-space: pre-wrap; word-wrap: break-word; 
}

.no-messages-placeholder, .loading-placeholder { 
  text-align: center; color: #888; padding: 30px 10px; font-style: italic;
  display: flex; align-items: center; justify-content: center; height: 100%;
}

.chat-input-area { 
  display: flex; gap: 10px; align-items: center; 
  padding: 10px; border-top: 1px solid #e0e0e0; 
  background-color: #fdfdfd; flex-shrink: 0; 
  border-radius: 8px; 
  margin-top: auto; 
  box-shadow: 0 -2px 5px rgba(0,0,0,0.03); 
}
.chat-input { 
  flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px; 
  resize: none; font-family: inherit; font-size: 1em; line-height: 1.4; 
  min-height: 40px; max-height: 120px; overflow-y: auto; 
}
.send-button { 
  padding: 0 18px; 
  background-color: #5c9ded; /* Bluish color */
  color: white; border: none; 
  border-radius: 6px; cursor: pointer; font-size: 1em; 
  height: 40px; line-height: 40px; 
  white-space: nowrap;
  transition: background-color 0.2s;
}
.send-button:hover { background-color: #4a8ad8; }
.send-button:disabled { background-color: #aaa; }
</style>
