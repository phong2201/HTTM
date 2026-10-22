import type { ReactNode } from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/app/components/ui/alert';

const ICONS = {
  success: CheckCircle2,
  destructive: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

interface NoticeProps {
  tone: keyof typeof ICONS;
  title?: string;
  children: ReactNode;
  className?: string;
}

/** Banner thông báo: thành công (xanh), lỗi (đỏ, có viền), cảnh báo, thông tin. */
export function Notice({ tone, title, children, className }: NoticeProps) {
  const Icon = ICONS[tone];
  return (
    <Alert variant={tone} className={className}>
      <Icon />
      {title && <AlertTitle className="font-bold">{title}</AlertTitle>}
      <AlertDescription>{children}</AlertDescription>
    </Alert>
  );
}
