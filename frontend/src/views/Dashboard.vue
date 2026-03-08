<template>
  <div class="dash">

    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <div class="stat-icon">{{ stat.icon }}</div>
        <p class="stat-label">{{ stat.label }}</p>
        <p class="stat-value">{{ stat.value }}</p>
        <p class="stat-sub">{{ stat.subValue }}</p>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Recent Activity</span>
        <button class="panel-action">View all</button>
      </div>
      <div v-if="loading" class="empty-state">
        <div class="spinner"></div>
        <span>Načítavam...</span>
      </div>
      <div v-else-if="recentActivity.length === 0" class="empty-state">
        <span style="font-size:1.5rem">📭</span>
        <span>Žiadna aktivita</span>
      </div>
      <ul v-else class="activity-list">
        <li v-for="item in recentActivity" :key="item.id" class="activity-item">
          <div class="act-icon">{{ item.icon }}</div>
          <div class="act-body">
            <p class="act-title">{{ item.title }}</p>
            <p class="act-time">{{ item.time }}</p>
          </div>
          <span class="act-badge">{{ item.status }}</span>
        </li>
      </ul>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api/api";

const stats = ref([
  { label: 'Celkovo domén',  value: '—', subValue: 'načítavam...', icon: '🌐' },
  { label: 'System Status',  value: '—', subValue: 'načítavam...', icon: '⚡' },
  { label: 'Udalosti (7d)', value: '—', subValue: 'posledných 7 dní', icon: '📅' },
]);
const recentActivity = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const [s, a] = await Promise.all([
      api.get("/dashboard/stats"),
      api.get("/dashboard/activities"),
    ]);
    stats.value[0].value = String(s.data.user_stats.total_domains);
    stats.value[0].subValue = 'Websupport domény';
    stats.value[1].value = s.data.system_health.database === 'online' ? 'Online' : 'Offline';
    stats.value[1].subValue = `API: ${s.data.system_health.websupport_api}`;
    stats.value[2].value = String(s.data.user_stats.recent_activities);
    recentActivity.value = a.data.activities.map((x, i) => ({
      id: i, title: x.action,
      time: new Date(x.timestamp).toLocaleString('sk-SK'),
      status: 'Info', icon: '📝',
    }));
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.dash { padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.stat-card {
  padding: 1.5rem;
  border-radius: 20px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 24px rgba(0,0,0,0.3);
  transition: background 0.2s;
}
.stat-card:hover { background: rgba(255,255,255,0.06); }
.stat-icon { font-size: 1.4rem; margin-bottom: 0.75rem; }
.stat-label { font-size: 0.7rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.35); margin-bottom: 0.4rem; }
.stat-value { font-size: 2rem; font-weight: 700; color: rgba(255,255,250,0.92); letter-spacing: -0.03em; line-height: 1; margin-bottom: 0.25rem; }
.stat-sub { font-size: 0.75rem; color: rgba(255,255,255,0.35); }

.panel {
  border-radius: 20px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 24px rgba(0,0,0,0.3);
  overflow: hidden;
}
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.06); }
.panel-title { font-size: 0.875rem; font-weight: 600; color: rgba(255,255,250,0.85); }
.panel-action { background: none; border: none; font-size: 0.75rem; color: rgba(255,255,255,0.35); cursor: pointer; transition: color 0.2s; }
.panel-action:hover { color: rgba(255,255,250,0.7); }

.empty-state { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; padding: 2.5rem; color: rgba(255,255,255,0.3); font-size: 0.85rem; }
.spinner { width: 22px; height: 22px; border: 2px solid rgba(255,255,255,0.1); border-top-color: rgba(255,255,255,0.5); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.activity-list { list-style: none; }
.activity-item { display: flex; align-items: center; gap: 0.875rem; padding: 0.875rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.15s; }
.activity-item:last-child { border-bottom: none; }
.activity-item:hover { background: rgba(255,255,255,0.03); }
.act-icon { width: 36px; height: 36px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,0.06); border-radius: 10px; font-size: 1rem; border: 1px solid rgba(255,255,255,0.07); }
.act-body { flex: 1; min-width: 0; }
.act-title { font-size: 0.85rem; font-weight: 500; color: rgba(255,255,250,0.85); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.act-time { font-size: 0.72rem; color: rgba(255,255,255,0.3); margin-top: 0.15rem; }
.act-badge { flex-shrink: 0; font-size: 0.68rem; font-weight: 600; padding: 0.2rem 0.6rem; border-radius: 999px; background: rgba(255,255,255,0.07); color: rgba(255,255,250,0.45); border: 1px solid rgba(255,255,255,0.08); }
</style>
