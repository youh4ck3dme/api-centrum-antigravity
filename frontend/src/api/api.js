import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 30000,
});

// ── Retry logic with exponential backoff ──
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

async function retryRequest(error) {
  const config = error.config;
  if (!config || config.__retryCount >= MAX_RETRIES) {
    return Promise.reject(error);
  }
  
  // Only retry on 5xx or network errors
  const status = error.response?.status;
  if (status && status < 500) {
    return Promise.reject(error);
  }
  
  config.__retryCount = (config.__retryCount || 0) + 1;
  const delay = RETRY_DELAY * Math.pow(2, config.__retryCount - 1);
  
  if (import.meta.env.DEV) {
    console.warn(`[API] Retry ${config.__retryCount}/${MAX_RETRIES} for ${config.url} in ${delay}ms`);
  }
  
  await new Promise(resolve => setTimeout(resolve, delay));
  return api(config);
}

// ── Request interceptor ──
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  
  if (import.meta.env.DEV) {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  }
  
  return config;
});

// ── Response interceptor ──
api.interceptors.response.use(
  (res) => {
    if (import.meta.env.DEV) {
      console.log(`[API] ✓ ${res.status} ${res.config.url}`);
    }
    return res;
  },
  async (err) => {
    // Retry on server errors / network failures
    if (!err.response || err.response.status >= 500) {
      try {
        return await retryRequest(err);
      } catch (retryErr) {
        // All retries exhausted — fall through
        err = retryErr;
      }
    }
    
    if (err.response?.status === 401) {
      // Try refresh token first
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken && !err.config.__isRetryAuth) {
        try {
          const refreshRes = await axios.post(
            `${import.meta.env.VITE_API_URL || "/api"}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          localStorage.setItem("access_token", refreshRes.data.access_token);
          err.config.__isRetryAuth = true;
          err.config.headers.Authorization = `Bearer ${refreshRes.data.access_token}`;
          return api(err.config);
        } catch {
          // Refresh failed — clear and redirect
        }
      }
      
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      if (typeof window !== "undefined") {
        window.location.href = "/";
      }
    }
    return Promise.reject(err);
  }
);

export default api;
