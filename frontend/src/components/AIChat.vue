<template>
  <div class="ai-chat-container" :class="{ 'is-open': isOpen }">
    <!-- Floating Toggle Button -->
    <button @click="isOpen = !isOpen" class="chat-toggle" :class="{ 'has-unread': hasUnread }">
      <span v-if="!isOpen" class="toggle-icon">🤖</span>
      <span v-else class="toggle-icon">✕</span>
      <span class="toggle-label" v-if="!isOpen">AI Autopilot</span>
    </button>

    <!-- Chat Window -->
    <div v-if="isOpen" class="chat-window">
      <div class="chat-header">
        <div class="header-info">
          <span class="bot-avatar">🤖</span>
          <div>
            <h3>DNS Autopilot</h3>
            <span class="status-online">Powered by GPT-4o</span>
          </div>
        </div>
        <button @click="isOpen = false" class="close-btn">✕</button>
      </div>

      <div class="chat-messages" ref="messageContainer">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
          <div class="message-content">
            {{ msg.content }}
          </div>
        </div>
        <div v-if="isLoading" class="message assistant loading">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage"
          placeholder="Pýtaj sa na DNS..." 
          :disabled="isLoading"
        />
        <button @click="sendMessage" :disabled="isLoading || !userInput.trim()" class="send-btn">
          <span v-if="!isLoading">→</span>
          <span v-else class="btn-loader"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import api from '../api/api';

const props = defineProps({
  domain: String // Optional: if provided, context is locked to this domain
});

const isOpen = ref(false);
const hasUnread = ref(false);
const userInput = ref('');
const isLoading = ref(false);
const messageContainer = ref(null);

const messages = ref([
  { role: 'assistant', content: 'Ahoj! Som tvoj AI Autopilot. Ako ti môžem pomôcť s tvojimi DNS záznamami?' }
]);

const scrollToBottom = async () => {
  await nextTick();
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  const currentQuery = userInput.value;
  messages.value.push({ role: 'user', content: currentQuery });
  userInput.value = '';
  isLoading.value = true;
  await scrollToBottom();

  try {
    // Collect history (last 5 messages)
    const history = messages.value.slice(-6, -1).map(m => ({ role: m.role, content: m.content }));
    
    const res = await api.post('/ai/chat', {
      query: currentQuery,
      domain: props.domain || 'all',
      history: history
    });

    messages.value.push({ role: 'assistant', content: res.data.response });
  } catch (err) {
    messages.value.push({ role: 'assistant', content: 'Prepáč, vyskytla sa chyba pri komunikácii s AI.' });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};

watch(isOpen, (newVal) => {
  if (newVal) {
    hasUnread.value = false;
    scrollToBottom();
  }
});
</script>

<style scoped>
.ai-chat-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  font-family: inherit;
}

/* ── Toggle Button ──────────────── */
.chat-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: rgba(99, 102, 241, 0.9);
  border: none;
  border-radius: 50px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.chat-toggle:hover {
  transform: translateY(-4px) scale(1.05);
  background: #4f46e5;
}

.toggle-icon { font-size: 1.25rem; }

/* ── Chat Window ───────────────── */
.chat-window {
  position: absolute;
  bottom: 4.5rem;
  right: 0;
  width: 380px;
  height: 550px;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(25px) saturate(180%);
  -webkit-backdrop-filter: blur(25px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.chat-header {
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-info { display: flex; align-items: center; gap: 0.75rem; }
.bot-avatar { font-size: 1.5rem; }
.chat-header h3 { margin: 0; font-size: 0.95rem; color: #f8fafc; }
.status-online { font-size: 0.7rem; color: #818cf8; opacity: 0.8; }

.close-btn { background: none; border: none; color: rgba(255, 255, 255, 0.3); cursor: pointer; font-size: 1rem; }

/* ── Messages ─────────────────── */
.chat-messages {
  flex: 1;
  padding: 1.25rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 85%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.assistant {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
  border-bottom-left-radius: 4px;
}

.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border-bottom-right-radius: 4px;
}

/* ── Input ────────────────────── */
.chat-input-area {
  padding: 1.25rem;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  gap: 0.75rem;
}

.chat-input-area input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 0.6rem 1rem;
  color: white;
  outline: none;
  font-size: 0.9rem;
}

.send-btn {
  width: 40px; height: 40px;
  background: #6366f1;
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.send-btn:hover:not(:disabled) { background: #4f46e5; transform: scale(1.05); }
.send-btn:disabled { opacity: 0.4; }

/* ── Loading ─────────────────── */
.typing-indicator { display: flex; gap: 4px; }
.typing-indicator span {
  width: 6px; height: 6px; background: rgba(255, 255, 255, 0.3);
  border-radius: 50%; animation: bounce 1.4s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@media (max-width: 480px) {
  .chat-window {
    width: calc(100vw - 2rem);
    height: 60vh;
    bottom: 4rem;
  }
}
</style>
