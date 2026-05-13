"use client";

import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { BrandLogo } from "./BrandLogo";
import { apiRequest, setToken } from "@/lib/api";
import type { AuthResponse } from "@/lib/types";

interface LoginScreenProps {
  onLoginSuccess: () => void;
}

export function LoginScreen({ onLoginSuccess }: LoginScreenProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });

      setToken(response.access_token);
      onLoginSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar sesion");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center">
      {/* Background with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0.9)), 
            url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920&q=80')`,
        }}
      />
      
      {/* Login box */}
      <div className="relative z-10 w-full max-w-md mx-4 bg-card/95 backdrop-blur-sm rounded-lg p-8">
        <div className="flex flex-col items-center gap-6">
          <BrandLogo size="lg" />
          
          <h2 className="text-2xl font-semibold text-foreground">Iniciar sesion</h2>
          
          <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-foreground mb-2">
                Usuario o email
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-secondary text-foreground rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-muted-foreground"
                placeholder="Ingresa tu usuario o email"
                required
                disabled={loading}
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                Contrasena
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-secondary text-foreground rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-muted-foreground pr-12"
                  placeholder="Ingresa tu contrasena"
                  required
                  disabled={loading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? "Ocultar contrasena" : "Mostrar contrasena"}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>
            
            {error && (
              <p className="text-primary text-sm text-center">{error}</p>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Entrando...
                </>
              ) : (
                "Entrar"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
