import type { ReactNode } from 'react';
import { cn } from '@/app/components/ui/utils';

const COLUMNS = {
  4: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4',
  5: 'grid-cols-2 md:grid-cols-3 lg:grid-cols-5',
};

export function ProductGrid({ columns = 4, className, children }: { columns?: 4 | 5; className?: string; children: ReactNode }) {
  return <div className={cn('grid gap-5', COLUMNS[columns], className)}>{children}</div>;
}
