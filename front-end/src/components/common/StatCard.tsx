import type { LucideIcon } from 'lucide-react';
import { GradientIcon } from './Gradient';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  index: number;
}

export function StatCard({ icon, label, value, index }: StatCardProps) {
  return (
    <div className="flex items-center gap-4 rounded-[10px] bg-card p-5 shadow-card">
      <GradientIcon icon={icon} index={index} />
      <div className="min-w-0">
        <p className="text-[13px] text-muted-foreground">{label}</p>
        <p className="truncate text-[28px] font-black leading-tight">{value}</p>
      </div>
    </div>
  );
}
