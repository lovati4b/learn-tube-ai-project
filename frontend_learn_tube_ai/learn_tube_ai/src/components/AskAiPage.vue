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
import { ref, nextTick, onMounted, watch, onActivated } from 'vue';

// --- Props and Emits for "Explain Selected Text" ---
const props = defineProps({
  textForExplanation: { 
    type: String,
    default: null
  }
});
const emit = defineEmits(['explanation-query-handled']);
// --- End Props and Emits ---

const messages = ref([]); 
const userInput = ref('');
const chatHistoryContainer = ref(null);
const isLoadingMessages = ref(false); // For future use if loading history
const isSending = ref(false);         // For user typed messages
const isExplaining = ref(false);      // For "Explain Selected Text" loading/processing state

const chatInputTextareaRef = ref(null); 
const MAX_TEXTAREA_ROWS = 5; 

const scrollToBottom = () => { 
  nextTick(() => { 
    if (chatHistoryContainer.value) {
      chatHistoryContainer.value.scrollTop = chatHistoryContainer.value.scrollHeight; 
    } 
  });
};

const autoGrowTextarea = () => { 
  const textarea = chatInputTextareaRef.value; 
  if (textarea) { 
    textarea.style.height = 'auto'; 
    const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || 20; 
    const scrollHeight = textarea.scrollHeight; 
    const contentHeight = scrollHeight - parseFloat(getComputedStyle(textarea).paddingTop) - parseFloat(getComputedStyle(textarea).paddingBottom); 
    const calculatedRows = Math.round(contentHeight / lineHeight); 
    textarea.rows = Math.max(1, Math.min(calculatedRows, MAX_TEXTAREA_ROWS)); 
    textarea.style.height = `${textarea.scrollHeight}px`; 
    if (calculatedRows > MAX_TEXTAREA_ROWS) { 
      textarea.style.overflowY = 'auto'; 
    } else { 
      textarea.style.overflowY = 'hidden'; 
    } 
  }
};

const sendMessage = async () => { 
    const text = userInput.value.trim();
    if (!text || isSending.value) return;
    isSending.value = true;
    messages.value.push({ sender: 'user', text: text });
    const textToSend = userInput.value; 
    userInput.value = ''; 
    nextTick(() => { 
        if (chatInputTextareaRef.value) { 
            chatInputTextareaRef.value.style.height = 'auto'; 
            chatInputTextareaRef.value.rows = 1; 
            autoGrowTextarea(); 
        } 
        scrollToBottom(); 
    });
    
    // Simulate backend call for regular chat
    console.log("AskAiPage: Sending regular user message:", textToSend);
    setTimeout(() => {
        messages.value.push({ sender: 'ai', text: `Mock AI response to your question: "${textToSend}".`});
        isSending.value = false;
        nextTick(scrollToBottom); 
    }, 800 + Math.random() * 700);
};

const handleEnterKey = (event) => { if (event.shiftKey) { return; } event.preventDefault(); sendMessage();};

// --- Function to process explained text from prop ---
const processExplainTextProp = async (textToExplain) => {
  if (textToExplain && !isExplaining.value) { 
    console.log("AskAiPage: Processing textForExplanation prop:", `"${textToExplain.substring(0,50)}..."`);
    isExplaining.value = true; 

    messages.value.push({ sender: 'user', text: `Please explain this from the transcript: "${textToExplain}"` });
    nextTick(scrollToBottom);

    try {
      console.log("AskAiPage: Calling backend /api/explain_text with:", textToExplain);
      const response = await fetch('http://localhost:5000/api/explain_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            selected_text: textToExplain, 
            // current_video_id: "PASS_VIDEO_ID_HERE_IF_NEEDED_FROM_APP_VUE_PROPS" 
        })
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({ explanation: "Error from explanation server." }));
        throw new Error(errData.details || errData.error || `HTTP error ${response.status}`);
      }
      const data = await response.json();
      messages.value.push({ sender: 'ai', text: data.explanation || "No explanation received." });
    } catch (error) {
      console.error("AskAiPage: Error fetching explanation:", error);
      messages.value.push({ sender: 'ai', text: `Sorry, I couldn't get an explanation: ${error.message}` });
    } finally {
      isExplaining.value = false;
      nextTick(scrollToBottom);
      emit('explanation-query-handled'); 
      console.log("AskAiPage: Emitted explanation-query-handled");
    }
  } else if (textToExplain && isExplaining.value) {
    console.log("AskAiPage: Explanation already in progress for:", textToExplain);
  } else if (!textToExplain) {
    console.log("AskAiPage: processExplainTextProp called with null/empty text. Doing nothing.");
  }
};

// --- Watcher and Lifecycle Hooks ---
watch(() => props.textForExplanation, (newText, oldText) => {
  console.log("AskAiPage: textForExplanation watcher. New:", `"${newText}"`, "Old:", `"${oldText}"`);
  // Only process if newText is truthy and different from the one being processed or just processed.
  // The isExplaining flag and Notebook.vue clearing the prop are the main guards.
  if (newText) { 
    processExplainTextProp(newText);
  }
});

watch(messages, () => { scrollToBottom(); }, { deep: true });
watch(userInput, () => { nextTick(autoGrowTextarea); });

onMounted(() => { 
  scrollToBottom(); 
  nextTick(autoGrowTextarea); 
  console.log("AskAiPage MOUNTED. Initial textForExplanation:", props.textForExplanation);
  if (props.textForExplanation) {
    processExplainTextProp(props.textForExplanation);
  }
});
onActivated(() => { 
  scrollToBottom();
  nextTick(autoGrowTextarea);
  console.log("AskAiPage ACTIVATED. Current textForExplanation:", props.textForExplanation);
  if (props.textForExplanation) { 
      processExplainTextProp(props.textForExplanation);
  }
});
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