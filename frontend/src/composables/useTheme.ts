type ThemeMode = 'system' | 'dark' | 'light';

const getSystemPrefersDark = () => {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return true;
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

export const applyThemeMode = (themeMode: ThemeMode) => {
  if (typeof document === 'undefined') return;

  const shouldUseDark = themeMode === 'system' ? getSystemPrefersDark() : themeMode === 'dark';
  document.body.classList.toggle('light-theme', !shouldUseDark);
};

export const useTheme = () => {
  const getSavedTheme = (): ThemeMode => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme === 'light' || savedTheme === 'dark' || savedTheme === 'system' ? savedTheme : 'system';
  };

  const applySavedTheme = () => applyThemeMode(getSavedTheme());

  return { applySavedTheme, applyThemeMode, getSavedTheme };
};
