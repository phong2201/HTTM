import { useEffect, useMemo, useState } from 'react';
import { NativeSelect } from '@/components/common/Field';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { OrderCard } from '@/components/common/OrderCard';
import { ORDER_STATUSES, orderStatusValue } from '@/components/common/OrderStatus';
import { apiService, type OrderResponse } from '@/services/api';
import { errorMessage } from '@/lib/format';
import { TabToolbar, type AdminTabProps } from './shared';

const TIME_PERIODS = [
  { value: '', label: 'Mọi thời gian' },
  { value: '7', label: '7 ngày qua' },
  { value: '30', label: '30 ngày qua' },
  { value: '90', label: '90 ngày qua' },
];

const categoryOf = (item: OrderResponse['items'][number]) => item.product?.index_group_name ?? null;

/** Màn 13 · Admin · Đơn hàng. Lọc time_period / category phía client. */
export function OrdersTab({ reloadKey, tabBar, onSuccess, onError }: AdminTabProps) {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [timePeriod, setTimePeriod] = useState('');
  const [category, setCategory] = useState('');

  useEffect(() => {
    apiService.getAllOrders()
      .then((data) => setOrders([...data].sort((a, b) => b.order_date.localeCompare(a.order_date))))
      .catch((err) => onError(errorMessage(err, 'Không tải được đơn hàng')));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reloadKey]);

  const categories = useMemo(
    () => Array.from(new Set(orders.flatMap((o) => o.items.map(categoryOf)).filter((c): c is string => Boolean(c)))).sort(),
    [orders],
  );

  const filtered = orders.filter((order) => {
    if (timePeriod && Date.now() - new Date(order.order_date).getTime() > Number(timePeriod) * 86_400_000) return false;
    if (category && !order.items.some((item) => categoryOf(item) === category)) return false;
    return true;
  });

  const updateStatus = async (order: OrderResponse, status: number) => {
    try {
      const saved = await apiService.updateOrderStatus(order.id, status);
      setOrders((prev) => prev.map((o) => (o.id === saved.id ? saved : o)));
      onSuccess('Đã cập nhật trạng thái đơn hàng');
    } catch (err) {
      onError(errorMessage(err, 'Không cập nhật được trạng thái'));
    }
  };

  return (
    <>
      <TabToolbar tabBar={tabBar}>
        <NativeSelect aria-label="time_period" value={timePeriod} onChange={(e) => setTimePeriod(e.target.value)} className="w-44">
          {TIME_PERIODS.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
        </NativeSelect>
        <NativeSelect aria-label="category" value={category} onChange={(e) => setCategory(e.target.value)} className="w-44">
          <option value="">Mọi danh mục</option>
          {categories.map((c) => <option key={c}>{c}</option>)}
        </NativeSelect>
      </TabToolbar>

      {filtered.length === 0 ? (
        <EmptyState {...EMPTY.orders} />
      ) : (
        <div className="space-y-4">
          {filtered.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              subtitle={`User: ${order.user_id}`}
              status={
                <NativeSelect value={orderStatusValue(order.status)} onChange={(e) => updateStatus(order, Number(e.target.value))} className="h-9 w-36">
                  {ORDER_STATUSES.map((s) => <option key={s.value} value={s.value}>{s.adminLabel}</option>)}
                </NativeSelect>
              }
            />
          ))}
        </div>
      )}
    </>
  );
}
