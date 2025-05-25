<!-- FILE: src/components/AskAiPage.vue - REFINED LAYOUT FOR INPUT GROWTH & STYLING -->
<template>
  <div class="notebook-page ask-ai-page">
    <h3 class="page-title">Ask the AI</h3>
    
    <!-- This wrapper will take available space and be relative parent for scroll area -->
    <div class="ask-ai-chat-wrapper"> 
      <div class="chat-history-scroll-area" ref="chatHistoryContainer"> 
        <div v-for="(message, index) in messages" :key="'msg-' + index"
             :class="['chat-message', message.sender === 'user' ? 'user-message' : 'ai-message']">
          <div class="message-bubble">
            <p class="message-text">{{ message.text }}</p>
          </div>
        </div>
        <div v-if="messages.length === 0 && !isLoadingMessages" class="no-messages-placeholder">
          <p><i>Ask a question, or select text from the Transcript tab and click "Explain Selection".</i></p>
        </div>
        <div v-if="isLoadingMessages" class="loading-placeholder">
            <p><i>Loading messages...</i></p>
        </div>
      </div>
    </div>

    <div class="chat-input-area"> 
      <textarea
        ref="chatInputTextareaRef"
        class="chat-input"
        v-model="userInput"
        placeholder="Type your question here..."
        @keydown.enter="handleEnterKey"
        @input="autoGrowTextarea"
        rows="1" 
      ></textarea>
      <button @click="sendMessage" :disabled="!userInput.trim() || isSending" class="send-button" title="Send message">
        <svg v-if="!isSending" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
        <span v-if="isSending" class="sending-dots">...</span>
      </button>
    </div>
  </div>
</template>

<script setup>
// --- SCRIPT IS THE SAME as your last version with dynamic textarea logic ---
import { ref, nextTick, onMounted, defineProps, watch, defineEmits, onActivated } from 'vue';
const props = defineProps({ textForExplanation: { type: String, default: null }}); const emit = defineEmits(['explanation-query-handled']); const messages = ref([]); const userInput = ref(''); const chatHistoryContainer = ref(null); const isLoadingMessages = ref(false); const isSending = ref(false); const chatInputTextareaRef = ref(null); 
const scrollToBottom = () => { nextTick(() => { if (chatHistoryContainer.value) { chatHistoryContainer.value.scrollTop = chatHistoryContainer.value.scrollHeight; } });};
const processExplainTextProp = (textToExplain) => { if (textToExplain) { messages.value.push({ sender: 'user', text: `Please explain this: "${textToExplain}"` }); setTimeout(() => { messages.value.push({ sender: 'ai', text: `Mock explanation for: "${textToExplain.substring(0, 70)}..."` }); nextTick(scrollToBottom); }, 600); nextTick(scrollToBottom); emit('explanation-query-handled'); }};
onMounted(() => { scrollToBottom(); if (props.textForExplanation) { processExplainTextProp(props.textForExplanation); } nextTick(autoGrowTextarea); });
onActivated(() => { scrollToBottom(); if (props.textForExplanation) { processExplainTextProp(props.textForExplanation); } nextTick(autoGrowTextarea); });
watch(() => props.textForExplanation, (newText, oldText) => { if (newText && newText !== oldText) { processExplainTextProp(newText); }});
watch(messages, () => { scrollToBottom(); }, { deep: true });
const sendMessage = () => { const text = userInput.value.trim(); if (!text || isSending.value) return; isSending.value = true; messages.value.push({ sender: 'user', text: text }); const currentInputBeforeClear = userInput.value; userInput.value = ''; nextTick(() => { if (chatInputTextareaRef.value) { chatInputTextareaRef.value.style.height = 'auto'; chatInputTextareaRef.value.rows = 1; autoGrowTextarea(); } scrollToBottom(); }); setTimeout(() => { messages.value.push({ sender: 'ai', text: `Mock AI response to: "${currentInputBeforeClear}".`}); isSending.value = false; nextTick(scrollToBottom); }, 800 + Math.random() * 700);};
const handleEnterKey = (event) => { if (event.shiftKey) { return; } event.preventDefault(); sendMessage();};
const MAX_TEXTAREA_ROWS = 5; 
const autoGrowTextarea = () => { const textarea = chatInputTextareaRef.value; if (textarea) { textarea.style.height = 'auto'; const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20; const scrollHeight = textarea.scrollHeight; const contentHeight = scrollHeight - parseFloat(getComputedStyle(textarea).paddingTop) - parseFloat(getComputedStyle(textarea).paddingBottom); const calculatedRows = Math.round(contentHeight / lineHeight); textarea.rows = Math.max(1, Math.min(calculatedRows, MAX_TEXTAREA_ROWS)); textarea.style.height = `${textarea.scrollHeight}px`; if (calculatedRows > MAX_TEXTAREA_ROWS) { textarea.style.overflowY = 'auto'; } else { textarea.style.overflowY = 'hidden'; } }};
watch(userInput, () => { nextTick(autoGrowTextarea); });
</script>

