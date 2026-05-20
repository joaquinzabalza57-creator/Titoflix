// API configuration and utility functions for TITOFLIX

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
const DIRECT_API_BASE_URL = process.env.NEXT_PUBLIC_DIRECT_API_URL || "/api/v1";
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "";

// Max upload size (bytes). Can be overridden at build time with NEXT_PUBLIC_MAX_UPLOAD_SIZE.
export const MAX_UPLOAD_SIZE = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE) || 10 * 1024 * 1024; // 10MB

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

  // Client-side check to avoid sending bodies larger than MAX_UPLOAD_SIZE.
  if (hasBody) {
    try {
      let bodySize = 0;
      if (isFormData && typeof FormData !== "undefined") {
        const fd = options.body as FormData;
        for (const entry of fd.entries()) {
          const value = entry[1] as any;
          if (typeof File !== "undefined" && value instanceof File) {
            bodySize += value.size || 0;
          } else if (typeof value === "string") {
            bodySize += new Blob([value]).size;
          }
        }
      } else if (typeof options.body === "string") {
        bodySize = new Blob([options.body]).size;
      } else if (typeof options.body === "object") {
        // Fallback for objects that weren't stringified by the caller.
        try {
          const text = JSON.stringify(options.body as any);
          bodySize = new Blob([text]).size;
        } catch {}
      }

      if (bodySize > MAX_UPLOAD_SIZE) {
        const actualMB = Math.round((bodySize / 1024 / 1024) * 10) / 10;
        const allowedMB = Math.round((MAX_UPLOAD_SIZE / 1024 / 1024) * 10) / 10;
        throw new Error(`El archivo es demasiado grande (${actualMB}MB). Tamaño máximo permitido: ${allowedMB}MB.`);
      }
    } catch (err) {
      if (err instanceof Error) throw err;
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch {
    throw new Error("No se pudo conectar con el backend. Verifica que Docker esté corriendo y que la app esté configurada para usar la IP del servidor.");
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
