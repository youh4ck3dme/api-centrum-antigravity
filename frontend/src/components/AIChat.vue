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
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999; /* Maximal visibility */
  font-family: inherit;
}

/* ── Toggle Button ──────────────── */
.chat-toggle {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  color: white;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4), 0 10px 25px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  animation: pulse-glow 3s infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.4); }
  50% { box-shadow: 0 0 30px rgba(99, 102, 241, 0.7); transform: scale(1.02); }
}
.chat-toggle:hover {
  transform: translateY(-4px) scale(1.05);
  background: #4f46e5;
}

.toggle-icon { font-size: 1.25rem; }

/* ── Chat Window ───────────────── */
.chat-window {
  position: absolute;
  bottom: 4rem;
  right: 0;
  width: 305px; /* ~20% smaller than 380px */
  height: 440px; /* ~20% smaller than 550px */
  background: rgba(10, 10, 18, 0.88);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6), 0 0 15px rgba(99, 102, 241, 0.1);
  overflow: hidden;
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: bottom right;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px) scale(0.9); filter: blur(10px); }
  to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
}

.chat-header {
  padding: 0.9rem 1.1rem;
  background: linear-gradient(to bottom, rgba(99, 102, 241, 0.1), transparent);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-info { display: flex; align-items: center; gap: 0.6rem; }
.bot-avatar { font-size: 1.2rem; filter: drop-shadow(0 0 4px #6366f1); }
.chat-header h3 { margin: 0; font-size: 0.85rem; color: #fff; font-weight: 700; letter-spacing: -0.01em; }
.status-online { font-size: 0.65rem; color: #a5b4fc; opacity: 0.9; display: flex; align-items: center; gap: 0.3rem; }
.status-online::before { content: ''; width: 6px; height: 6px; background: #4ade80; border-radius: 50%; box-shadow: 0 0 5px #4ade80; }

.close-btn { 
  background: rgba(255, 255, 255, 0.05); border: none; 
  color: rgba(255, 255, 255, 0.5); width: 24px; height: 24px;
  border-radius: 50%; cursor: pointer; font-size: 0.75rem; 
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.close-btn:hover { background: rgba(248, 113, 113, 0.2); color: #f87171; }

/* ── Messages ─────────────────── */
.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  scrollbar-width: none;
}
.chat-messages::-webkit-scrollbar { display: none; }

.message {
  max-width: 90%;
  padding: 0.65rem 0.9rem;
  border-radius: 16px;
  font-size: 0.85rem;
  line-height: 1.45;
  position: relative;
}

.assistant {
  align-self: flex-start;
  background: rgba(30, 30, 46, 0.6);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom-left-radius: 4px;
}

.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

/* ── Input ────────────────────── */
.chat-input-area {
  padding: 0.9rem 1.1rem;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  gap: 0.6rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.chat-input-area input {
  flex: 1;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 0.5rem 0.8rem;
  color: #fff;
  outline: none;
  font-size: 0.82rem;
  transition: border-color 0.2s;
}
.chat-input-area input:focus { border-color: rgba(99, 102, 241, 0.5); }

.send-btn {
  width: 34px; height: 34px;
  background: #6366f1;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.send-btn:hover:not(:disabled) { background: #4f46e5; transform: scale(1.05); box-shadow: 0 0 10px rgba(99, 102, 241, 0.4); }
.send-btn:disabled { opacity: 0.3; }

/* ── Loading ─────────────────── */
.typing-indicator { display: flex; gap: 4px; padding: 4px; }
.typing-indicator span {
  width: 5px; height: 5px; background: #818cf8;
  border-radius: 50%; animation: bounce 1.4s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@media (max-width: 480px) {
  .ai-chat-container { bottom: 1rem; right: 1rem; }
  .chat-window {
    width: calc(100vw - 2rem);
    height: 60vh;
    bottom: 4rem;
  }
}
</style>
