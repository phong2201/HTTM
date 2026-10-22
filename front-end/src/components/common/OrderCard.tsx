import type { ReactNode } from 'react';
import type { OrderResponse } from '@/services/api';
import { formatDateTime, formatPrice, shortId } from '@/lib/format';
import { OrderStatusBadge } from './OrderStatus';

interface OrderCardProps {
  order: OrderResponse;
  /** Dòng phụ dưới mã đơn; mặc định là ngày giờ đặt. */
  subtitle?: ReactNode;
  /** Thay badge trạng thái (vd select trạng thái ở Admin). */
  status?: ReactNode;
  actions?: ReactNode;
}

/** Card đơn hàng dùng chung cho Lịch sử đơn (09) và Admin · Đơn hàng (13). */
export function OrderCard({ order, subtitle, status, actions }: OrderCardProps) {
  return (
    <article className="rounded-[10px] bg-card p-5 shadow-card">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="font-bold">Đơn #{shortId(order.id)}</p>
          <p className="text-[13px] text-muted-foreground">{subtitle ?? formatDateTime(order.order_date)}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-lg font-bold text-primary">{formatPrice(order.total_amount)}</span>
          {status ?? <OrderStatusBadge status={order.status} />}
          {actions}
        </div>
      </div>
      <div className="divide-y divide-border border-t border-border">
        {order.items.map((item) => (
          <div key={item.id} className="flex items-center justify-between gap-4 py-2.5 text-sm">
            <span className="min-w-0 truncate">
              {item.product?.prod_name || item.product_id} <span className="text-muted-foreground">x {item.quantity}</span>
            </span>
            <span className="shrink-0 font-semibold">{formatPrice(item.subtotal)}</span>
          </div>
        ))}
      </div>
    </article>
  );
}
