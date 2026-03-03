<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar -->
    <nav class="bg-blue-800 text-white shadow-md p-4 flex items-center justify-between">
      <h1 class="text-xl font-bold">API Centrum - Domain & SSL Manager</h1>
      <div class="flex gap-1 bg-blue-900/50 p-1 rounded-lg">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="currentTab = tab.id"
          class="px-4 py-1.5 rounded-md text-sm font-medium transition-all"
          :class="currentTab === tab.id ? 'bg-white text-blue-800 shadow-sm' : 'text-blue-100 hover:bg-blue-700/50'"
        >
          {{ tab.name }}
        </button>
      </div>
    </nav>

    <!-- Content -->
    <main class="max-w-6xl mx-auto mt-6 bg-white shadow-sm rounded-xl border min-h-[600px]">
      <Domains v-if="currentTab === 'domains'" />
      <Backups v-if="currentTab === 'backups'" />
      <Performance v-if="currentTab === 'performance'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from "vue";
import Domains from "./views/Domains.vue";
import Backups from "./views/Backups.vue";
import Performance from "./views/Performance.vue";

const currentTab = ref('domains');
const tabs = [
  { id: 'domains', name: 'Domény' },
  { id: 'backups', name: 'Zálohy' },
  { id: 'performance', name: 'Výkon' }
];
</script>
