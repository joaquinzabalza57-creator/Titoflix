// Cliente HTTP compartido por todo el frontend. Centraliza URLs, auth headers,
// errores del backend y adaptacion de assets privados servidos desde /api/v1.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
const DIRECT_API_BASE_URL = process.env.NEXT_PUBLIC_DIRECT_API_URL || "/api/v1";
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "";

// Max upload size para assets chicos. Videos se validan/procesan en backend.
export const MAX_UPLOAD_SIZE = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_SIZE) || 10 * 1024 * 1024;

export function getApiUrl(path: string): string {
  // Ruta normal: usa proxy/rewrite de Next o una URL publica configurada.
  return `${API_BASE_URL}${path}`;
}

export function getDirectApiUrl(path: string): string {
  // Ruta directa al backend, util cuando se evita el proxy del frontend.
  return `${DIRECT_API_BASE_URL}${path}`;
}

export function getBackendUrl(path: string): string {
  // Los endpoints /playback devuelven URLs relativas de stream; aca se vuelven
  // absolutas cuando el navegador necesita hablar directo con FastAPI.
  if (path.startsWith("http")) {
    return path;
  }
  return `${BACKEND_BASE_URL}${path}`;
}

export function getAssetUrl(path: string | null | undefined): string | null {
  // MinIO nunca se expone directo al navegador: assets/* se sirven por backend.
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
  // El token vive en localStorage porque esta app es client-side.
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
  // Wrapper unico para fetch: agrega Authorization, JSON headers y parsing de
  // errores con el formato que devuelve app_error_handler.
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

  // Check cliente para evitar subir assets chicos demasiado grandes. Videos se
  // validan en backend/proceso porque pueden superar este limite.
  if (hasBody) {
    try {
      let bodySize = 0;
      if (isFormData && typeof FormData !== "undefined") {
        const fd = options.body as FormData;
        for (const entry of fd.entries()) {
          const value = entry[1];
          if (typeof File !== "undefined" && value instanceof File) {
            bodySize += value.size || 0;
          } else if (typeof value === "string") {
            bodySize += new Blob([value]).size;
          }
        }
      } else if (typeof options.body === "string") {
        bodySize = new Blob([options.body]).size;
      } else if (typeof options.body === "object") {
        try {
          const text = JSON.stringify(options.body);
          bodySize = new Blob([text]).size;
        } catch {}
      }

      if (bodySize > MAX_UPLOAD_SIZE) {
        const actualMB = Math.round((bodySize / 1024 / 1024) * 10) / 10;
        const allowedMB = Math.round((MAX_UPLOAD_SIZE / 1024 / 1024) * 10) / 10;
        throw new Error(`El archivo es demasiado grande (${actualMB}MB). Tamano maximo permitido: ${allowedMB}MB.`);
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
    throw new Error("No se pudo conectar con el backend. Verifica que Docker este corriendo y que la app este configurada para usar la IP del servidor.");
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

// Registro de cuentas publicas.
export async function register(email: string, password: string, plan: "basico" | "estandar" | "premium"): Promise<void> {
  await apiRequest("/cuentas/", {
    method: "POST",
    body: JSON.stringify({ email, password, plan }),
  });
}

// Estado de cuenta autenticada guardado en el navegador.
export type StoredAccount = {
  id?: number;
  email: string;
  plan?: "basico" | "estandar" | "premium";
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

// Perfil actualmente elegido por la cuenta.
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
  // Limpia cuenta, token y perfil para volver al flujo de login.
  removeToken();
  removeStoredAccount();
  removeSelectedProfile();
}

// HU5: busqueda de contenido con filtros.
export interface ContentSearchParams {
  q?: string;
  genero?: string;
  tipo?: "pelicula" | "serie";
  ordenar?: "anio_desc" | "anio_asc" | "titulo_asc";
  perfil_id?: number;
}

export function buildContentSearchUrl(params: ContentSearchParams): string {
  // Mantiene sincronizado el contrato de query params con product_router.search.
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.genero) query.set("genero", params.genero);
  if (params.tipo) query.set("tipo", params.tipo);
  if (params.ordenar) query.set("ordenar", params.ordenar);
  if (params.perfil_id) query.set("perfil_id", String(params.perfil_id));
  const qs = query.toString();
  return qs ? `/contenidos?${qs}` : "/contenidos";
}

// HU6: progreso de reproduccion.
export interface ReportVistaPayload {
  contenido_id?: number;
  episodio_id?: number;
  segundos_vistos: number;
  terminado?: boolean;
}

export async function reportarVista(perfilId: number, payload: ReportVistaPayload): Promise<void> {
  // El reproductor llama esto periodicamente para alimentar Continuar viendo.
  await apiRequest(`/perfiles/${perfilId}/vistas`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface Calificacion {
  id: number;
  perfil_id: number;
  contenido_id: number;
  puntaje: number;
}

export async function setCalificacion(perfilId: number, contenidoId: number, puntaje: number): Promise<Calificacion> {
  return apiRequest<Calificacion>(`/perfiles/${perfilId}/calificaciones/${contenidoId}`, {
    method: "POST",
    body: JSON.stringify({ puntaje }),
  });
}

export async function getCalificacion(perfilId: number, contenidoId: number): Promise<Calificacion | null> {
  try {
    return await apiRequest<Calificacion>(`/perfiles/${perfilId}/calificaciones/${contenidoId}`);
  } catch {
    return null;
  }
}

export async function deleteCalificacion(perfilId: number, contenidoId: number): Promise<void> {
  await apiRequest(`/perfiles/${perfilId}/calificaciones/${contenidoId}`, {
    method: "DELETE",
  });
}

export async function getRecomendaciones(perfilId: number): Promise<import("@/lib/types").Contenido[]> {
  return apiRequest<import("@/lib/types").Contenido[]>(`/perfiles/${perfilId}/recomendaciones`);
}

export async function downloadFromApi(path: string, fallbackFilename: string): Promise<void> {
  const response = await fetch(getApiUrl(path), {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Error ${response.status}`);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") || "";
  const match = disposition.match(/filename="?([^"]+)"?/i);
  const filename = match?.[1] || fallbackFilename;
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
