import type { ReactNode } from 'react';
import { Sparkles } from 'lucide-react';

/** Nền gradient hồng nhạt sống động với ánh sáng mờ, logo HUB 40px trên card trắng 448px (màn 01–02). */
export function AuthLayout({ title, description, children }: { title: string; description: string; children: ReactNode }) {
  return (
    <div className="relative flex min-h-dvh flex-col items-center justify-center gap-6 overflow-hidden bg-gradient-to-br from-canvas via-[#FFE8EC] to-accent p-4">
      {/* Hạt sáng trang trí nền */}
      <div className="pointer-events-none absolute -left-24 -top-24 size-96 rounded-full bg-[#FF7A3D]/15 blur-3xl animate-float-slow" />
      <div className="pointer-events-none absolute -bottom-28 -right-20 size-96 rounded-full bg-primary/15 blur-3xl animate-float-slow" />

      <div className="relative flex flex-col items-center gap-1.5 animate-fade-up">
        <div className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-white/80 px-3 py-1 text-xs font-semibold text-primary shadow-2xs backdrop-blur-xs">
          <Sparkles className="size-3.5" />
          <span>AI-Powered Fashion Recommendation</span>
        </div>
        <span className="bg-gradient-to-r from-[#E8112D] to-[#FF7A3D] bg-clip-text text-[42px] font-black leading-none tracking-tight text-transparent">
          HUB
        </span>
      </div>

      <div className="relative w-full max-w-[448px] rounded-2xl border border-white/80 bg-card/95 p-8 shadow-xl backdrop-blur-sm animate-fade-up">
        <h1 className="text-[26px] font-black tracking-tight">{title}</h1>
        <p className="mb-6 mt-1 text-sm text-muted-foreground">{description}</p>
        {children}
      </div>
    </div>
  );
}
