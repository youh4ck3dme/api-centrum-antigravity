import { ref } from 'vue';
import axios from 'axios';

export function useGithub() {
  const token = ref(localStorage.getItem('ghp_token') || '');
  const profile = ref(null);
  const repos = ref([]);
  const loading = ref(false);
  const error = ref('');

  const GITHUB_API = 'https://api.github.com';

  const setToken = (newToken) => {
    token.value = newToken;
    localStorage.setItem('ghp_token', newToken);
  };

  const logout = () => {
    token.value = '';
    localStorage.removeItem('ghp_token');
    profile.value = null;
    repos.value = [];
  };

  const fetchProfile = async () => {
    if (!token.value) return;
    loading.value = true;
    error.value = '';
    try {
      const res = await axios.get(`${GITHUB_API}/user`, {
        headers: { Authorization: `token ${token.value}` }
      });
      profile.value = res.data;
    } catch (err) {
      error.value = 'Nepodarilo sa načítať GitHub profil. Skontrolujte token.';
      if (err.response?.status === 401) logout();
    } finally {
      loading.value = false;
    }
  };

  const fetchRepos = async () => {
    if (!token.value) return;
    loading.value = true;
    try {
      // Načítame top 50 repozitárov zoradených podľa poslednej aktivity
      const res = await axios.get(`${GITHUB_API}/user/repos`, {
        headers: { Authorization: `token ${token.value}` },
        params: {
          sort: 'updated',
          per_page: 50
        }
      });
      repos.value = res.data;
    } catch (err) {
      error.value = 'Nepodarilo sa načítať repozitáre.';
    } finally {
      loading.value = false;
    }
  };

  const loadAll = async () => {
    await Promise.all([fetchProfile(), fetchRepos()]);
  };

  return {
    token,
    profile,
    repos,
    loading,
    error,
    setToken,
    logout,
    loadAll
  };
}
