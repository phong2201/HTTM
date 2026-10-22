import { Star } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

export function Stars({ value, size = 14, className }: { value?: number | null; size?: number; className?: string }) {
  const filled = Math.round(value ?? 0);
  return (
    <span className={cn('inline-flex items-center gap-0.5', className)}>
      {Array.from({ length: 5 }, (_, i) => (
        <Star
          key={i}
          style={{ width: size, height: size }}
          className={i < filled ? 'fill-[#FFB020] text-[#FFB020]' : 'text-border-strong'}
        />
      ))}
    </span>
  );
}
