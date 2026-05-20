"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { Loader2, Lock, X } from "lucide-react";

type PinModalProps = {
  profileName: string;
  loading?: boolean;
  error?: string | null;
  onSubmit: (pin: string) => void;
  onCancel: () => void;
};

export function PinModal({ profileName, loading = false, error, onSubmit, onCancel }: PinModalProps) {
  const [digits, setDigits] = useState(["", "", "", ""]);
  const [now, setNow] = useState(() => Date.now());
  const inputs = useRef<Array<HTMLInputElement | null>>([]);
  const lockedUntil = getLockedUntil(error);
  const remainingSeconds = lockedUntil ? Math.max(0, Math.ceil((lockedUntil.getTime() - now) / 1000)) : 0;
  const isLocked = remainingSeconds > 0;
  const displayError = isLocked
    ? `Perfil bloqueado hasta dentro de ${formatRemainingTime(remainingSeconds)}`
    : error;

  useEffect(() => {
    inputs.current[0]?.focus();
  }, []);

  useEffect(() => {
    if (!lockedUntil) return;
    setNow(Date.now());
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [lockedUntil?.getTime()]);

  const setDigit = (index: number, value: string) => {
    if (isLocked) return;
    if (!/^\d*$/.test(value)) return;
    const next = [...digits];
    next[index] = value.slice(-1);
    setDigits(next);

    if (value && index < 3) {
      inputs.current[index + 1]?.focus();
    }
    if (value && index === 3 && next.every(Boolean)) {
      onSubmit(next.join(""));
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isLocked) return;
    const pin = digits.join("");
    if (pin.length === 4) {
      onSubmit(pin);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4">
      <form onSubmit={handleSubmit} className="relative w-full max-w-sm rounded-lg border border-border bg-card p-6 shadow-2xl">
        <button
          type="button"
          onClick={onCancel}
          className="absolute right-4 top-4 rounded-full p-1 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          aria-label="Cerrar"
        >
          <X size={20} />
        </button>

        <div className="mb-5 flex justify-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
            <Lock size={28} className="text-primary" />
          </div>
        </div>

        <h2 className="mb-2 text-center text-xl font-semibold text-foreground">PIN de {profileName}</h2>
        <div className="mb-5 flex justify-center gap-2">
          {digits.map((digit, index) => (
            <input
              key={index}
              ref={(element) => {
                inputs.current[index] = element;
              }}
              type="password"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              disabled={loading || isLocked}
              onChange={(event) => setDigit(index, event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Backspace" && !digits[index] && index > 0) {
                  inputs.current[index - 1]?.focus();
                }
              }}
              className="h-12 w-12 rounded-md border border-border bg-background text-center text-xl font-bold text-foreground outline-none transition-colors focus:border-primary disabled:opacity-60"
              aria-label={`Digito ${index + 1} del PIN`}
            />
          ))}
        </div>

        {displayError && (
          <p className="mb-4 rounded-md border border-primary/60 bg-primary/10 px-3 py-2 text-center text-sm text-primary">
            {displayError}
          </p>
        )}

        <button
          type="submit"
          disabled={loading || isLocked || digits.join("").length !== 4}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-3 font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <Lock size={18} />}
          Entrar
        </button>
      </form>
    </div>
  );
}

function getLockedUntil(error?: string | null): Date | null {
  const match = error?.match(/Perfil bloqueado hasta\s+(.+)$/);
  if (!match) return null;
  const rawTimestamp = match[1].trim();
  const timestamp = /(?:Z|[+-]\d{2}:?\d{2})$/.test(rawTimestamp)
    ? rawTimestamp
    : `${rawTimestamp}Z`;
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime()) ? null : date;
}

function formatRemainingTime(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}
