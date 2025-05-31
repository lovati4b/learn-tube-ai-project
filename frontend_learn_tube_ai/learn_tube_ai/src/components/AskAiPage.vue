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
const chatHistoryContainer = ref(null); 
const isLoadingMessages = ref(false); 
const isSending = ref(false);         
const isExplaining = ref(false);      
const chatInputTextareaRef = ref(null); 
const MAX_TEXTAREA_ROWS = 5; 
const chatIsForContentId = ref(null);

// Helper functions
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

// Sync function
function syncChatStateWithContentId(newContentId, isInitialSetup = false) {
  console.log(`AskAiPage: syncChatState. Current chat is for: '${chatIsForContentId.value}'. New incoming content ID: '${newContentId}'. InitialSetup: ${isInitialSetup}`);
  
  if (newContentId !== chatIsForContentId.value) {
    console.log(`AskAiPage: Content ID mismatch. Clearing chat messages and input. Old: ${chatIsForContentId.value}, New: ${newContentId}`);
    messages.value = [];
    userInput.value = ''; 
    chatIsForContentId.value = newContentId;
  } else if (isInitialSetup && newContentId === chatIsForContentId.value) {
    console.log(`AskAiPage: Content ID '${newContentId}' is same as current. Chat preserved during sync.`);
  }
}

// Key Functions: sendMessage, handleEnterKey, processExplainTextProp

const sendMessage = async () => { 
    const text = userInput.value.trim();
    // Diagnostic logs
    console.log(`AskAiPage sendMessage: CLICKED. userInput.value="'${userInput.value}'", trimmed text="'${text}'", isSending=${isSending.value}`); 
    if (!text || isSending.value) {
        console.log("AskAiPage sendMessage: Bailing out due to guard condition (!text || isSending.value)."); 
        return;
    }
    
    isSending.value = true; 
    const userMessage = { sender: 'user', text: text }; // Use the trimmed text
    messages.value.push(userMessage);
    
    userInput.value = ''; // Clear input field 
    
    nextTick(() => { 
        if (chatInputTextareaRef.value) { 
            chatInputTextareaRef.value.style.height = 'auto'; 
            chatInputTextareaRef.value.rows = 1; 
            autoGrowTextarea(); 
        } 
        scrollToBottom(); 
    });
    
    console.log("AskAiPage: Sending regular user message (text used for mock):", text, "for contentId:", chatIsForContentId.value);
    
    setTimeout(() => {
        const aiResponse = { sender: 'ai', text: `Mock AI response to your question: "${text}".`}; // Use trimmed 'text'
        messages.value.push(aiResponse);
        isSending.value = false; 
        nextTick(scrollToBottom); 
    }, 800 + Math.random() * 700);
};

const handleEnterKey = (event) => { 
  if (event.shiftKey) { return; } 
  event.preventDefault(); 
  sendMessage();
};

