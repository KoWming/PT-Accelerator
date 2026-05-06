import notifyMeta from '@/utils/notify-meta.json';

const rawNotifyMeta = notifyMeta as {
  aliases: Record<string, string>;
  commonFields: string[];
  types: Array<{
    type: string;
    label: string;
    fields: string[];
    icon: string;
    chipClass: string;
  }>;
  guideGroups: Array<{
    title: string;
    chipClass: string;
    description: string;
    types: string[];
  }>;
};


export const NOTIFY_TYPE_ALIASES: Record<string, string> = rawNotifyMeta.aliases;

export const NOTIFY_COMMON_FIELDS = rawNotifyMeta.commonFields;

export const NOTIFY_TYPE_META = rawNotifyMeta.types.reduce<Record<string, {
  label: string;
  fields: string[];
  icon: string;
  chipClass: string;
}>>((acc, item) => {
  acc[item.type] = {
    label: item.label,
    fields: item.fields,
    icon: item.icon,
    chipClass: item.chipClass
  };
  return acc;
}, {});

export type NotifyCanonicalType = keyof typeof NOTIFY_TYPE_META;

export const NOTIFY_TYPE_OPTIONS = rawNotifyMeta.types.map(({ type, label }) => ({
  value: type,
  label
}));

export const NOTIFY_GUIDE_GROUPS = rawNotifyMeta.guideGroups;


export const normalizeNotifyType = (type: string) => NOTIFY_TYPE_ALIASES[type] || type;

export const getNotifyConfigFields = (type: string) => {
  const normalizedType = normalizeNotifyType(type) as NotifyCanonicalType;
  const fields = NOTIFY_TYPE_META[normalizedType]?.fields || [];
  return [...NOTIFY_COMMON_FIELDS, ...fields];
};

export const shouldKeepNotifyConfigValue = (value: unknown) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim() !== '';
  return true;
};

export const pickNotifyConfig = (type: string, source: Record<string, any>) => {
  const fields = getNotifyConfigFields(type);
  return fields.reduce<Record<string, any>>((config, field) => {
    const value = source[field];
    if (shouldKeepNotifyConfigValue(value)) {
      config[field] = value;
    }
    return config;
  }, {});
};

export const getNotifyTypeLabel = (type: string) => {
  const normalizedType = normalizeNotifyType(type) as NotifyCanonicalType;
  return NOTIFY_TYPE_META[normalizedType]?.label || type;
};

export const getNotifyTypeIcon = (type: string) => {
  const normalizedType = normalizeNotifyType(type) as NotifyCanonicalType;
  return NOTIFY_TYPE_META[normalizedType]?.icon || 'bx bx-bell';
};

export const getNotifyTypeChipClass = (type: string) => {
  const normalizedType = normalizeNotifyType(type) as NotifyCanonicalType;
  return NOTIFY_TYPE_META[normalizedType]?.chipClass || 'settings-chip-neutral';
};

