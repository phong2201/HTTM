import type { ComponentProps, ReactNode } from 'react';
import { cn } from '@/app/components/ui/utils';

export const controlClass =
  'h-10 w-full rounded-lg border border-border-strong bg-card px-3 text-sm outline-none transition focus-visible:border-primary focus-visible:ring-[3px] focus-visible:ring-primary/20 disabled:opacity-50';

export function Field({ label, htmlFor, children, className }: { label: string; htmlFor?: string; children: ReactNode; className?: string }) {
  return (
    <div className={cn('space-y-1.5', className)}>
      <label htmlFor={htmlFor} className="block text-[13px] font-semibold">{label}</label>
      {children}
    </div>
  );
}

export function NativeSelect({ className, ...props }: ComponentProps<'select'>) {
  return <select className={cn(controlClass, 'pr-8', className)} {...props} />;
}

export function TextArea({ className, ...props }: ComponentProps<'textarea'>) {
  return <textarea className={cn(controlClass, 'h-auto py-2', className)} {...props} />;
}
