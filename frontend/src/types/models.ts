export interface User {
  username: string;
}

export interface Host {
  id?: string | number;
  domain: string;
  ip?: string;
}

export interface Tracker {
  id?: string | number;
  url: string;
}
