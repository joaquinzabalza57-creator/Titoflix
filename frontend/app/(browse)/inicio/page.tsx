"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Hero } from "@/components/Hero";
import { ContentRow } from "@/components/ContentRow";
import { apiRequest, getSelectedProfile } from "@/lib/api";
import type { Contenido, MiListaItem, ContinuarViendoItem } from "@/lib/types";

const mockContenidos: Contenido[] = [
  {
    id: 1,
    titulo: "Pelicula de Ejemplo",
    descripcion: "Una emocionante pelicula llena de aventuras y momentos inolvidables.",
    tipo: "pelicula",
    anio: 2024,
    clasificacion: "PG-13",
    generos: [{ id: 1, nombre: "Accion" }, { id: 2, nombre: "Aventura" }],
  },
  {
    id: 2,
    titulo: "Serie Dramatica",
    descripcion: "Una serie que te mantendra al borde de tu asiento con cada episodio.",
    tipo: "serie",
    anio: 2023,
    clasificacion: "TV-MA",
    generos: [{ id: 3, nombre: "Drama" }, { id: 4, nombre: "Suspenso" }],
  },
];

export default function InicioPage() {
  const [allContent, setAllContent] = useState<Contenido[]>([]);
  const [topContent, setTopContent] = useState<Contenido[]>([]);
  const [miLista, setMiLista] = useState<Contenido[]>([]);
  const [continuarViendo, setContinuarViendo] = useState<Contenido[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchContent = useCallback(async () => {
    setLoading(true);
    try {
      const contenidos = await apiRequest<Contenido[]>("/contenidos").catch(() => []);
      setAllContent(contenidos.length > 0 ? contenidos : mockContenidos);

      const top = await apiRequest<Contenido[]>("/contenidos/top").catch(() => []);
      setTopContent(top);

      const profile = getSelectedProfile();
      if (profile && profile.id > 0) {
        const lista = await apiRequest<MiListaItem[]>(`/perfiles/${profile.id}/mi-lista`).catch(() => []);
        const listaContenidos = lista
          .filter((item) => item.contenido)
          .map((item) => item.contenido as Contenido);
        setMiLista(listaContenidos);

        const continuar = await apiRequest<ContinuarViendoItem[]>(`/perfiles/${profile.id}/continuar`).catch(() => []);
        const continuarContenidos = continuar
          .filter((item) => item.contenido)
          .map((item) => item.contenido as Contenido);
        setContinuarViendo(continuarContenidos);
      }
    } catch (error) {
      console.error("Error fetching content:", error);
      setAllContent(mockContenidos);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchContent();
  }, [fetchContent]);

  const peliculas = allContent.filter((c) => c.tipo === "pelicula");
  const series = allContent.filter((c) => c.tipo === "serie");

  return (
    <>
      <Hero />

      <div className="-mt-20 relative z-10">
        <ContentRow
          title="Contenido principal"
          contents={topContent.length > 0 ? topContent : allContent}
          loading={loading}
          linkPrefix="/contenido"
          emptyMessage="No hay peliculas o series disponibles en este momento. Intentar mas tarde."
        />

        <ContentRow
          title="Peliculas"
          contents={peliculas}
          loading={loading}
          linkPrefix="/contenido"
          emptyMessage="No hay peliculas disponibles en este momento. Intentar mas tarde."
        />

        <ContentRow
          title="Series"
          contents={series}
          loading={loading}
          linkPrefix="/contenido"
          emptyMessage="No hay series disponibles en este momento. Intentar mas tarde."
        />

        {miLista.length > 0 && (
          <ContentRow
            title="Mi lista"
            contents={miLista}
            loading={false}
            linkPrefix="/contenido"
          />
        )}

        {continuarViendo.length > 0 && (
          <ContentRow
            title="Continuar viendo"
            contents={continuarViendo}
            loading={false}
            linkPrefix="/contenido"
          />
        )}
      </div>
    </>
  );
}
