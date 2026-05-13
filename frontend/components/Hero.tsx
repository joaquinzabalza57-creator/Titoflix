"use client";

import { Play, List } from "lucide-react";

interface HeroProps {
  onExplore: () => void;
  onMiLista: () => void;
}

export function Hero({ onExplore, onMiLista }: HeroProps) {
  return (
    <div className="relative h-[80vh] md:h-[90vh] w-full flex items-center">
      {/* Background with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(8,8,8,0.95) 0%, rgba(8,8,8,0.7) 50%, rgba(8,8,8,0.4) 100%), 
            linear-gradient(to top, rgba(8,8,8,1) 0%, rgba(8,8,8,0) 30%),
            url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1920&q=80')`,
        }}
      />
      
      {/* Content */}
      <div className="relative z-10 px-4 md:px-8 lg:px-16 max-w-3xl">
        {/* Tag */}
        <div className="inline-block px-3 py-1 bg-primary text-primary-foreground text-xs font-semibold rounded mb-4">
          BIENVENIDO
        </div>
        
        {/* Title */}
        <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold mb-4">
          <span className="text-tito-green">TIT</span>
          <span className="text-tito-white">O</span>
          <span className="text-tito-red">FLIX</span>
        </h1>
        
        {/* Description */}
        <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-xl leading-relaxed">
          Explora nuestra coleccion de peliculas y series. Disfruta del mejor contenido 
          en streaming desde la comodidad de tu hogar.
        </p>
        
        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={onExplore}
            className="flex items-center justify-center gap-2 px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Play size={20} fill="currentColor" />
            Explorar
          </button>
          <button
            onClick={onMiLista}
            className="flex items-center justify-center gap-2 px-8 py-3 bg-secondary text-secondary-foreground font-semibold rounded-lg hover:bg-secondary/80 transition-colors border border-border"
          >
            <List size={20} />
            Mi lista
          </button>
        </div>
      </div>
    </div>
  );
}
