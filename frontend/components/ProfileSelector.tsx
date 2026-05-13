"use client";

import { useState, useEffect } from "react";
import { BrandLogo } from "./BrandLogo";
import { apiRequest, setSelectedProfile } from "@/lib/api";
import type { Profile } from "@/lib/types";

interface ProfileSelectorProps {
  onProfileSelect: (profile: { id: number; nombre: string }) => void;
}

// Default guest profile
const guestProfile: Profile = {
  id: 0,
  nombre: "Invitado",
  user_id: 0,
};

export function ProfileSelector({ onProfileSelect }: ProfileSelectorProps) {
  const [profiles, setProfiles] = useState<Profile[]>([guestProfile]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProfiles() {
      try {
        const data = await apiRequest<Profile[]>("/perfiles");
        if (data && data.length > 0) {
          setProfiles(data);
        }
      } catch {
        // Use default guest profile if fetch fails
        setProfiles([guestProfile]);
      } finally {
        setLoading(false);
      }
    }

    fetchProfiles();
  }, []);

  const handleProfileSelect = (profile: Profile) => {
    const selectedProfile = { id: profile.id, nombre: profile.nombre };
    setSelectedProfile(selectedProfile);
    onProfileSelect(selectedProfile);
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-background px-4">
      <BrandLogo size="lg" className="mb-12" />
      
      <h2 className="text-3xl font-semibold text-foreground mb-10">
        Quien esta mirando?
      </h2>
      
      {loading ? (
        <div className="flex gap-6">
          {[1, 2].map((i) => (
            <div key={i} className="flex flex-col items-center gap-3">
              <div className="w-28 h-28 md:w-36 md:h-36 rounded-lg bg-muted animate-pulse" />
              <div className="w-20 h-4 bg-muted rounded animate-pulse" />
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-wrap justify-center gap-6">
          {profiles.map((profile) => (
            <button
              key={profile.id}
              onClick={() => handleProfileSelect(profile)}
              className="group flex flex-col items-center gap-3 focus:outline-none"
            >
              <div className="w-28 h-28 md:w-36 md:h-36 rounded-lg overflow-hidden border-2 border-transparent group-hover:border-tito-white group-focus:border-tito-white transition-all duration-200">
                {/* Avatar with Italian flag gradient */}
                <div 
                  className="w-full h-full flex items-center justify-center text-4xl md:text-5xl font-bold text-white"
                  style={{
                    background: `linear-gradient(135deg, #009246 0%, #009246 33%, #ffffff 33%, #ffffff 66%, #ce2b37 66%, #ce2b37 100%)`,
                  }}
                >
                  {profile.nombre.charAt(0).toUpperCase()}
                </div>
              </div>
              <span className="text-muted-foreground group-hover:text-foreground transition-colors text-sm md:text-base">
                {profile.nombre}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
