// Tipos compartidos por componentes. Deben mantenerse alineados con los DTOs
// de backend/src/dtos para que el contrato frontend/backend sea explicito.

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin?: boolean;
}

export interface AuthAccount {
  id: number;
  email: string;
  plan: "basico" | "estandar" | "premium";
  is_admin: boolean;
}

export interface Profile {
  id: number;
  nombre: string;
  avatar?: string;
  cuenta_id: number;
  es_infantil?: boolean;
  has_pin?: boolean;
}

export interface Genero {
  id: number;
  nombre: string;
}

export interface VideoVariant {
  // Variante generada por FFmpeg y seleccionable en los reproductores.
  id: number;
  quality: "FHD" | "QHD" | "4K";
  video_storage_key: string;
  video_mime?: string;
  video_size?: number;
}

export interface ProcessingWarning {
  message: string;
  source_quality: string;
}

export interface Contenido {
  id: number;
  titulo: string;
  descripcion?: string;
  tipo: "pelicula" | "serie";
  anio?: number;
  duracion_min?: number;
  clasificacion?: string;
  clasificacion_edad?: string;
  portada_url?: string;
  processing_warning?: ProcessingWarning;
  generos?: Genero[];
  promedio_calificacion?: number;
  promedio_calificaciones?: number;
  storage_folder_id?: string;
  video_storage_key?: string;
  video_mime?: string;
  video_size?: number;
  video_variants?: VideoVariant[];
}

export interface Temporada {
  id: number;
  numero: number;
  nombre?: string;
  contenido_id: number;
  anio?: number;
}

export interface Episodio {
  id: number;
  numero: number;
  titulo: string;
  descripcion?: string;
  temporada_id: number;
  duracion?: number;
  duracion_min?: number;
  storage_folder_id?: string;
  video_storage_key?: string;
  video_mime?: string;
  video_size?: number;
  video_variants?: VideoVariant[];
  thumbnail_url?: string;
  processing_warning?: ProcessingWarning;
}

export interface PlaybackResponse {
  // /playback devuelve una URL temporal que luego se usa como src del <video>.
  stream_url: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  id?: number;
  is_admin?: boolean;
  email?: string;
  plan?: "basico" | "estandar" | "premium";
  user?: User;
}

export interface MiListaItem {
  id: number;
  perfil_id: number;
  contenido_id: number;
  contenido?: Contenido;
}

export interface Vista {
  id: number;
  perfil_id: number;
  contenido_id?: number | null;
  episodio_id?: number | null;
  segundos_vistos: number;
  terminado: boolean;
  actualizado_en?: string;
}

export interface ContinuarViendoItem {
  // Respuesta enriquecida para la fila "Continuar viendo".
  contenido: Contenido;
  episodio?: Episodio | null;
  temporada?: Temporada | null;
  segundos_vistos: number;
  duracion_total: number;
  terminado: boolean;
  actualizado_en?: string;
}
