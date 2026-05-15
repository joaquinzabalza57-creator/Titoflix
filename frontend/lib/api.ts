// API configuration and utility functions for TITOFLIX

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const DIRECT_API_BASE_URL = process.env.NEXT_PUBLIC_DIRECT_API_URL || "http://localhost:8000/api/v1";
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "";

export function getApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export function getDirectApiUrl(path: string): string {
  return `${DIRECT_API_BASE_URL}${path}`;
}

export function getBackendUrl(path: string): string {
  // Handle relative stream URLs
  if (path.startsWith("http")) {
    return path;
  }
  return `${BACKEND_BASE_URL}${path}`;
}

export function getAssetUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null;
  }
  if (path.startsWith("http") || path.startsWith("data:")) {
    return path;
  }
  if (path.startsWith("assets/")) {
    return getApiUrl(`/assets/${encodeURI(path.slice("assets/".length))}`);
  }
  return path;
}

export function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("titoflix_token");
  if (!token) return {};
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const url = getApiUrl(path);
  const hasBody = options.body !== undefined && options.body !== null;
  const headers: HeadersInit = {
    ...getAuthHeaders(),
    ...options.headers,
  };

  if (hasBody && !isFormData) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch {
    throw new Error("No se pudo conectar con el backend. Verifica que Docker este corriendo y que el backend este en http://localhost:8000.");
  }

  if (!response.ok) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      const error = await response.json().catch(() => null);
      const detail = Array.isArray(error?.detail)
        ? error.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(". ")
        : error?.detail;
      throw new Error(error?.message || detail || `Error ${response.status}`);
    }

    const text = await response.text().catch(() => "");
    throw new Error(text.trim() || `Error ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return undefined as T;
  }

  return response.json();
}

// Registration
export async function register(email: string, password: string, plan: "basico" | "estandar" | "premium"): Promise<void> {
  await apiRequest("/cuentas/", {
    method: "POST",
    body: JSON.stringify({ email, password, plan }),
  });
}

// Auth
export type StoredAccount = {
  id?: number;
  email: string;
  is_admin: boolean;
};

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("titoflix_token");
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("titoflix_token");
}

export function setToken(token: string): void {
  localStorage.setItem("titoflix_token", token);
}

export function removeToken(): void {
  localStorage.removeItem("titoflix_token");
}

export function getStoredAccount(): StoredAccount | null {
  if (typeof window === "undefined") return null;
  const account = localStorage.getItem("titoflix_account");
  return account ? JSON.parse(account) : null;
}

export function setStoredAccount(account: StoredAccount): void {
  localStorage.setItem("titoflix_account", JSON.stringify(account));
}

export function removeStoredAccount(): void {
  localStorage.removeItem("titoflix_account");
}

// Profile
export type StoredProfile = {
  id: number;
  nombre: string;
  avatar?: string | null;
};

export function getSelectedProfile(): StoredProfile | null {
  if (typeof window === "undefined") return null;
  const profile = localStorage.getItem("titoflix_profile");
  return profile ? JSON.parse(profile) : null;
}

export function setSelectedProfile(profile: StoredProfile): void {
  localStorage.setItem("titoflix_profile", JSON.stringify(profile));
}

export function removeSelectedProfile(): void {
  localStorage.removeItem("titoflix_profile");
}

export function logout(): void {
  removeToken();
  removeStoredAccount();
  removeSelectedProfile();
}
