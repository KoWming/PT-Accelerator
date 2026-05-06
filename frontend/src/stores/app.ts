import { defineStore } from 'pinia';
import { ref } from 'vue';

type ThemeMode = 'system' | 'dark' | 'light';

export const useAppStore = defineStore('app', () => {
  const theme = ref<ThemeMode>('system');
  const sidebarCollapsed = ref(false);
  const language = ref('zh-CN');

  const setTheme = (value: ThemeMode) => {
    theme.value = value;
  };

  const setSidebarCollapsed = (value: boolean) => {
    sidebarCollapsed.value = value;
  };

  return { theme, sidebarCollapsed, language, setTheme, setSidebarCollapsed };
});
