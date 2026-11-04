import type { LucideIcon } from 'lucide-react';
import { GradientIcon } from './Gradient';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  index: number;
  badge?: string;
  badgeTone?: 'positive' | 'neutral' | 'info';
}

export function StatCard({ icon, label, value, index, badge, badgeTone = 'positive' }: StatCardProps) {
  const badgeColors = {
    positive: 'bg-[#E4F2E9] text-[#2E7D4F] border-[#B7DFCA]',
    neutral: 'bg-muted text-muted-foreground border-border',
    info: 'bg-[#E5EAF6] text-[#3B5BA9] border-[#C3D0EE]',
  };

  return (
    <div className="flex flex-col justify-between rounded-[10px] bg-card p-5 shadow-card transition-all duration-200 hover:shadow-md">
      <div className="flex items-center justify-between gap-2">
        <GradientIcon icon={icon} index={index} />
        {badge && (
          <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-bold tracking-tight ${badgeColors[badgeTone]}`}>
            {badge}
          </span>
        )}
      </div>
      <div className="mt-4 min-w-0">
        <p className="text-[13px] font-medium text-muted-foreground">{label}</p>
        <p className="truncate text-[28px] font-black leading-tight tracking-tight">{value}</p>
      </div>
    </div>
  );
}
