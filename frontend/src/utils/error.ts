import axios from 'axios';

export type AppErrorCode = 'network' | 'auth' | 'validation' | 'server' | 'unknown';

export interface AppErrorInfo {
  code: AppErrorCode;
  message: string;
  status?: number;
}

export class AppError extends Error {
  readonly code: AppErrorCode;
  readonly status?: number;

  constructor(info: AppErrorInfo) {
    super(info.message);
    this.name = 'AppError';
    this.code = info.code;
    this.status = info.status;
  }
}

const stringifyUnknownRecord = (value: Record<string, unknown>) => {
  if (typeof value.msg === 'string' && value.msg.trim()) return value.msg;
  if (typeof value.message === 'string' && value.message.trim()) return value.message;
  return JSON.stringify(value);
};

const extractErrorDetail = (detail: unknown): string | null => {
  if (typeof detail === 'string' && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const normalized = detail
      .map((item) => {
        if (typeof item === 'string' && item.trim()) return item;
        if (item && typeof item === 'object') return stringifyUnknownRecord(item as Record<string, unknown>);
        return String(item ?? '').trim();
      })
      .filter(Boolean);

    return normalized.length ? normalized.join('；') : null;
  }

  if (detail && typeof detail === 'object') {
    return stringifyUnknownRecord(detail as Record<string, unknown>);
  }

  return null;
};

export const getErrorMessage = (error: unknown, fallback = '操作失败，请稍后重试') => {
  if (error instanceof AppError) return error.message;

  if (axios.isAxiosError(error)) {
    const detailMessage = extractErrorDetail(error.response?.data?.detail);
    if (detailMessage) return detailMessage;

    const responseMessage = typeof error.response?.data?.message === 'string' ? error.response.data.message.trim() : '';
    if (responseMessage) return responseMessage;

    if (error.message) return error.message;
  }

  if (error instanceof Error && error.message) return error.message;
  if (typeof error === 'string' && error.trim()) return error;
  return fallback;
};

export const normalizeError = (error: unknown, fallback?: string): AppErrorInfo => {
  if (error instanceof AppError) {
    return {
      code: error.code,
      message: error.message,
      status: error.status,
    };
  }

  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const message = getErrorMessage(error, fallback || '请求失败，请稍后重试');

    if (!error.response) return { code: 'network', message, status };
    if (status === 401 || status === 403) return { code: 'auth', message, status };
    if (status === 422) return { code: 'validation', message, status };
    if (status && status >= 500) return { code: 'server', message, status };

    return { code: 'unknown', message, status };
  }

  return {
    code: 'unknown',
    message: getErrorMessage(error, fallback),
  };
};

