import { ref, computed } from 'vue'
import api from '../api/api'

export function useStats() {
  const stats = ref([
    { value: '—', subValue: 'načítavam...', accent: '' },
    { value: '—', subValue: 'načítavam...', accent: '' },
    { value: '—', subValue: '', accent: '' },
    { value: '—', subValue: 'domény do 30 dní', accent: 'accent-warn' },
    { value: '—', subValue: '', accent: '' },
  ])
  const prevValues = ref(['—', '—', '—', '—', '—'])
  const recentActivity = ref([])
  const loading = ref(true)
  const lastUpdated = ref(null)
  const vpsStats = ref(null)
  const dbStatus = ref('unknown')
  const apiStatus = ref('unknown')
  const flashIdx = ref(null)

  const ramPct = computed(() => vpsStats.value
    ? Math.round(vpsStats.value.ram_used_mb / vpsStats.value.ram_total_mb * 100) : 0)

  const ACTION_META = {
    login:       { icon: '🔑', label: 'Login',    color: 'badge-blue' },
    register:    { icon: '👤', label: 'Nový účet', color: 'badge-green' },
    '2fa_enabled': { icon: '🛡️', label: 'Security', color: 'badge-purple' },
    logout:      { icon: '🚪', label: 'Logout',   color: 'badge-gray' },
    backup:      { icon: '💾', label: 'Backup',   color: 'badge-indigo' },
    restore:     { icon: '⏪', label: 'Restore',  color: 'badge-indigo' },
    dns:         { icon: '🌐', label: 'DNS',       color: 'badge-indigo' },
    domain:      { icon: '🌍', label: 'Domain',   color: 'badge-indigo' },
    ssl:         { icon: '🔒', label: 'SSL',       color: 'badge-green' },
  }

  const getActionMeta = (action) => {
    const key = Object.keys(ACTION_META).find(k => action?.toLowerCase().startsWith(k))
    return ACTION_META[key] || { icon: '📝', label: 'Info', color: 'badge-gray' }
  }

  function flashCard(i) {
    flashIdx.value = i
    setTimeout(() => { flashIdx.value = null; }, 600)
  }

  const loadStats = async () => {
    try {
      const [s, a] = await Promise.all([
        api.get("/dashboard/stats"),
        api.get("/dashboard/activities"),
      ])

      const u = s.data.user_stats
      const h = s.data.system_health
      dbStatus.value = h.database
      apiStatus.value = h.websupport_api

      const newValues = [
        String(u.total_domains),
        h.database === 'online' ? 'Online' : 'Offline',
        String(u.recent_activities),
        String(u.expiring_soon ?? 0),
      ]

      newValues.forEach((v, i) => {
        if (v !== prevValues.value[i] && prevValues.value[i] !== '—') flashCard(i);
      })
      prevValues.value = [...newValues, prevValues.value[4] ?? '—'];

      stats.value[0].value = newValues[0];
      stats.value[0].subValue = 'Websupport domény';
      stats.value[0].accent = '';

      stats.value[1].value = newValues[1];
      stats.value[1].subValue = `API: ${h.websupport_api}`;
      stats.value[1].accent = h.database === 'online' ? 'accent-green' : 'accent-red';

      stats.value[2].value = newValues[2];

      const exp = u.expiring_soon ?? 0;
      stats.value[3].value = String(exp);
      stats.value[3].accent = exp > 0 ? 'accent-warn' : 'accent-green';
      stats.value[3].subValue = exp > 0 ? `${exp} domén treba obnoviť` : 'Všetko v poriadku';

      recentActivity.value = a.data.activities.map((x, i) => {
        const meta = getActionMeta(x.action);
        return { id: i, title: x.action, time: new Date(x.timestamp).toLocaleString('sk-SK'), ...meta };
      });

      lastUpdated.value = new Date()
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  const loadVPS = async () => {
    try {
      const res = await api.get("/vps/stats")
      const prev = vpsStats.value?.cpu_percent
      vpsStats.value = res.data
      if (prev !== undefined && Math.abs(res.data.cpu_percent - prev) > 2) flashCard(4)
    } catch {}
  }

  const reload = async () => {
    loading.value = true
    await Promise.all([loadStats(), loadVPS()])
  }

  return {
    stats,
    recentActivity,
    loading,
    lastUpdated,
    vpsStats,
    dbStatus,
    apiStatus,
    flashIdx,
    ramPct,
    loadStats,
    loadVPS,
    reload
  }
}
