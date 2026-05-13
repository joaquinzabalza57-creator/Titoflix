// API configuration and utility functions for TITOFLIX

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export function getApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export function getBackendUrl(path: string): string {
  // Handle relative stream URLs
  if (path.startsWith("http")) {
    return path;
  }
  return `${BACKEND_BASE_URL}${path}`;
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
  const url = getApiUrl(path);
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...getAuthHeaders(),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail || `Error ${response.status}`);
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

// Profile
export function getSelectedProfile(): { id: number; nombre: string } | null {
  if (typeof window === "undefined") return null;
  const profile = localStorage.getItem("titoflix_profile");
  return profile ? JSON.parse(profile) : null;
}

export function setSelectedProfile(profile: { id: number; nombre: string }): void {
  localStorage.setItem("titoflix_profile", JSON.stringify(profile));
}

export function removeSelectedProfile(): void {
  localStorage.removeItem("titoflix_profile");
}

export function logout(): void {
  removeToken();
  removeSelectedProfile();
}
