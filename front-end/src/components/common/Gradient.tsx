import type { LucideIcon } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

/** Các cặp gradient sáng, xoay vòng cho ô icon thống kê và thanh biểu đồ. */
export const BRIGHT_GRADIENTS = [
  ['#FF7A3D', '#FFC93C'],
  ['#FF5E7E', '#FFB38A'],
  ['#FFA62B', '#FFE36E'],
  ['#FF7EB3', '#FF9F5A'],
  ['#FFB38A', '#FFE066'],
  ['#E8112D', '#FF7EB3'],
] as const;

export function gradientAt(index: number, direction = '135deg'): string {
  const [from, to] = BRIGHT_GRADIENTS[index % BRIGHT_GRADIENTS.length];
  return `linear-gradient(${direction}, ${from}, ${to})`;
}

export function GradientIcon({ icon: Icon, index, size = 48 }: { icon: LucideIcon; index: number; size?: number }) {
  return (
    <span
      className="flex shrink-0 items-center justify-center rounded-[10px] text-white"
      style={{ width: size, height: size, background: gradientAt(index) }}
    >
      <Icon style={{ width: size / 2, height: size / 2 }} />
    </span>
  );
}

interface BarProps {
  /** 0–1; null/undefined = chưa có số. */
  value?: number | null;
  max?: number;
  background: string;
  className?: string;
}

/** Thanh ngang tỉ lệ; khi thiếu dữ liệu chỉ vẽ rãnh trống. */
export function Bar({ value, max = 1, background, className }: BarProps) {
  const width = value == null || max <= 0 ? 0 : Math.max(0, Math.min(1, value / max)) * 100;
  return (
    <div className={cn('h-3 w-full overflow-hidden rounded-full bg-muted', className)}>
      <div className="h-full rounded-full transition-[width]" style={{ width: `${width}%`, background }} />
    </div>
  );
}
