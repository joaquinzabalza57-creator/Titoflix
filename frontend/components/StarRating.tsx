"use client";

import { Star } from "lucide-react";
import { useState } from "react";

type StarRatingProps = {
  value: number;
  onChange?: (value: number) => void;
  readOnly?: boolean;
  size?: number;
  label?: string;
};

export function StarRating({ value, onChange, readOnly = false, size = 22, label }: StarRatingProps) {
  const [hoverValue, setHoverValue] = useState(0);
  const displayValue = hoverValue || value;

  return (
    <div className="flex items-center gap-1" aria-label={label}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          disabled={readOnly}
          onClick={() => onChange?.(star)}
          onMouseEnter={() => !readOnly && setHoverValue(star)}
          onMouseLeave={() => setHoverValue(0)}
          className={`rounded-sm transition-transform ${
            readOnly ? "cursor-default" : "cursor-pointer hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary"
          }`}
          aria-label={`${star} estrellas`}
        >
          <Star
            size={size}
            className={star <= displayValue ? "fill-yellow-500 text-yellow-500" : "text-muted-foreground"}
          />
        </button>
      ))}
    </div>
  );
}
