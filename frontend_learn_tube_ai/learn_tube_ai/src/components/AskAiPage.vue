<!-- FILE: src/components/AskAiPage.vue - PROCESSES EXPLAIN TEXT REQUEST -->
<template>
  <div class="notebook-page ask-ai-page">
    <h3 class="page-title">Ask the AI</h3>
    <div class="ask-ai-growing-content-wrapper"> 
      <div class="chat-history-scroll-area" ref="chatHistoryContainer"> 
        <div v-for="(message, index) in messages" :key="'msg-' + index"
             :class="['chat-message', message.sender === 'user' ? 'user-message' : 'ai-message']">
          <div class="message-bubble">
            <span class="sender-label">{{ message.sender === 'user' ? 'You' : 'AI Assistant' }}:</span>
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
      <textarea class="chat-input" v-model="userInput" placeholder="Type your question here..." @keydown.enter="handleEnterKey"></textarea>
      <button @click="sendMessage" :disabled="!userInput.trim() || isSending" class="send-button">
        {{ isSending ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUpdated, defineProps, watch, defineEmits } from 'vue';

const props = defineProps({
  textForExplanation: { // Prop from Notebook.vue
    type: String,
    default: null
  }
});

const emit = defineEmits(['explanation-query-handled']); // To notify Notebook.vue

const messages = ref([]); 
const userInput = ref('');
const chatHistoryContainer = ref(null);
const isLoadingMessages = ref(false); 
const isSending = ref(false); 

const scrollToBottom = () => { /* ... same as before ... */ };
onMounted(() => { 
  scrollToBottom(); 
  // Check if there's text to explain on initial mount/activation
  if (props.textForExplanation) {
    processExplainTextProp(props.textForExplanation);
  }
});
// onUpdated(scrollToBottom); // Already called by messages.value.push if messages array itself changes

const sendMessage = () => { 
    const text = userInput.value.trim();
    if (!text || isSending.value) return;
    isSending.value = true;
    messages.value.push({ sender: 'user', text: text });
    userInput.value = ''; 
    setTimeout(() => {
        messages.value.push({ sender: 'ai', text: `Mock AI response to: "${text}".`});
        isSending.value = false;
        nextTick(scrollToBottom); // Ensure scroll after AI message
    }, 800 + Math.random() * 700);
    nextTick(scrollToBottom); // Scroll after user message
};
const handleEnterKey = (event) => { if (event.shiftKey) { return; } event.preventDefault(); sendMessage();};

const processExplainTextProp = (textToExplain) => {
  if (textToExplain) {
    console.log("AskAiPage: Received textForExplanation via prop:", textToExplain);
    messages.value.push({ sender: 'user', text: `Please explain this: "${textToExplain}"` });
    setTimeout(() => {
      messages.value.push({ 
        sender: 'ai', 
        text: `This is a mock AI explanation for: "${textToExplain.substring(0, 70)}..." - Real explanation pending LLM integration.` 
      });
      nextTick(scrollToBottom); // Scroll after AI mock response
    }, 600);
    nextTick(scrollToBottom); // Scroll after user query
    emit('explanation-query-handled'); // Notify parent to clear the prop
  }
};

// Watch for textForExplanation prop changes
watch(() => props.textForExplanation, (newText, oldText) => {
  // Process only if newText is present and different from the immediate previous one
  // (to avoid re-processing if component re-renders but prop hasn't "meaningfully" changed for this purpose)
  if (newText) { 
    processExplainTextProp(newText);
  }
});

// Also scroll when messages array is directly manipulated
watch(messages, () => {
    scrollToBottom();
}, { deep: true });

</script>

<style scoped>
/* STYLES ARE THE SAME as the last working version for AskAI page layout */
/* ... (ensure all styles from the last complete AskAiPage.vue are here) ... */
.notebook-page.ask-ai-page { width: 100%; flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; padding: 0; box-sizing: border-box; font-size: 15px; line-height: 1.6;}
.page-title { margin-bottom: 0.75em; color: var(--color-heading); font-weight: 600; font-size: 1.4em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; flex-shrink: 0; }
.ask-ai-growing-content-wrapper { flex-grow: 1; display: flex; /* Ensure this is flex if not already */ flex-direction: column; /* Ensure this is column if not already */ min-height: 0; overflow: hidden; position: relative; background-color: #ffffff; border: none; border-radius: 0; margin-bottom: 10px; }
.chat-history-scroll-area { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; padding: 10px;}
.chat-message { margin-bottom: 12px; display: flex; }
.message-bubble { padding: 8px 12px; border-radius: 15px; max-width: 80%; box-shadow: 0 1px 2px rgba(0,0,0,0.05); line-height: 1.4; }
.message-bubble .sender-label { font-weight: bold; font-size: 0.8em; display: block; margin-bottom: 4px; color: #555; }
.message-bubble .message-text { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
.user-message { justify-content: flex-end; }
.user-message .message-bubble { background-color: #DCF8C6; border-bottom-right-radius: 5px; }
.user-message .sender-label { text-align: right; }
.ai-message { justify-content: flex-start; }
.ai-message .message-bubble { background-color: transparent; border: none; box-shadow: none; padding: 0; border-radius: 0; max-width: 100%; line-height: 1.4; }
.no-messages-placeholder, .loading-placeholder { text-align: center; color: #888; padding: 30px 10px; font-style: italic; display: flex; align-items: center; justify-content: center; height: 100%;}
.chat-input-area { display: flex; gap: 10px; align-items: center; padding: 10px; border-top: 1px solid #e0e0e0; background-color: #fdfdfd; flex-shrink: 0; border-radius: 8px; box-shadow: 0 -2px 5px rgba(0,0,0,0.03); }
.chat-input { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px; resize: none; font-family: inherit; font-size: 1em; line-height: 1.4; min-height: 40px; max-height: 120px; overflow-y: auto; }
.send-button { padding: 0 18px; background-color: #5c9ded; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; height: 40px; line-height: 40px; white-space: nowrap; transition: background-color 0.2s;}
.send-button:hover { background-color: #4a8ad8; } .send-button:disabled { background-color: #aaa; }
</style>