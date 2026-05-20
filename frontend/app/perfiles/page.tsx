"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Loader2, Lock } from "lucide-react";
import { BrandLogo } from "@/components/BrandLogo";
import { PinModal } from "@/components/PinModal";
import { apiRequest, setSelectedProfile, desbloquearPerfil, getCuentaInfo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Profile } from "@/lib/types";

const planLimits = {
  basico: 1,
  estandar: 2,
  premium: 5,
};

export default function ProfilesPage() {
  const router = useRouter();
  const { account, isAuthenticated, isLoading, selectProfile } = useAuth();
  
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // HU11: PIN validation state
  const [hasPin, setHasPin] = useState(false);
  const [selectedProfileForPin, setSelectedProfileForPin] = useState<Profile | null>(null);

  useEffect(() => {
    if (isLoading) return;
    
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (account?.is_admin) {
      router.replace("/admin");
      return;
    }
  }, [isAuthenticated, isLoading, account, router]);

  useEffect(() => {
    async function fetchProfiles() {
      if (!account?.id) return;
      
      try {
        const data = await apiRequest<Profile[]>(`/cuentas/${account.id}/perfiles`);
        if (!data || data.length === 0) {
          router.replace("/perfiles/crear");
          return;
        }
        setProfiles(data);

        // HU11: Check if account has PIN configured
        const cuentaInfo = await getCuentaInfo(account.id).catch(() => null);
        if (cuentaInfo) {
          setHasPin(cuentaInfo.has_pin);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudieron cargar los perfiles");
      } finally {
        setLoading(false);
      }
    }

    if (account?.id) {
      fetchProfiles();
    }
  }, [account, router]);

  const handleProfileSelect = (profile: Profile) => {
    // HU11: If account has PIN and profile is not infantil, require PIN
    if (hasPin && !profile.es_infantil) {
      setSelectedProfileForPin(profile);
      return;
    }

    // No PIN required, proceed directly
    completeProfileSelection(profile);
  };

  const completeProfileSelection = (profile: Profile) => {
    const selectedProfileData = { id: profile.id, nombre: profile.nombre, avatar: profile.avatar };
    setSelectedProfile(selectedProfileData);
    selectProfile(selectedProfileData);
    router.push("/inicio");
  };

  // HU11: Handle PIN validation
  const handlePinSubmit = async (pin: string): Promise<{ success: boolean; error?: string; blockedUntil?: string }> => {
    if (!selectedProfileForPin) {
      return { success: false, error: "No hay perfil seleccionado" };
    }

    try {
      const result = await desbloquearPerfil(selectedProfileForPin.id, pin);
      if (result.success) {
        completeProfileSelection(selectedProfileForPin);
        return { success: true };
      }
      return {
        success: false,
        error: "PIN incorrecto",
        blockedUntil: result.bloqueado_hasta,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Error al validar PIN";
      // Check if it's a block error
      if (errorMessage.includes("bloqueado") || errorMessage.includes("locked")) {
        return {
          success: false,
          error: "Perfil bloqueado por demasiados intentos fallidos",
          blockedUntil: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
        };
      }
      return { success: false, error: errorMessage };
    }
  };

  const handleCreateProfile = () => {
    if (!account) return;
    
    const canCreate = profiles.length < planLimits[account.plan];
    if (!canCreate) {
      setError("Si quieres crear un nuevo perfil, mejora tu plan");
      return;
    }
    router.push("/perfiles/crear");
  };

  if (isLoading || (loading && !error)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  const canCreateProfile = account ? profiles.length < planLimits[account.plan] : false;

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-background px-4">
      <BrandLogo size="lg" className="mb-12" />
      
      <h2 className="text-3xl font-semibold text-foreground mb-10">
        Quien esta mirando?
      </h2>
      
      {error ? (
        <div className="rounded-lg border border-primary/60 bg-primary/10 px-4 py-3 text-sm text-primary">
          {error}
        </div>
      ) : (
        <div className="flex flex-wrap justify-center gap-6">
          {profiles.map((profile) => (
            <button
              key={profile.id}
              onClick={() => handleProfileSelect(profile)}
              className="group flex flex-col items-center gap-3 focus:outline-none"
            >
              <div className="relative w-28 h-28 md:w-36 md:h-36 rounded-lg overflow-hidden border-2 border-transparent group-hover:border-tito-white group-focus:border-tito-white transition-all duration-200">
                <div 
                  className="w-full h-full flex items-center justify-center text-4xl md:text-5xl font-bold text-white"
                  style={{
                    background: `linear-gradient(135deg, #009246 0%, #009246 33%, #ffffff 33%, #ffffff 66%, #ce2b37 66%, #ce2b37 100%)`,
                  }}
                >
                  {profile.nombre.charAt(0).toUpperCase()}
                </div>
                {/* HU11: Show lock icon for non-infantil profiles when PIN is set */}
                {hasPin && !profile.es_infantil && (
                  <div className="absolute bottom-1 right-1 w-6 h-6 rounded-full bg-background/90 flex items-center justify-center">
                    <Lock size={14} className="text-muted-foreground" />
                  </div>
                )}
              </div>
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-sm md:text-base">
                {profile.nombre}
                {profile.es_infantil && (
                  <span className="ml-1 text-xs text-primary">(Infantil)</span>
                )}
              </span>
            </button>
          ))}
          <button
            type="button"
            onClick={handleCreateProfile}
            className="group flex flex-col items-center gap-3 focus:outline-none"
          >
            <div className="flex w-28 h-28 md:w-36 md:h-36 items-center justify-center rounded-lg border-2 border-dashed border-border bg-card transition-all duration-200 group-hover:border-tito-white group-focus:border-tito-white">
              <Plus size={36} className="text-muted-foreground group-hover:text-foreground" />
            </div>
            <span className="text-muted-foreground group-hover:text-foreground transition-colors text-sm md:text-base">
              Crear perfil
            </span>
          </button>
        </div>
      )}

      {/* HU11: PIN Modal */}
      {selectedProfileForPin && (
        <PinModal
          profileName={selectedProfileForPin.nombre}
          onSubmit={handlePinSubmit}
          onCancel={() => setSelectedProfileForPin(null)}
        />
      )}
    </div>
  );
}
