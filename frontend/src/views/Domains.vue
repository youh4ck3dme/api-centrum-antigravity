<template>
  <div class="p-4">
    <h2 class="text-xl font-semibold mb-3">Domény</h2>
    <div class="mb-3">
      <button
        @click="fetchDomains"
        class="bg-blue-600 text-white px-3 py-1 rounded"
      >
        Načítať domény
      </button>
    </div>

    <div v-if="loading">Načítavam...</div>

    <div v-else>
      <div v-if="domains && domains.length">
        <div v-for="d in domains" :key="d.id" class="border p-2 mb-2">
          <div>
            <strong>{{ d.name }}</strong>
          </div>
          <div v-if="d.description">{{ d.description }}</div>
        </div>
      </div>
      <div v-else>Žiadne domény.</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/api";

const domains = ref([]);
const loading = ref(false);

const fetchDomains = async () => {
  loading.value = true;
  try {
    const res = await api.get("/domains");
    domains.value = res.data.domains || res.data;
  } catch (err) {
    console.error(err);
    alert("Chyba pri načítaní domén.");
  } finally {
    loading.value = false;
  }
};
</script>
