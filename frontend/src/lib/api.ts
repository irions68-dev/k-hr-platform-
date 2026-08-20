export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const AUTH_HEADER = "X-App-Password";
const STORAGE_KEY = "khr-app-password";

export function getStoredPassword(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(STORAGE_KEY) ?? "";
}

export function setStoredPassword(password: string): void {
  window.localStorage.setItem(STORAGE_KEY, password);
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const password = getStoredPassword();
  const res = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(password ? { [AUTH_HEADER]: password } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new ApiError(res.status, detail || res.statusText);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path);
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return apiRequest<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export async function apiPostFile<T>(
  path: string,
  file: File,
  fields: Record<string, string> = {}
): Promise<T> {
  const password = getStoredPassword();
  const formData = new FormData();
  formData.append("file", file);
  for (const [key, value] of Object.entries(fields)) {
    formData.append(key, value);
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    cache: "no-store",
    // Content-Type을 직접 지정하면 안 됨 - FormData는 브라우저가 boundary를
    // 포함해서 자동으로 설정해야 서버가 파싱할 수 있음.
    headers: password ? { [AUTH_HEADER]: password } : {},
    body: formData,
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new ApiError(res.status, detail || res.statusText);
  }
  return (await res.json()) as T;
}
