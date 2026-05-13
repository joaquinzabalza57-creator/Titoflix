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

export interface Contenido {
  id: number;
  titulo: string;
  descripcion?: string;
  tipo: "pelicula" | "serie";
  anio?: number;
  clasificacion?: string;
  portada_url?: string;
  generos?: Genero[];
  promedio_calificacion?: number;
}

export interface Temporada {
  id: number;
  numero: number;
  nombre?: string;
  contenido_id: number;
}

export interface Episodio {
  id: number;
  numero: number;
  titulo: string;
  descripcion?: string;
  temporada_id: number;
  duracion?: number;
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
