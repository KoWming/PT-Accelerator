import { settings } from '@/api';
import type { Ref } from 'vue';
import type { AuthFormState, PageFeedback, SettingPageKey } from '@/types/settings';
import { getErrorMessage } from '@/utils/error';

interface UseSettingsAuthActionsOptions {
  authInitialized: Ref<boolean>;
  authForm: AuthFormState;
  savingAuth: Ref<boolean>;
  toast: {
    success: (message: string) => void;
    error: (message: string) => void;
  };
  ensurePageDataReady: (section: SettingPageKey) => Promise<void>;
  markPageDataStale: (section: SettingPageKey) => void;
  setPageStatusBanner: (
    title: string,
    message: string,
    status?: PageFeedback['status']
  ) => void;
}

export const useSettingsAuthActions = ({
  authInitialized,
  authForm,
  savingAuth,
  toast,
  ensurePageDataReady,
  markPageDataStale,
  setPageStatusBanner,
}: UseSettingsAuthActionsOptions) => {
  const reloadAuthSection = async (
    title: string,
    message: string,
    toastMessage?: string
  ) => {
    markPageDataStale('system');
    await ensurePageDataReady('system');
    setPageStatusBanner(title, message);
    if (toastMessage) {
      toast.success(toastMessage);
    }
  };

  const saveAuthSettings = async () => {
    const username = (authForm.username || '').trim();
    const hasPasswordInput = Boolean(authForm.new_password || authForm.confirm_password);

    if (!username) {
      toast.error('管理员用户名不能为空');
      return;
    }

    if (authForm.new_password && authForm.new_password !== authForm.confirm_password) {
      toast.error('两次输入的密码不一致');
      return;
    }

    if (!authInitialized.value && !authForm.new_password) {
      toast.error('请先设置初始化密码');
      return;
    }

    if (authInitialized.value && hasPasswordInput && !authForm.current_password) {
      toast.error('修改密码时必须输入当前密码');
      return;
    }

    savingAuth.value = true;
    try {
      const wasInitialized = authInitialized.value;

      await settings.updateConfig({
        auth: {
          username,
        },
      });

      if (authForm.new_password) {
        await settings.changePassword(authForm.new_password, authForm.current_password || undefined);
        authInitialized.value = true;
      }

      await reloadAuthSection(
        '安全与认证已保存',
        wasInitialized ? '管理员账号与密码策略已更新。' : '管理员初始化已完成，后续请使用当前凭据登录后台。',
        wasInitialized ? '管理员设置已保存' : '管理员初始化已完成'
      );

      authForm.current_password = '';
      authForm.new_password = '';
      authForm.confirm_password = '';
    } catch (e: any) {
      const message = getErrorMessage(e, '保存失败');
      setPageStatusBanner('安全与认证保存失败', message, 'error');
      toast.error('保存失败: ' + message);
    } finally {
      savingAuth.value = false;
    }
  };

  return {
    saveAuthSettings,
  };
};