<style scoped>
.notebook-page.ask-ai-page { 
  width: 100%; 
  flex-grow: 1; 
  display: flex; 
  flex-direction: column;
  overflow: hidden; 
  min-height: 0; 
  padding: 0; 
  box-sizing: border-box;
}
.page-title { 
  margin-bottom: 0.4em; /* <<< REDUCED */
  color: var(--color-heading); 
  font-weight: 600; 
  font-size: 1.4em; 
  border-bottom: 1px solid #eee; 
  padding-bottom: 0.25em; /* <<< REDUCED */
  flex-shrink: 0; 
  text-align: left; /* <<< CHANGED */
}

/* This wrapper takes up available space between title and input area */
.ask-ai-chat-wrapper { /* Renamed from .ask-ai-content-and-input-wrapper */
  flex-grow: 1; 
  display: flex; /* Not strictly necessary if child is absolute, but fine */
  min-height: 0; 
  overflow: hidden; 
  position: relative; /* <<< CRITICAL: For child's absolute positioning */
  background-color: #fff; /* Chat area background */
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 8px; 
}

.chat-history-scroll-area { 
  position: absolute; /* <<< Fills the .ask-ai-chat-wrapper */
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  overflow-y: auto; 
  padding: 10px 15px;
}

/* Message styles */
.chat-message { margin-bottom: 10px; display: flex; }
.message-bubble { 
  padding: 10px 14px; 
  border-radius: 12px; /* <<< Intermediate rounding for bubbles */
  max-width: 85%; 
  box-shadow: 0 1px 1px rgba(0,0,0,0.06); 
  line-height: 1.45; 
  word-wrap: break-word;
}
.message-bubble .message-text { margin: 0; white-space: pre-wrap; }
.user-message { justify-content: flex-end; }
.user-message .message-bubble { 
  background-color: #dcf8c6; 
  border-bottom-right-radius: 6px; 
}
.ai-message { justify-content: flex-start; }
.ai-message .message-bubble { /* <<< AI response plain text */
  background-color: transparent;
  box-shadow: none;
  padding: 2px 0; 
  border-radius: 0;
  max-width: 100%;
  color: #333; /* Ensure good text color */
}

.chat-input-area { 
  display: flex; gap: 8px; align-items: flex-end; 
  padding: 8px 10px; 
  border-top: 1px solid #d8dde3; /* Softer border */
  background-color: #f0f2f5; /* Slightly different background for input bar */
  flex-shrink: 0; 
  border-radius: 12px; /* <<< Intermediate rounding */
}
.chat-input { 
  flex-grow: 1; padding: 10px 14px; 
  border: 1px solid #d1d5db; 
  border-radius: 10px; /* <<< Intermediate rounding */
  resize: none; font-family: inherit; font-size: 1em; line-height: 1.4; 
  max-height: calc(1.4em * 5 + 22px); 
  overflow-y: hidden; 
  background-color: #fff;
  transition: border-color 0.2s, box-shadow 0.2s, height 0.1s ease-out;
}
.chat-input:focus { border-color: #5D8BF4; box-shadow: 0 0 0 2.5px rgba(93, 139, 244, 0.25); outline: none;}

.send-button { 
  background-color: #528BFF; /* Softer, slightly desaturated blue */
  color: white; border: none; 
  border-radius: 50%; 
  cursor: pointer; 
  height: 38px; /* Slightly smaller to match textarea better */
  width: 38px; 
  padding: 0; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: background-color 0.2s;
}
.send-button svg { width: 18px; height: 18px; }
.send-button .sending-dots { font-weight: bold; font-size: 1.2em; }
.send-button:hover { background-color: #4272d3; /* Darker shade */ } 
.send-button:disabled { background-color: #b0b0b0; cursor: not-allowed; }
</style>