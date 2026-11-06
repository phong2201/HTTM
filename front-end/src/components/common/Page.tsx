import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, type LucideIcon } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

/** Khung nội dung 1280px với hiệu ứng xuất hiện mượt mà. */
export function Container({ className, children }: { className?: string; children: ReactNode }) {
  return <div className={cn('mx-auto w-full max-w-[1280px] px-4 xl:px-0 animate-fade-up', className)}>{children}</div>;
}

interface PageHeaderProps {
  title: string;
  description?: ReactNode;
  icon?: LucideIcon;
  actions?: ReactNode;
}

/** Đầu trang: khối icon nổi bật + tiêu đề 30px Black + mô tả + nút bên phải. */
export function PageHeader({ title, description, icon: Icon, actions }: PageHeaderProps) {
  return (
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4 border-b border-border/70 pb-5">
      <div className="flex items-center gap-3.5">
        {Icon && (
          <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-canvas text-primary shadow-2xs ring-1 ring-primary/15">
            <Icon className="size-6" />
          </span>
        )}
        <div>
          <h1 className="text-[30px] font-black tracking-tight">{title}</h1>
          {description && <p className="mt-1 text-[15px] text-muted-foreground">{description}</p>}
        </div>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2.5">{actions}</div>}
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
    <div className="mb-6 flex items-end justify-between gap-4">
      <div className="flex items-center gap-3">
        {Icon && (
          <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-accent/80 text-primary ring-1 ring-primary/15">
            <Icon className="size-5 fill-primary/15" />
          </span>
        )}
        <div>
          <h2 className="text-2xl font-black tracking-tight">{title}</h2>
          {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
        </div>
      </div>
      {viewAllTo && (
        <Link
          to={viewAllTo}
          className="group flex shrink-0 items-center gap-1 rounded-full bg-card px-3.5 py-1.5 text-sm font-semibold text-primary shadow-2xs ring-1 ring-border transition-all hover:bg-primary hover:text-white hover:ring-primary"
        >
          Xem tất cả <ChevronRight className="size-4 transition-transform group-hover:translate-x-0.5" />
        </Link>
      )}
    </div>
  );
}

/** Card trắng bo 12px, viền tinh tế, đổ bóng nhẹ. */
export function Panel({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section className={cn('rounded-xl border border-border/80 bg-card p-6 shadow-card transition-shadow duration-200 hover:shadow-md', className)}>
      {children}
    </section>
  );
}

export function PanelTitle({ icon: Icon, children, aside }: { icon?: LucideIcon; children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <h2 className="flex items-center gap-2 text-lg font-bold tracking-tight">
        {Icon && (
          <span className="flex size-7 items-center justify-center rounded-lg bg-accent/70 text-primary">
            <Icon className="size-4" />
          </span>
        )}
        {children}
      </h2>
      {aside}
    </div>
  );
}
