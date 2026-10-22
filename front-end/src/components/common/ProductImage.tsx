import { useState } from 'react';
import { ImageIcon } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

interface ProductImageProps {
  src?: string | null;
  alt: string;
  className?: string;
  iconSize?: number;
}

/** Ảnh sản phẩm; thiếu ảnh hoặc lỗi → ô nền imgPh + icon ảnh. */
export function ProductImage({ src, alt, className, iconSize = 32 }: ProductImageProps) {
  const [failed, setFailed] = useState(false);

  if (!src || failed) {
    return (
      <div className={cn('flex items-center justify-center bg-img-ph text-faint', className)} aria-label={alt}>
        <ImageIcon style={{ width: iconSize, height: iconSize }} strokeWidth={1.5} />
      </div>
    );
  }

  return <img src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} className={cn('bg-img-ph object-cover', className)} />;
}
