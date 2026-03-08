<template>
  <div class="notes-root">

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2 class="page-title">Poznámky</h2>
        <p class="page-sub">
          {{ notes.length }} poznámok &nbsp;·&nbsp; {{ storageUsed }} KB / 4 900 KB
        </p>
      </div>
      <button @click="addNote" class="btn-new">📝 Nová poznámka</button>
    </div>

    <!-- Empty state -->
    <div v-if="notes.length === 0" class="empty-state">
      <span style="font-size:2.5rem">📝</span>
      <span>Žiadne poznámky</span>
      <span style="font-size:0.8rem;color:#64748b">Kliknite na "Nová poznámka" pre začiatok.</span>
    </div>

    <!-- Notes grid -->
    <div v-else class="notes-grid">
      <div
        v-for="note in notes"
        :key="note.id"
        class="note-card"
        :class="{ editing: editingId === note.id }"
        @click="openNote(note.id)"
      >
        <!-- Card header -->
        <div class="note-header">
          <input
            class="note-title-input"
            v-model="note.title"
            placeholder="Názov poznámky..."
            @click.stop
            @input="scheduleSave(note)"
          />
          <button class="btn-delete" @click.stop="deleteNote(note.id)" title="Zmazať">🗑</button>
        </div>

        <!-- Preview mode -->
        <p v-if="editingId !== note.id" class="note-preview">
          {{ note.body ? note.body.slice(0, 160) : 'Kliknite pre úpravu...' }}
        </p>

        <!-- Edit mode -->
        <textarea
          v-else
          class="note-textarea"
          v-model="note.body"
          placeholder="Napíšte poznámku..."
          @click.stop
          @input="scheduleSave(note)"
          :ref="el => { if (el && editingId === note.id) activeTextarea = el }"
        ></textarea>

        <!-- Footer -->
        <div class="note-footer">
          <span class="note-date">{{ formatDate(note.updatedAt) }}</span>
          <transition name="saved-fade">
            <span v-if="savedId === note.id" class="note-saved">✓ Uložené</span>
          </transition>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';

const LS_KEY = 'apcentrum_notes';

const loadNotes = () => {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); }
  catch { return []; }
};

const notes = ref(loadNotes());
const editingId = ref(null);
const savedId = ref(null);
let activeTextarea = null;
let saveTimer = null;
let savedTimer = null;

const saveAll = () => {
  localStorage.setItem(LS_KEY, JSON.stringify(notes.value));
};

const scheduleSave = (note) => {
  note.updatedAt = new Date().toISOString();
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    saveAll();
    savedId.value = note.id;
    clearTimeout(savedTimer);
    savedTimer = setTimeout(() => { savedId.value = null; }, 1500);
  }, 600);
};

const addNote = async () => {
  const id = Date.now().toString();
  notes.value.unshift({ id, title: '', body: '', updatedAt: new Date().toISOString() });
  saveAll();
  editingId.value = id;
  await nextTick();
  if (activeTextarea) activeTextarea.focus();
};

const openNote = async (id) => {
  editingId.value = id;
  await nextTick();
  if (activeTextarea) activeTextarea.focus();
};

const deleteNote = (id) => {
  if (!confirm('Zmazať túto poznámku?')) return;
  notes.value = notes.value.filter(n => n.id !== id);
  if (editingId.value === id) editingId.value = null;
  saveAll();
};

const formatDate = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleString('sk-SK', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

const storageUsed = computed(() => {
  const str = localStorage.getItem(LS_KEY) || '';
  return (new Blob([str]).size / 1024).toFixed(1);
});
</script>

<style scoped>
.notes-root { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
@media (max-width: 480px) { .notes-root { padding: 1rem 0.5rem; gap: 1rem; } }

.page-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; }
.page-title  { font-size: 1.5rem; font-weight: 700; color: #f1f5f9; margin: 0; }
.page-sub    { font-size: 0.85rem; color: #94a3b8; margin: 0.2rem 0 0; }
@media (max-width: 480px) {
  .page-title { font-size: 1.2rem; }
}

.btn-new {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(99,102,241,0.25); border: 1px solid rgba(99,102,241,0.4);
  color: #a5b4fc; padding: 0.5rem 1.1rem; border-radius: 8px;
  cursor: pointer; font-size: 0.85rem; font-weight: 600;
  transition: background 0.2s;
}
.btn-new:hover { background: rgba(99,102,241,0.4); }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.75rem; padding: 3rem; color: #64748b; font-size: 0.9rem;
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
@media (max-width: 640px) { .notes-grid { grid-template-columns: 1fr; } }
@media (min-width: 641px) and (max-width: 1023px) { .notes-grid { grid-template-columns: repeat(2, 1fr); } }

.note-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  backdrop-filter: blur(12px);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  display: flex; flex-direction: column; gap: 0.6rem;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  min-height: 140px;
}
.note-card:hover { border-color: rgba(255,255,255,0.18); background: rgba(255,255,255,0.07); }
.note-card.editing {
  background: rgba(255,255,255,0.08);
  border-color: rgba(99,102,241,0.45);
  cursor: default;
}

.note-header { display: flex; align-items: center; gap: 0.5rem; }
.note-title-input {
  flex: 1; background: transparent; border: none; outline: none;
  color: #f1f5f9; font-size: 0.9rem; font-weight: 600;
}
.note-title-input::placeholder { color: #64748b; }

.btn-delete {
  background: none; border: none; cursor: pointer;
  font-size: 0.9rem; opacity: 0.4; transition: opacity 0.15s; padding: 0.15rem;
}
.btn-delete:hover { opacity: 1; }

.note-preview {
  flex: 1; font-size: 0.8rem; color: #94a3b8; line-height: 1.5;
  white-space: pre-wrap; word-break: break-word;
  overflow: hidden; display: -webkit-box;
  -webkit-line-clamp: 4; -webkit-box-orient: vertical;
}

.note-textarea {
  flex: 1; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  color: #e2e8f0; font-size: 0.82rem; line-height: 1.6;
  padding: 0.6rem 0.75rem; resize: vertical; min-height: 120px;
  font-family: inherit; outline: none;
  transition: border-color 0.2s;
}
.note-textarea:focus { border-color: rgba(99,102,241,0.5); }

.note-footer { display: flex; justify-content: space-between; align-items: center; }
.note-date  { font-size: 0.7rem; color: #475569; }
.note-saved { font-size: 0.7rem; color: #4ade80; font-weight: 600; }

.saved-fade-enter-active, .saved-fade-leave-active { transition: opacity 0.3s; }
.saved-fade-enter-from, .saved-fade-leave-to { opacity: 0; }
</style>
