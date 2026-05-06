import { computed, type Ref } from 'vue';
import type {
  AuthFormState,
  BackupFormState,
  CfstFormState,
  CfstResultItem,
  CfstStatusState,
  IkuaiDnsFormState,
  PageOverviewCard,
  PageFeedback,
  SettingPageKey,
  SettingPageMeta
} from '@/types/settings';

interface UseSettingsSectionsOptions {
  activePage: Ref<SettingPageKey>;
  authInitialized: Ref<boolean>;
  authForm: AuthFormState;
  backupForm: BackupFormState;
  cfstForm: CfstFormState;
  cfstStatus: Ref<CfstStatusState>;
  cfstResults: Ref<CfstResultItem[]>;
  cfstBestIp: Ref<string>;
  notifyChannels: Ref<Array<{ enabled?: boolean; type?: string }>>;
  ikuaiDnsForm: IkuaiDnsFormState;
  hasLoadedSystemPage: Ref<boolean>;
  hasLoadedNotifyPage: Ref<boolean>;
  hasLoadedBackupPage: Ref<boolean>;
  hasLoadedCfstPage: Ref<boolean>;
  hasLoadedIkuaiPage: Ref<boolean>;
  getCfstNumberValue: (value: unknown, fallback: number) => number;
  cfstDefaults: {
    threads: number;
    ping_times: number;
    download_count: number;
    min_delay: number;
    max_delay: number;
    show_count: number;
  };
}

const PAGE_META: Record<SettingPageKey, SettingPageMeta> = {
  system: {
    title: '安全与认证',
    description: '单独管理管理员账号与密码，不再把认证能力混在其他系统杂项里。'
  },
  notification: {
    title: '通知渠道',
    description: '按渠道维度维护推送配置、启停状态和测试发送结果。'
  },
  backup: {
    title: '备份设置',
    description: '围绕 WebDAV、自动备份策略和恢复流程管理配置安全。'
  },
  cfst: {
    title: 'CFST 设置',
    description: '集中管理优选参数、运行状态和测速结果，不再把测速链路当成总设置附属项。'
  },
  'ikuai-dns': {
    title: '远程同步管理',
    description: '独立维护爱快 DNS 同步开关、连接参数和测试链路。'
  }
};

