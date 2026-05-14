// Types for the TITOFLIX streaming app

export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Profile {
  id: number;
  nombre: string;
  avatar?: string;
  user_id: number;
}

export interface Genero {
  id: number;
  nombre: string;
}

export interface VideoVariant {
  id: number;
  quality: "HD" | "1440p" | "4K";
  video_storage_key: string;
  video_mime?: string;
  video_size?: number;
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
}

export interface PlaybackResponse {
  stream_url: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

export interface MiListaItem {
  id: number;
  perfil_id: number;
  contenido_id: number;
  contenido?: Contenido;
}

export interface ContinuarViendoItem {
  id: number;
  perfil_id: number;
  contenido_id: number;
  contenido?: Contenido;
  progreso?: number;
}
