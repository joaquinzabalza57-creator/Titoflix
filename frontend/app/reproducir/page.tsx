"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function ReproducirPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading, profile, account } = useAuth();
  
  const streamUrl = searchParams.get("url");
  const title = searchParams.get("title") || "Reproduciendo";

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

    if (!profile) {
      router.replace("/perfiles");
      return;
    }
  }, [isAuthenticated, isLoading, account, profile, router]);

  const handleBack = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 bg-black flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary" />
      </div>
    );
  }

  if (!streamUrl) {
    return (
      <div className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center gap-4">
        <p className="text-white">No se especifico un video para reproducir.</p>
        <button
          onClick={handleBack}
          className="text-primary hover:underline"
        >
          Volver
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-black to-transparent">
        <div className="flex items-center gap-4">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white hover:text-primary transition-colors"
          >
            <ArrowLeft size={24} />
            <span className="font-medium">Volver</span>
          </button>
          <span className="text-white font-medium truncate">{title}</span>
        </div>
      </div>

      {/* Video */}
      <video
        className="w-full h-full object-contain"
        src={streamUrl}
        controls
        autoPlay
        playsInline
      >
        Tu navegador no soporta la reproduccion de video.
      </video>
    </div>
  );
}
