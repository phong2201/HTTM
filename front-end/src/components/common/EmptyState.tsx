import type { ReactNode } from 'react';
import { HeartOff, PackageSearch, PackageX, ShieldOff, ShoppingCart, Sparkles, type LucideIcon } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';

/** Câu chữ cố định theo màn 10 · Trạng thái rỗng & lỗi. */
export const EMPTY = {
  products: { icon: PackageSearch, title: 'Chưa có sản phẩm', description: 'Không tìm thấy sản phẩm phù hợp. Thử đổi bộ lọc hoặc kiểm tra dữ liệu backend.' },
  wishlist: { icon: HeartOff, title: 'Wishlist trống', description: 'Bấm ♥ trên sản phẩm để lưu lại những món bạn thích.' },
  orders: { icon: PackageX, title: 'Chưa có đơn hàng', description: 'Các đơn bạn đặt qua thanh toán sẽ hiển thị ở đây.' },
  cart: { icon: ShoppingCart, title: 'Giỏ hàng trống', description: 'Thêm sản phẩm vào giỏ để bắt đầu thanh toán.' },
  coldStart: { icon: Sparkles, title: 'Chưa có lịch sử mua (cold start)', description: 'Bạn chưa có lịch sử mua — đang hiển thị sản phẩm bán chạy.' },
  forbidden: { icon: ShieldOff, title: 'Không có quyền truy cập', description: 'Tài khoản của bạn không có quyền xem trang này.' },
} satisfies Record<string, { icon: LucideIcon; title: string; description: string }>;

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex min-h-[280px] flex-col items-center justify-center gap-2 rounded-[10px] border-2 border-dashed border-border-strong bg-card p-8 text-center', className)}>
      <Icon className="mb-2 size-10 text-faint" strokeWidth={1.5} />
      <h3 className="text-[17px] font-bold">{title}</h3>
      {description && <p className="max-w-md text-[13px] text-muted-foreground">{description}</p>}
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
