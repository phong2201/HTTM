import { useEffect, useState } from 'react';
import { Star } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/app/components/ui/dialog';
import { cn } from '@/app/components/ui/utils';
import { Container, PageHeader } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { TextArea } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { OrderCard } from '@/components/common/OrderCard';
import { ORDER_COMPLETED, orderStatusValue } from '@/components/common/OrderStatus';
import { useAuth } from '@/context/AuthContext';
import { apiService, type OrderResponse } from '@/services/api';
import { errorMessage, shortId } from '@/lib/format';

/** Màn 09 · Lịch sử đơn hàng (+ bước Feedback cho đơn Hoàn tất). */
export function OrdersPage() {
  const [orders, setOrders] = useState<OrderResponse[] | null>(null);
  const [error, setError] = useState('');
  const [reviewing, setReviewing] = useState<OrderResponse | null>(null);

  useEffect(() => {
    apiService.getMyOrders()
      .then((data) => setOrders([...data].sort((a, b) => b.order_date.localeCompare(a.order_date))))
      .catch((err) => { setOrders([]); setError(errorMessage(err, 'Không tải được đơn hàng')); });
  }, []);

  return (
    <Container className="py-8">
      <PageHeader title="Lịch sử đơn hàng" description="Các đơn hàng đã đặt qua thanh toán" />
      {error && <Notice tone="destructive" className="mb-4">{error}</Notice>}
      {orders === null ? (
        <p className="text-sm text-muted-foreground">Đang tải...</p>
      ) : orders.length === 0 ? (
        <EmptyState {...EMPTY.orders} />
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              actions={orderStatusValue(order.status) === ORDER_COMPLETED && (
                <Button variant="outlineRed" size="sm" onClick={() => setReviewing(order)}>
                  <Star /> Đánh giá
                </Button>
              )}
            />
          ))}
        </div>
      )}
      <ReviewOrderDialog order={reviewing} onClose={() => setReviewing(null)} />
    </Container>
  );
}

function ReviewOrderDialog({ order, onClose }: { order: OrderResponse | null; onClose: () => void }) {
  const { user } = useAuth();
  const [rank, setRank] = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    setRank(5);
    setComment('');
  }, [order?.id]);

  const submit = async () => {
    if (!order || !user?.id) return;
    setSubmitting(true);
    try {
      await apiService.evaluateOrder(user.id, order, rank, comment);
      toast.success('Cảm ơn bạn đã đánh giá đơn hàng');
      onClose();
    } catch (err) {
      toast.error(errorMessage(err, 'Không gửi được đánh giá'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={Boolean(order)} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">Đánh giá đơn #{order ? shortId(order.id) : ''}</DialogTitle>
          <DialogDescription>Điểm đánh giá được ghi cho từng sản phẩm trong đơn.</DialogDescription>
        </DialogHeader>
        <div className="flex justify-center gap-1 py-2">
          {[1, 2, 3, 4, 5].map((value) => (
            <button key={value} type="button" onClick={() => setRank(value)} aria-label={`${value} sao`}>
              <Star className={cn('size-9', value <= rank ? 'fill-[#FFB020] text-[#FFB020]' : 'text-border-strong')} />
            </button>
          ))}
        </div>
        <TextArea rows={3} placeholder="Nhận xét của bạn (không bắt buộc)" value={comment} onChange={(e) => setComment(e.target.value)} />
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Hủy</Button>
          <Button onClick={submit} disabled={submitting}>{submitting ? 'Đang gửi...' : 'Gửi đánh giá'}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
