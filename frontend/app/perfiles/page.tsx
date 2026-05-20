"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Loader2, Lock } from "lucide-react";
import { BrandLogo } from "@/components/BrandLogo";
import { PinModal } from "@/components/PinModal";
import { ProfileAvatar } from "@/components/ProfileAvatar";
import { apiRequest, setSelectedProfile } from "@/lib/api";
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
  const [pinProfile, setPinProfile] = useState<Profile | null>(null);
  const [pinError, setPinError] = useState<string | null>(null);
  const [pinLoading, setPinLoading] = useState(false);

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

  const completeProfileSelection = (profile: Profile) => {
    const selectedProfileData = { id: profile.id, nombre: profile.nombre, avatar: profile.avatar };
    setSelectedProfile(selectedProfileData);
    selectProfile(selectedProfileData);
    router.push("/inicio");
  };

  const handleProfileSelect = (profile: Profile) => {
    if (profile.has_pin) {
      setPinProfile(profile);
      setPinError(null);
      return;
    }
    completeProfileSelection(profile);
  };

  const handlePinSubmit = async (pin: string) => {
    if (!pinProfile) return;
    setPinLoading(true);
    setPinError(null);
    try {
      await apiRequest(`/auth/perfiles/${pinProfile.id}`, {
        method: "POST",
        body: JSON.stringify({ pin }),
      });
      completeProfileSelection(pinProfile);
    } catch (err) {
      setPinError(err instanceof Error ? err.message : "PIN invalido");
    } finally {
      setPinLoading(false);
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
                <ProfileAvatar profile={profile} size="lg" className="h-full w-full" />
                {profile.has_pin && (
                  <div className="absolute bottom-2 right-2 flex h-7 w-7 items-center justify-center rounded-full bg-background/90 text-muted-foreground">
                    <Lock size={15} />
                  </div>
                )}
              </div>
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-sm md:text-base">
                {profile.nombre}
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
      {pinProfile && (
        <PinModal
          profileName={pinProfile.nombre}
          loading={pinLoading}
          error={pinError}
          onSubmit={handlePinSubmit}
          onCancel={() => setPinProfile(null)}
        />
      )}
    </div>
  );
}
