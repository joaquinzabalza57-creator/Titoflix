"use client";

import { useState, useEffect, useCallback } from "react";
import { LoginScreen } from "@/components/LoginScreen";
import { ProfileSelector } from "@/components/ProfileSelector";
import { ProfileCreateScreen } from "@/components/ProfileCreateScreen";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { ContentRow } from "@/components/ContentRow";
import { ContentDetail } from "@/components/ContentDetail";
import { VideoPlayer } from "@/components/VideoPlayer";
import { AdminDashboard } from "@/components/AdminDashboard";
import { apiRequest, getSelectedProfile, getStoredAccount, isAuthenticated, logout, setStoredAccount } from "@/lib/api";
import type { AuthAccount, Contenido, MiListaItem, ContinuarViendoItem, Profile } from "@/lib/types";

type AppView = "login" | "profile-select" | "profile-create" | "home" | "player" | "admin";
type Section = "inicio" | "peliculas" | "series" | "mi-lista";

// Mock data as fallback
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

export default function Home() {
  const [view, setView] = useState<AppView>("login");
  const [activeSection, setActiveSection] = useState<Section>("inicio");
  const [selectedContent, setSelectedContent] = useState<Contenido | null>(null);
  const [playerData, setPlayerData] = useState<{ url: string; title: string } | null>(null);
  const [account, setAccount] = useState<AuthAccount | null>(null);

  // Content state
  const [allContent, setAllContent] = useState<Contenido[]>([]);
  const [topContent, setTopContent] = useState<Contenido[]>([]);
  const [miLista, setMiLista] = useState<Contenido[]>([]);
  const [continuarViendo, setContinuarViendo] = useState<Contenido[]>([]);
  const [loading, setLoading] = useState(true);

  // Check auth status on mount
  useEffect(() => {
    if (!isAuthenticated()) {
      setView("login");
      return;
    }

    const account = getStoredAccount();
    if (account?.is_admin) {
      setView("admin");
      return;
    }

    apiRequest<AuthAccount>("/auth/me")
      .then((currentAccount) => {
        setAccount(currentAccount);
        setStoredAccount({
          id: currentAccount.id,
          email: currentAccount.email,
          is_admin: currentAccount.is_admin,
        });
        if (currentAccount.is_admin) {
          setView("admin");
          return;
        }
        routeAfterAccountLoad(currentAccount);
      })
      .catch(() => {
        logout();
        setView("login");
      });
  }, []);

  const routeAfterAccountLoad = async (currentAccount: AuthAccount) => {
    try {
      const profiles = await apiRequest<Profile[]>(`/cuentas/${currentAccount.id}/perfiles`);
      if (!profiles || profiles.length === 0) {
        setView("profile-create");
        return;
      }

      const selectedProfile = getSelectedProfile();
      const selectedStillExists = selectedProfile && profiles.some((profile) => profile.id === selectedProfile.id);
      setView(selectedStillExists ? "home" : "profile-select");
    } catch {
      setView("profile-select");
    }
  };

  // Fetch content
  const fetchContent = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch all content
      const contenidos = await apiRequest<Contenido[]>("/contenidos").catch(() => []);
      setAllContent(contenidos.length > 0 ? contenidos : mockContenidos);

      // Fetch top content
      const top = await apiRequest<Contenido[]>("/contenidos/top").catch(() => []);
      setTopContent(top);

      // Fetch Mi Lista
      const profile = getSelectedProfile();
      if (profile && profile.id > 0) {
        const lista = await apiRequest<MiListaItem[]>(`/perfiles/${profile.id}/mi-lista`).catch(() => []);
        const listaContenidos = lista
          .filter((item) => item.contenido)
          .map((item) => item.contenido as Contenido);
        setMiLista(listaContenidos);

        // Fetch Continuar Viendo
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

  // Fetch content when entering home
  useEffect(() => {
    if (view === "home") {
      fetchContent();
    }
  }, [view, fetchContent]);

  // Filter content by type
  const peliculas = allContent.filter((c) => c.tipo === "pelicula");
  const series = allContent.filter((c) => c.tipo === "serie");

  // Handlers
  const handleLoginSuccess = (options?: { admin?: boolean }) => {
    if (options?.admin) {
      setView("admin");
      return;
    }

    apiRequest<AuthAccount>("/auth/me")
      .then((currentAccount) => {
        setAccount(currentAccount);
        setStoredAccount({
          id: currentAccount.id,
          email: currentAccount.email,
          is_admin: currentAccount.is_admin,
        });
        return routeAfterAccountLoad(currentAccount);
      })
      .catch(() => setView("profile-select"));
  };

  const handleProfileSelect = () => {
    setView("home");
  };

  const handleNoProfiles = () => {
    setView("profile-create");
  };

  const handleCreateProfile = () => {
    setView("profile-create");
  };

  const handleProfileChanged = () => {
    setSelectedContent(null);
    setPlayerData(null);
    fetchContent();
  };

  const handleLogout = () => {
    setView("login");
    setActiveSection("inicio");
    setSelectedContent(null);
    setPlayerData(null);
    setAccount(null);
  };

  const handleNavigate = (section: string) => {
    setActiveSection(section as Section);
  };

  const handleContentClick = (content: Contenido) => {
    setSelectedContent(content);
  };

  const handleCloseDetail = () => {
    setSelectedContent(null);
  };

  const handlePlay = (streamUrl: string, title: string) => {
    setSelectedContent(null);
    setPlayerData({ url: streamUrl, title });
    setView("player");
  };

  const handleBackFromPlayer = () => {
    setPlayerData(null);
    setView("home");
  };

  // Render based on view
  if (view === "login") {
    return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
  }

  if (view === "profile-select") {
    if (!account) {
      return null;
    }
    return (
      <ProfileSelector
        accountId={account.id}
        accountPlan={account.plan}
        onProfileSelect={handleProfileSelect}
        onNoProfiles={handleNoProfiles}
        onCreateProfile={handleCreateProfile}
      />
    );
  }

  if (view === "profile-create") {
    if (!account) {
      return null;
    }
    return (
      <ProfileCreateScreen
        accountId={account.id}
        onProfileCreated={handleProfileSelect}
      />
    );
  }

  if (view === "player" && playerData) {
    return (
      <VideoPlayer
        streamUrl={playerData.url}
        title={playerData.title}
        onBack={handleBackFromPlayer}
      />
    );
  }

  if (view === "admin") {
    return <AdminDashboard onLogout={handleLogout} />;
  }

  if (!account) {
    return null;
  }

  // Home view
  return (
    <div className="min-h-screen bg-background">
      <Header
        activeSection={activeSection}
        account={account}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
        onProfileChanged={handleProfileChanged}
      />

      <main>
        {activeSection === "inicio" && (
          <>
            <Hero
              onExplore={() => handleNavigate("peliculas")}
              onMiLista={() => handleNavigate("mi-lista")}
            />

            <div className="-mt-20 relative z-10">
              {/* Contenido Principal (Top content or all content) */}
              <ContentRow
                title="Contenido principal"
                contents={topContent.length > 0 ? topContent : allContent}
                loading={loading}
                onContentClick={handleContentClick}
                emptyMessage="No hay peliculas o series disponibles en este momento. Intentar mas tarde."
              />

              {/* Peliculas */}
              <ContentRow
                title="Peliculas"
                contents={peliculas}
                loading={loading}
                onContentClick={handleContentClick}
                emptyMessage="No hay peliculas disponibles en este momento. Intentar mas tarde."
              />

              {/* Series */}
              <ContentRow
                title="Series"
                contents={series}
                loading={loading}
                onContentClick={handleContentClick}
                emptyMessage="No hay series disponibles en este momento. Intentar mas tarde."
              />

              {/* Mi Lista */}
              {miLista.length > 0 && (
                <ContentRow
                  title="Mi lista"
                  contents={miLista}
                  loading={false}
                  onContentClick={handleContentClick}
                />
              )}

              {/* Continuar viendo */}
              {continuarViendo.length > 0 && (
                <ContentRow
                  title="Continuar viendo"
                  contents={continuarViendo}
                  loading={false}
                  onContentClick={handleContentClick}
                />
              )}
            </div>
          </>
        )}

        {activeSection === "peliculas" && (
          <div className="pt-24 pb-12">
            <h1 className="text-3xl font-bold text-foreground px-4 md:px-8 lg:px-16 mb-6">
              Peliculas
            </h1>
            <ContentRow
              title=""
              contents={peliculas}
              loading={loading}
              onContentClick={handleContentClick}
              emptyMessage="No hay peliculas disponibles en este momento. Intentar mas tarde."
            />
          </div>
        )}

        {activeSection === "series" && (
          <div className="pt-24 pb-12">
            <h1 className="text-3xl font-bold text-foreground px-4 md:px-8 lg:px-16 mb-6">
              Series
            </h1>
            <ContentRow
              title=""
              contents={series}
              loading={loading}
              onContentClick={handleContentClick}
              emptyMessage="No hay series disponibles en este momento. Intentar mas tarde."
            />
          </div>
        )}

        {activeSection === "mi-lista" && (
          <div className="pt-24 pb-12">
            <h1 className="text-3xl font-bold text-foreground px-4 md:px-8 lg:px-16 mb-6">
              Mi lista
            </h1>
            <ContentRow
              title=""
              contents={miLista}
              loading={loading}
              onContentClick={handleContentClick}
              emptyMessage="Tu lista esta vacia. Agrega peliculas y series para verlas mas tarde."
            />
          </div>
        )}
      </main>

      {/* Content Detail Modal */}
      {selectedContent && (
        <ContentDetail
          content={selectedContent}
          onClose={handleCloseDetail}
          onPlay={handlePlay}
        />
      )}
    </div>
  );
}