const processExplainTextProp = async (textToExplain, processingForContentId) => {
  console.log(`AskAiPage: processExplainTextProp CALLED. text: "${textToExplain ? textToExplain.substring(0,30) : 'null'}", forContentId: ${processingForContentId}, isExplaining: ${isExplaining.value}`);
  
  if (!textToExplain || typeof textToExplain !== 'string' || !textToExplain.trim()) {
    console.log("AskAiPage: processExplainTextProp - bailing: invalid text.");
    emit('explanation-query-handled'); 
    return;
  }

  if (isExplaining.value) {
    console.log("AskAiPage: processExplainTextProp - bailing: already explaining.");
    return; 
  }
  
  isExplaining.value = true; 
  
  if (processingForContentId !== chatIsForContentId.value) {
      console.warn(`AskAiPage: processExplainTextProp running for ${processingForContentId}, but chatIsForContentId is ${chatIsForContentId.value}. Syncing chat context.`);
      syncChatStateWithContentId(processingForContentId); 
  }
  
  const userMessage = { sender: 'user', text: `Please explain this: "${textToExplain}"` };
  messages.value.push(userMessage);
  console.log('AskAiPage: Pushed user message:', JSON.parse(JSON.stringify(userMessage)));
  
  await nextTick();
  scrollToBottom();
  console.log('AskAiPage: After 1st nextTick for user message.');

  const aiThinkingMessage = { sender: 'ai', text: 'Thinking...' };
  messages.value.push(aiThinkingMessage);
  console.log('AskAiPage: Pushed AI thinking message.');
  let thinkingMessageIndex = messages.value.length - 1;

  await nextTick();
  scrollToBottom();
  console.log('AskAiPage: After 2nd nextTick for thinking message.');

  try {
    console.log("AskAiPage: Calling backend /api/explain_text with text and context ID:", processingForContentId);
    const response = await fetch('http://localhost:5000/api/explain_text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
          selected_text: textToExplain, 
          current_video_id: processingForContentId 
      })
    });
    console.log("AskAiPage: Backend responded with status:", response.status);
    if (!response.ok) { 
      // Enhanced error parsing from response
      let errorDetails = `HTTP error ${response.status}`;
      try {
        const errData = await response.json();
        errorDetails = errData.details || errData.error || errorDetails;
      } catch (e) {
        console.error("AskAiPage: Failed to parse error response as JSON", e);
        // errorDetails remains `HTTP error ${response.status}` or could try response.text()
      }
      throw new Error(errorDetails); 
    }
    const data = await response.json();
    const aiMessage = { sender: 'ai', text: data.explanation || "No explanation received." };
    if(messages.value[thinkingMessageIndex]?.text === 'Thinking...'){
        messages.value.splice(thinkingMessageIndex, 1, aiMessage);
    } else {
        messages.value.push(aiMessage); 
        thinkingMessageIndex = -1; 
    }
    console.log('AskAiPage: Pushed/Spliced AI response.');

  } catch (error) { 
    console.error("AskAiPage: Error fetching explanation:", error); // Log the actual error object
    const errorMsg = { sender: 'ai', text: `Sorry, I couldn't get an explanation: ${error.message}` }; // error.message should be populated now
     if(messages.value[thinkingMessageIndex]?.text === 'Thinking...'){
        messages.value.splice(thinkingMessageIndex, 1, errorMsg);
    } else {
        messages.value.push(errorMsg);
         thinkingMessageIndex = -1;
    }
    console.log('AskAiPage: Pushed/Spliced AI error message.');
  } finally {
    isExplaining.value = false;
    await nextTick(); 
    scrollToBottom();
    emit('explanation-query-handled'); 
    console.log("AskAiPage: Emitted explanation-query-handled.");
  }
};

// Lifecycle Hooks
onMounted(() => {
  console.log("AskAiPage MOUNTED. props.currentContentId:", props.currentContentId, "props.textForExplanation:", props.textForExplanation ? props.textForExplanation.substring(0,20) : null);
  syncChatStateWithContentId(props.currentContentId, true); 
  scrollToBottom(); 
  nextTick(autoGrowTextarea); 
});

onActivated(() => {
  console.log("AskAiPage ACTIVATED. props.currentContentId:", props.currentContentId, "Chat is for:", chatIsForContentId.value, "props.textForExplanation:", props.textForExplanation ? props.textForExplanation.substring(0,20) : null);
  syncChatStateWithContentId(props.currentContentId, true); 
  scrollToBottom();
  nextTick(autoGrowTextarea);
  if (props.textForExplanation && chatIsForContentId.value === props.currentContentId) {
      console.log("AskAiPage (onActivated): textForExplanation is present. Watcher should handle it.");
  }
});

// Watchers
watch(() => props.currentContentId, (newId, oldId) => {
  console.log(`AskAiPage PROPS WATCHER for currentContentId: changed from '${oldId}' to '${newId}'`);
  syncChatStateWithContentId(newId, false); 
});

watch(() => props.textForExplanation, (newText, oldText) => {
  console.log(`AskAiPage WATCHER for textForExplanation: New='${newText ? newText.substring(0,20) : 'null'}', Old='${oldText === undefined ? 'undefined' : (oldText ? oldText.substring(0,20) : 'null')}'`);
  
  if (newText && typeof newText === 'string' && newText.trim()) {
    console.log(`AskAiPage WATCHER: Valid new text. Calling processExplainTextProp for contentId '${props.currentContentId}'.`);
    processExplainTextProp(newText, props.currentContentId);
  } else if (!newText && oldText) { 
    console.log(`AskAiPage WATCHER: textForExplanation was cleared.`);
  }
}, { immediate: true }); 


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