"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronLeft, ChevronRight, Play, Film, Tv } from "lucide-react";
import { useRef, useState, type MouseEvent } from "react";
import { apiRequest, getAssetUrl, getBackendUrl } from "@/lib/api";
import type { ContinuarViendoItem, PlaybackResponse } from "@/lib/types";

interface ContinuarViendoRowProps {
  items: ContinuarViendoItem[];
}

export function ContinuarViendoRow({ items }: ContinuarViendoRowProps) {
  const rowRef = useRef<HTMLDivElement>(null);

  if (items.length === 0) return null;

  const scroll = (direction: "left" | "right") => {
    if (!rowRef.current) return;
    const scrollAmount = rowRef.current.clientWidth * 0.8;
    rowRef.current.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  };

  return (
    <div className="mb-8">
      <h2 className="text-xl font-semibold text-foreground px-4 md:px-8 lg:px-16 mb-3">
        Continuar viendo
      </h2>

      <div className="relative group/row">
        {/* Left arrow */}
        <button
          type="button"
          onClick={() => scroll("left")}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-full bg-gradient-to-r from-background to-transparent flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
          aria-label="Desplazar izquierda"
        >
          <ChevronLeft size={28} className="text-foreground" />
        </button>

        {/* Scroll container */}
        <div
          ref={rowRef}
          className="flex gap-3 overflow-x-auto scrollbar-hide px-4 md:px-8 lg:px-16 pb-2"
          style={{ scrollbarWidth: "none" }}
        >
          {items.map((item) => (
            <ContinuarViendoCard key={`${item.contenido.id}-${item.episodio?.id ?? "movie"}`} item={item} />
          ))}
        </div>

        {/* Right arrow */}
        <button
          type="button"
          onClick={() => scroll("right")}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-full bg-gradient-to-l from-background to-transparent flex items-center justify-center opacity-0 group-hover/row:opacity-100 transition-opacity"
          aria-label="Desplazar derecha"
        >
          <ChevronRight size={28} className="text-foreground" />
        </button>
      </div>
    </div>
  );
}

function ContinuarViendoCard({ item }: { item: ContinuarViendoItem }) {
  const router = useRouter();
  const { contenido, episodio, temporada, segundos_vistos, duracion_total } = item;
  const [loading, setLoading] = useState(false);
  const portadaUrl = getAssetUrl(contenido.portada_url);
  const progress = duracion_total > 0 ? Math.min((segundos_vistos / duracion_total) * 100, 100) : 0;

  const href = `/contenido/${contenido.id}`;

  const subtitle =
    episodio && temporada
      ? `T${temporada.numero} E${episodio.numero}: ${episodio.titulo}`
      : contenido.tipo === "pelicula"
      ? "Pelicula"
      : null;

  const handlePlay = async (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    setLoading(true);
    try {
      const path = episodio
        ? `/episodios/${episodio.id}/playback`
        : `/contenidos/${contenido.id}/playback`;
      const data = await apiRequest<PlaybackResponse>(path);
      const streamUrl = getBackendUrl(data.stream_url);
      const title = episodio && temporada
        ? `${contenido.titulo} - T${temporada.numero} E${episodio.numero}: ${episodio.titulo}`
        : contenido.titulo;
      const params = new URLSearchParams({
        url: streamUrl,
        title,
        contenido_id: String(contenido.id),
        start: String(Math.max(0, segundos_vistos)),
      });
      if (episodio) {
        params.set("episodio_id", String(episodio.id));
      }
      router.push(`/reproducir?${params.toString()}`);
    } catch {
      router.push(href);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Link href={href} onClick={handlePlay} className="group/continue flex-shrink-0 w-48 md:w-56">
      {/* Thumbnail */}
      <div className="relative aspect-video rounded-lg overflow-hidden bg-secondary mb-2">
        {portadaUrl ? (
          <img
            src={portadaUrl}
            alt={contenido.titulo}
            className="w-full h-full object-cover transition-transform duration-300 group-hover/continue:scale-105"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {contenido.tipo === "pelicula" ? (
              <Film size={32} className="text-muted-foreground" />
            ) : (
              <Tv size={32} className="text-muted-foreground" />
            )}
          </div>
        )}

        {/* Play overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover/continue:opacity-100 transition-opacity">
          <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
            {loading ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <Play size={20} fill="white" className="text-white ml-0.5" />
            )}
          </div>
        </div>

        {/* Progress bar */}
        {progress > 0 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/20">
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      {/* Info */}
      <p className="text-sm font-medium text-foreground truncate">{contenido.titulo}</p>
      {subtitle && (
        <p className="text-xs text-muted-foreground truncate">{subtitle}</p>
      )}
    </Link>
  );
}
