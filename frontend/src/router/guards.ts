import type { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { sanitizeAuthRedirect } from '@/composables/useAuthRedirect';

const LOGIN_PATH = '/login';
const SETTINGS_DEFAULT_PATH = '/settings/system';

const LEGACY_SETTINGS_REDIRECTS: Record<string, string> = {
  '/settings': SETTINGS_DEFAULT_PATH,
  '/settings/': SETTINGS_DEFAULT_PATH,
  '/settings/test': '/settings/cfst',
  '/settings/test/': '/settings/cfst',
};

const getRedirectTarget = (to: RouteLocationNormalized) => sanitizeAuthRedirect(to.query.redirect);


const getLegacySettingsRedirect = (path: string) => LEGACY_SETTINGS_REDIRECTS[path] || null;

const handleLegacySettingsRedirect = (to: RouteLocationNormalized, next: NavigationGuardNext) => {
  const redirectPath = getLegacySettingsRedirect(to.path);
  if (!redirectPath) {
    return false;
  }

  next({
    path: redirectPath,
    replace: true,
    query: to.query,
    hash: to.hash,
  });
  return true;
};

const handleGuestOnlyRoute = (to: RouteLocationNormalized, authStore: ReturnType<typeof useAuthStore>, next: NavigationGuardNext) => {
  if (!to.meta.guestOnly) {
    return false;
  }

  if (authStore.isAuthenticated) {
    next(getRedirectTarget(to));
    return true;
  }

  return false;
};

const handleProtectedRoute = async (to: RouteLocationNormalized, authStore: ReturnType<typeof useAuthStore>, next: NavigationGuardNext) => {
  if (!to.meta.requiresAuth) {
    return false;
  }

  if (authStore.isAuthenticated) {
    return false;
  }

  try {
    await authStore.checkAuth();
    if (authStore.isAuthenticated) {
      return false;
    }
  } catch {
    // ignore and fall through to login redirect
  }

  next({
    path: LOGIN_PATH,
    query: { redirect: to.fullPath },
  });
  return true;
};

export const registerRouterGuards = (router: Router) => {
  router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore();

    if (handleLegacySettingsRedirect(to, next)) {
      return;
    }

    await authStore.checkAuth();

    if (handleGuestOnlyRoute(to, authStore, next)) {
      return;
    }

    if (await handleProtectedRoute(to, authStore, next)) {
      return;
    }

    next();
  });
};
