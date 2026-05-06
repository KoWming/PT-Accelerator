const padNumber = (value: number) => String(value).padStart(2, '0');

const toValidDate = (value: string | null | undefined) => {
  if (!value) return null;

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;

  return date;
};

export const formatDateTime = (value: string | null | undefined, fallback = '--') => {
  const date = toValidDate(value);
  if (!date) return value || fallback;

  return date.toLocaleString('zh-CN', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

export const formatDateTimeCompact = (value: string | null | undefined, fallback = '--') => {
  const date = toValidDate(value);
  if (!date) return value || fallback;

  return `${date.getFullYear()}-${padNumber(date.getMonth() + 1)}-${padNumber(date.getDate())} ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}`;
};

export const formatTimeOnly = (value: string | null | undefined, fallback = '--') => {
  const date = toValidDate(value);
  if (!date) return value || fallback;

  return `${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:${padNumber(date.getSeconds())}`;
};

export const formatMetric = (value: number | string | null | undefined, digits = 2, suffix = '') => {
  if (value === null || value === undefined || value === '') return '--';

  const num = Number(value);
  if (Number.isNaN(num)) return String(value);

  return `${num.toFixed(digits)}${suffix}`;
};

export const formatFileSize = (bytes: string | number) => {
  const normalized = parseInt(String(bytes), 10);
  if (Number.isNaN(normalized)) return String(bytes);
  if (normalized < 1024) return `${normalized} B`;
  if (normalized < 1024 * 1024) return `${(normalized / 1024).toFixed(1)} KB`;
  return `${(normalized / (1024 * 1024)).toFixed(1)} MB`;
};

export const formatBackupTime = (value: string) => {
  const date = toValidDate(value);
  if (!date) return value || '--';

  return `${date.getFullYear()}年${padNumber(date.getMonth() + 1)}月${padNumber(date.getDate())}日 ${padNumber(date.getHours())}:${padNumber(date.getMinutes())}:${padNumber(date.getSeconds())}`;
};

