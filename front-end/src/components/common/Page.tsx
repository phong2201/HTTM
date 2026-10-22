import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, type LucideIcon } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

/** Khung nội dung 1280px. */
export function Container({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('mx-auto w-full max-w-[1280px] px-4 xl:px-0', className)}>{children}</div>;
}

interface PageHeaderProps {
  title: string;
  description?: ReactNode;
  icon?: LucideIcon;
  actions?: ReactNode;
}

/** Đầu trang: (icon đỏ 32px) + tiêu đề 30px Black + mô tả + nút bên phải. */
export function PageHeader({ title, description, icon: Icon, actions }: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div className="flex items-center gap-3">
        {Icon && <Icon className="size-8 shrink-0 text-primary" />}
        <div>
          <h1 className="text-[30px] font-black tracking-tight">{title}</h1>
          {description && <p className="mt-1 text-[15px] text-muted-foreground">{description}</p>}
        </div>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

interface SectionHeaderProps {
  title: string;
  description?: ReactNode;
  icon?: LucideIcon;
  viewAllTo?: string;
}

export function SectionHeader({ title, description, icon: Icon, viewAllTo }: SectionHeaderProps) {
  return (
    <div className="mb-5 flex items-end justify-between gap-4">
      <div className="flex items-center gap-3">
        {Icon && <Icon className="size-7 shrink-0 fill-primary/15 text-primary" />}
        <div>
          <h2 className="text-2xl font-black tracking-tight">{title}</h2>
          {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
        </div>
      </div>
      {viewAllTo && (
        <Link to={viewAllTo} className="flex shrink-0 items-center gap-0.5 text-sm font-semibold text-primary hover:underline">
          Xem tất cả <ChevronRight className="size-4" />
        </Link>
      )}
    </div>
  );
}

/** Card trắng bo 10, đổ bóng nhẹ. */
export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return <section className={cn('rounded-[10px] bg-card p-6 shadow-card', className)}>{children}</section>;
}

export function PanelTitle({ icon: Icon, children, aside }: { icon?: LucideIcon; children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <h2 className="flex items-center gap-2 text-lg font-bold">
        {Icon && <Icon className="size-5 text-primary" />}
        {children}
      </h2>
      {aside}
    </div>
  );
}
