import { computed, type Ref } from 'vue';
import type { RouteLocationNormalizedLoaded } from 'vue-router';

const DEFAULT_AUTH_REDIRECT = '/';
const LOGIN_PATH = '/login';

export const sanitizeAuthRedirect = (redirect: unknown) => {
  const normalized = typeof redirect === 'string' ? redirect : DEFAULT_AUTH_REDIRECT;
  if (!normalized.startsWith('/') || normalized.startsWith('//') || normalized === LOGIN_PATH) {
    return DEFAULT_AUTH_REDIRECT;
  }
  return normalized;
};

export const useAuthRedirect = (route: Ref<RouteLocationNormalizedLoaded>) => {
  const redirectTarget = computed(() => sanitizeAuthRedirect(route.value.query.redirect));

  return {
    redirectTarget,
  };
};
