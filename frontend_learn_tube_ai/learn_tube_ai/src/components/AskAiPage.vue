<!-- FILE: src/components/AskAiPage.vue - WORKING BASE + EXPLAIN TEXT LOGIC -->
<template>
  <div class="notebook-page ask-ai-page">
    <h3 class="page-title">Ask the AI</h3>
    
    <!-- This wrapper takes available space and is relative parent for scroll area -->
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
import { ref, nextTick, defineProps, watch, defineEmits, onMounted, onActivated } from 'vue';

const props = defineProps({
  currentContentId: { type: [String, null], default: null },
  textForExplanation: { type: String, default: null }
});
const emit = defineEmits(['explanation-query-handled']);

const messages = ref([]); 
const userInput = ref('');
const chatHistoryContainer = ref(null); // Assuming you have this ref in your template
const isLoadingMessages = ref(false); // Assuming these are used
const isSending = ref(false);         
const isExplaining = ref(false);      
const chatInputTextareaRef = ref(null); // Assuming you have this ref
const MAX_TEXTAREA_ROWS = 5; // Assuming this is used

// This ref tracks the ID for which the current 'messages' are valid.
const chatIsForContentId = ref(null); 

// Helper functions (scrollToBottom, autoGrowTextarea) - ensure they are defined or imported
const scrollToBottom = () => { /* ... your existing implementation ... */ };
const autoGrowTextarea = () => { /* ... your existing implementation ... */ };

function syncChatStateWithContentId(newContentId) {
  console.log(`AskAiPage: syncChatState. Current chat is for: '${chatIsForContentId.value}'. New incoming content ID: '${newContentId}'`);
  
  if (newContentId !== chatIsForContentId.value) {
    console.log(`AskAiPage: Content ID mismatch or change detected. Clearing chat messages and input.`);
    messages.value = [];
    userInput.value = '';
    chatIsForContentId.value = newContentId;
    // Future: Load chat for newContentId
  } else {
    console.log(`AskAiPage: Content ID '${newContentId}' is the same as current '${chatIsForContentId.value}'. Chat preserved.`);
  }
}

// sendMessage, handleEnterKey, processExplainTextProp - keep your existing implementations
// Ensure sendMessage logs `chatIsForContentId.value`
const sendMessage = async () => { 
    const text = userInput.value.trim();
    if (!text || isSending.value) return;
    isSending.value = true;
    messages.value.push({ sender: 'user', text: text });
    const textToSend = userInput.value; 
    userInput.value = ''; 
    nextTick(() => { /* ... autoGrow and scroll ... */ });
    
    console.log("AskAiPage: Sending regular user message:", textToSend, "for contentId:", chatIsForContentId.value); // Use chatIsForContentId
    setTimeout(() => {
        messages.value.push({ sender: 'ai', text: `Mock AI response to your question: "${textToSend}".`});
        isSending.value = false;
        nextTick(scrollToBottom); 
    }, 800 + Math.random() * 700);
};
const handleEnterKey = (event) => { /* ... */ };
const processExplainTextProp = async (textToExplain) => { /* ... your existing implementation, ensure it uses props.currentContentId for context if needed ... */ };


onMounted(() => {
  console.log("AskAiPage MOUNTED. Initial props.currentContentId:", props.currentContentId);
  syncChatStateWithContentId(props.currentContentId);
  scrollToBottom(); 
  nextTick(autoGrowTextarea); 
  if (props.textForExplanation) {
    processExplainTextProp(props.textForExplanation);
  }
});

onActivated(() => {
  console.log("AskAiPage ACTIVATED. Current props.currentContentId:", props.currentContentId, "Chat is for:", chatIsForContentId.value);
  syncChatStateWithContentId(props.currentContentId);
  scrollToBottom();
  nextTick(autoGrowTextarea);
  if (props.textForExplanation) { 
      processExplainTextProp(props.textForExplanation);
  }
});

watch(() => props.currentContentId, (newId, oldId) => {
  console.log(`AskAiPage PROPS WATCHER: props.currentContentId changed from '${oldId}' to '${newId}'`);
  syncChatStateWithContentId(newId);
});

// Watcher for textForExplanation prop
watch(() => props.textForExplanation, (newText, oldText) => {
  console.log("AskAiPage: textForExplanation watcher. New:", `"${newText ? newText.substring(0,20) : 'null'}"`, "Old:", `"${oldText ? oldText.substring(0,20) : 'null'}"`);
  if (newText) { 
    // It's important that processExplainTextProp uses the *current* context
    // or implies a new context related to newText.
    // If an explanation is for a specific content ID, that needs to be handled.
    // For now, it adds to the current message list.
    processExplainTextProp(newText);
  }
});

watch(messages, () => { scrollToBottom(); }, { deep: true });
watch(userInput, () => { nextTick(autoGrowTextarea); });
</script>


<style scoped>
/* STYLES ARE THE SAME as your last provided version that worked well */
.notebook-page.ask-ai-page { width: 100%; flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; padding: 0; box-sizing: border-box;}
.page-title { margin-bottom: 0.4em; color: var(--color-heading); font-weight: 600; font-size: 1.4em; border-bottom: 1px solid #eee; padding-bottom: 0.25em; flex-shrink: 0; text-align: left; }
.ask-ai-chat-wrapper { flex-grow: 1; display: flex; min-height: 0; overflow: hidden; position: relative; background-color: #fff; border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 8px; }
.chat-history-scroll-area { position: absolute; top: 0; left: 0; right: 0; bottom: 0; overflow-y: auto; padding: 10px 15px;}
.chat-message { margin-bottom: 10px; display: flex; }
.message-bubble { padding: 10px 14px; border-radius: 12px; max-width: 85%; box-shadow: 0 1px 1px rgba(0,0,0,0.06); line-height: 1.45; word-wrap: break-word;}
.message-bubble .message-text { margin: 0; white-space: pre-wrap; }
.user-message { justify-content: flex-end; }
.user-message .message-bubble { background-color: #dcf8c6; border-bottom-right-radius: 6px; }
.ai-message { justify-content: flex-start; }
.ai-message .message-bubble { background-color: transparent; box-shadow: none; padding: 2px 0; border-radius: 0; max-width: 100%; color: #333; }
.no-messages-placeholder, .loading-placeholder { text-align: center; color: #888; padding: 30px 10px; font-style: italic; display: flex; align-items: center; justify-content: center; height: 100%;}
.chat-input-area { display: flex; gap: 8px; align-items: flex-end; padding: 8px 10px; border-top: 1px solid #d8dde3; background-color: #f0f2f5; flex-shrink: 0; border-radius: 16px; }
.chat-input { flex-grow: 1; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 14px; resize: none; font-family: inherit; font-size: 1em; line-height: 1.4; max-height: calc(1.4em * 5 + 22px); overflow-y: hidden; background-color: #fff; transition: border-color 0.2s, box-shadow 0.2s, height 0.1s ease-out;}
.chat-input:focus { border-color: #5D8BF4; box-shadow: 0 0 0 2.5px rgba(93, 139, 244, 0.25); outline: none;}
.send-button { background-color: #528BFF; color: white; border: none; border-radius: 50%; cursor: pointer; height: 38px; width: 38px; padding: 0; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background-color 0.2s;}
.send-button svg { width: 18px; height: 18px; }
.send-button .sending-dots { font-weight: bold; font-size: 1.2em; }
.send-button:hover { background-color: #4272d3; } 
.send-button:disabled { background-color: #b0b0b0; cursor: not-allowed; }
</style>