import type { AxiosError } from 'axios';

export interface ApiResponse<T = unknown> {
  success?: boolean;
  code?: number;
  message?: string;
  data?: T;
}

export type ApiError = AxiosError<ApiResponse>;