export const useSettingsSections = ({
  activePage,
  authInitialized,
  authForm,
  backupForm,
  cfstForm,
  cfstStatus,
  cfstResults,
  cfstBestIp,
  notifyChannels,
  ikuaiDnsForm,
  hasLoadedSystemPage,
  hasLoadedNotifyPage,
  hasLoadedBackupPage,
  hasLoadedCfstPage,
  hasLoadedIkuaiPage,
  getCfstNumberValue,
  cfstDefaults
}: UseSettingsSectionsOptions) => {
  const activePageMeta = computed(() => PAGE_META[activePage.value]);

  const activePageLoaded = computed(() => {
    switch (activePage.value) {
      case 'system':
        return hasLoadedSystemPage.value;
      case 'notification':
        return hasLoadedNotifyPage.value;
      case 'backup':
        return hasLoadedBackupPage.value;
      case 'cfst':
        return hasLoadedCfstPage.value;
      case 'ikuai-dns':
        return hasLoadedIkuaiPage.value;
      default:
        return false;
    }
  });

  const cfstHasError = computed(() => cfstResults.value.some((item) => Boolean(item?.error)));

  const visibleCfstResults = computed(() => {
    const showCount = Math.max(getCfstNumberValue(cfstForm.show_count, cfstDefaults.show_count), 0);

    if (cfstForm.disable_download) {
      const ipResults = cfstResults.value.filter((item) => item?.error || item?.ip);
      return showCount > 0 ? ipResults.slice(0, showCount) : [];
    }

    return cfstResults.value.filter((item) => item?.error || Number(item?.download_speed) > 0);
  });

  const activePageCards = computed<PageOverviewCard[]>(() => {
    switch (activePage.value) {
      case 'system':
        return [
          {
            label: '认证状态',
            value: authInitialized.value ? '已初始化' : '待初始化',
            description: authInitialized.value ? '管理员凭据已生效，后续访问后台都需要登录验证。' : '保存当前账号和密码后，会直接作为后台管理员凭据启用。'
          },
          {
            label: '管理员账号',
            value: authForm.username || '未设置',
            description: '当前页面维护的管理员用户名，后续登录后台时会直接使用它。'
          },
          {
            label: '密码动作',
            value: authInitialized.value ? '更新凭据' : '初始化凭据',
            description: authInitialized.value ? '已初始化状态下可继续轮换密码，但修改时必须提供当前密码。' : '首次保存时会直接完成管理员初始化，不存在额外的 enable 开关。'
          }
        ];
      case 'notification':
        return [
          {
            label: '渠道总数',
            value: `${notifyChannels.value.length} 个`,
            description: '当前已创建的通知渠道数量，支持新增、编辑、启停和删除。'
          },
          {
            label: '已启用',
            value: `${notifyChannels.value.filter((channel) => channel.enabled).length} 个`,
            description: '这些渠道会参与后续通知发送，关闭后会保留配置但不再推送。'
          },
          {
            label: '类型覆盖',
            value: `${new Set(notifyChannels.value.map((channel) => channel.type)).size} 种`,
            description: '按共享元数据统一维护的通知类型分布，避免继续散落旧字段心智。'
          }
        ];
      case 'backup':
        return [
          {
            label: '备份状态',
            value: backupForm.enable ? '已启用' : '未启用',
            description: backupForm.enable ? '会按当前策略保留远程备份并允许立即备份与恢复。' : '当前不会启用自动备份任务，但仍可先配置远程存储参数。'
          },
          {
            label: '保留份数',
            value: `${backupForm.backup_count || 0} 份`,
            description: '超过该数量后会自动淘汰最旧备份，避免远端或本地备份无限增长。'
          },
          {
            label: '备份周期',
            value: backupForm.cron || '未设置',
            description: '自动备份任务当前使用的 Cron 表达式。'
          }
        ];
      case 'cfst':
        return [
          {
            label: '当前状态',
            value: cfstStatus.value.running ? '测速中' : '空闲',
            description: cfstStatus.value.message || '当前 CFST 任务状态会随着测速执行实时更新。'
          },
          {
            label: '最佳 IP',
            value: cfstBestIp.value || '--',
            description: '最近一次优选得到的最佳 IP；没有结果时会显示占位符。'
          },
          {
            label: '结果数量',
            value: `${visibleCfstResults.value.length || (cfstHasError.value ? cfstResults.value.length : 0)} 条`,
            description: '根据当前展示规则过滤后的结果数量，可直接与下方结果表联动查看。'
          }
        ];
      case 'ikuai-dns':
        return [
          {
            label: '同步状态',
            value: ikuaiDnsForm.enable ? '已启用' : '未启用',
            description: ikuaiDnsForm.enable ? '优选完成后会继续把域名解析同步到爱快路由器。' : '当前仅保留连接参数，不会自动触发爱快 DNS 同步。'
          },
          {
            label: '同步目标',
            value: ikuaiDnsForm.url || '未填写',
            description: '当前配置的爱快路由器地址，连接测试与同步都基于这里。'
          },
          {
            label: '账号',
            value: ikuaiDnsForm.username || 'admin',
            description: '用于访问爱快接口的登录账号。'
          }
        ];
      default:
        return [];
    }
  });

  const createPageFeedback = (
    title = '',
    message = '',
    status: PageFeedback['status'] = 'success'
  ): PageFeedback => ({ title, message, status });

  return {
    sectionMeta: PAGE_META,
    activePageMeta,
    activePageLoaded,
    activePageCards,
    cfstHasError,
    visibleCfstResults,
    createPageFeedback
  };
};
