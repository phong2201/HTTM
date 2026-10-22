import type { ReactNode } from 'react';

/** Nền gradient hồng nhạt, logo HUB 40px trên card trắng 448px (màn 01–02). */
export function AuthLayout({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-gradient-to-br from-canvas to-accent p-4">
      <span className="text-[40px] font-black leading-none tracking-tight text-primary">HUB</span>
      <div className="w-full max-w-[448px] rounded-[10px] bg-card p-8 shadow-card">
        <h1 className="text-[26px] font-bold">{title}</h1>
        <p className="mb-6 mt-1 text-sm text-muted-foreground">{description}</p>
        {children}
      </div>
    </div>
  );
}
