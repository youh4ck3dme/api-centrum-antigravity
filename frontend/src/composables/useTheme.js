import { ref, watch } from 'vue';

const isDark = ref(
  localStorage.getItem('theme') === 'dark' ||
  (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)
);

watch(isDark, (val) => {
  if (val) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('theme', 'light');
  }
}, { immediate: true });

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value;
  };

  return {
    isDark,
    toggleTheme
  };
}
