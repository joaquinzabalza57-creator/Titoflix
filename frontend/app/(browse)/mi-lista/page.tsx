"use client";

import { useState, useEffect } from "react";
import { ContentRow } from "@/components/ContentRow";
import { apiRequest, getSelectedProfile } from "@/lib/api";
import type { Contenido, MiListaItem } from "@/lib/types";

export default function MiListaPage() {
  const [miLista, setMiLista] = useState<Contenido[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMiLista() {
      try {
        const profile = getSelectedProfile();
        if (profile && profile.id > 0) {
          const lista = await apiRequest<MiListaItem[]>(`/perfiles/${profile.id}/mi-lista`);
          const contenidos = lista
            .filter((item) => item.contenido)
            .map((item) => item.contenido as Contenido);
          setMiLista(contenidos);
        }
      } catch (error) {
        console.error("Error fetching mi lista:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchMiLista();
  }, []);

  return (
    <div className="pt-24 pb-12">
      <h1 className="text-3xl font-bold text-foreground px-4 md:px-8 lg:px-16 mb-6">
        Mi lista
      </h1>
      <ContentRow
        title=""
        contents={miLista}
        loading={loading}
        linkPrefix="/contenido"
        emptyMessage="Tu lista esta vacia. Agrega peliculas y series para verlas mas tarde."
      />
    </div>
  );
}
