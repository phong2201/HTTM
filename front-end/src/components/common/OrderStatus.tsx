import { Badge } from '@/app/components/ui/badge';

type Tone = 'warning' | 'info' | 'success' | 'danger' | 'neutral';

/** Trạng thái đơn theo OrderStatus của backend (0–3). */
export const ORDER_STATUSES: Array<{ value: number; key: string; label: string; adminLabel: string; tone: Tone }> = [
  { value: 0, key: 'PENDING', label: 'Đang xử lý', adminLabel: 'Pending', tone: 'warning' },
  { value: 1, key: 'DELIVERING', label: 'Đang giao', adminLabel: 'Delivering', tone: 'info' },
  { value: 2, key: 'COMPLETED', label: 'Hoàn tất', adminLabel: 'Completed', tone: 'success' },
  { value: 3, key: 'CANCELLED', label: 'Đã hủy', adminLabel: 'Cancelled', tone: 'danger' },
];

export function orderStatusValue(status: number | string): number {
  const found = ORDER_STATUSES.find((s) => String(s.value) === String(status) || s.key === String(status).toUpperCase());
  return found?.value ?? -1;
}

export const ORDER_COMPLETED = 2;

export function OrderStatusBadge({ status }: { status: number | string }) {
  const found = ORDER_STATUSES.find((s) => s.value === orderStatusValue(status));
  return <Badge variant={found?.tone ?? 'neutral'}>{found?.label ?? String(status)}</Badge>;
}
