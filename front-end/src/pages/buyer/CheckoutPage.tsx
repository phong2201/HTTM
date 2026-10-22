import { useState, type ChangeEvent, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, MapPin, Truck, Landmark } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { cn } from '@/app/components/ui/utils';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { Field, NativeSelect, TextArea } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { ProductImage } from '@/components/common/ProductImage';
import { useShop } from '@/context/ShopContext';
import { apiService } from '@/services/api';
import { errorMessage, formatPrice } from '@/lib/format';

const PROVINCES: Record<string, string[]> = {
  'Hà Nội': ['Ba Đình', 'Hoàn Kiếm', 'Cầu Giấy', 'Đống Đa', 'Hai Bà Trưng'],
  'TP. Hồ Chí Minh': ['Quận 1', 'Quận 3', 'Quận 10', 'Bình Thạnh', 'Thủ Đức'],
  'Đà Nẵng': ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Ngũ Hành Sơn'],
  'Hải Phòng': ['Hồng Bàng', 'Lê Chân', 'Ngô Quyền'],
  'Cần Thơ': ['Ninh Kiều', 'Bình Thủy', 'Cái Răng'],
};

const PAYMENT_METHODS = [
  { id: 'cod', icon: Truck, title: 'Thanh toán khi nhận hàng (COD)', description: 'Thanh toán bằng tiền mặt khi nhận hàng' },
  { id: 'bank', icon: Landmark, title: 'Chuyển khoản ngân hàng', description: 'Chuyển khoản qua Internet Banking' },
];

/** Màn 08 · Thanh toán. */
export function CheckoutPage() {
  const { cartItems, cartTotal, clearCart } = useShop();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ name: '', phone: '', email: '', address: '', city: '', district: '', paymentMethod: 'cod', note: '' });

  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value, ...(name === 'city' ? { district: '' } : {}) }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await apiService.createOrder(
        cartItems.map((item) => ({ product_id: item.id, quantity: item.quantity })),
        [form.name, form.phone, form.email, `${form.address}, ${form.district}, ${form.city}`, form.paymentMethod, form.note].join(' | '),
      );
      clearCart();
      toast.success('Đặt hàng thành công! Cảm ơn bạn đã mua hàng.');
      navigate('/orders');
    } catch (err) {
      setError(errorMessage(err, 'Không đặt được đơn hàng'));
    } finally {
      setSubmitting(false);
    }
  };

  if (cartItems.length === 0) {
    return (
      <Container className="py-8">
        <PageHeader title="Thanh toán" />
        <EmptyState {...EMPTY.cart} />
      </Container>
    );
  }

  return (
    <Container className="py-8">
      <PageHeader title="Thanh toán" />
      {error && <Notice tone="destructive" className="mb-4">{error}</Notice>}

      <form onSubmit={handleSubmit} className="grid items-start gap-8 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <Panel>
            <PanelTitle icon={MapPin}>Thông tin giao hàng</PanelTitle>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Họ và tên *" htmlFor="name" className="md:col-span-2">
                <Input id="name" name="name" required value={form.name} onChange={handleChange} />
              </Field>
              <Field label="Số điện thoại *" htmlFor="phone">
                <Input id="phone" name="phone" type="tel" required value={form.phone} onChange={handleChange} />
              </Field>
              <Field label="Email" htmlFor="email">
                <Input id="email" name="email" type="email" value={form.email} onChange={handleChange} />
              </Field>
              <Field label="Địa chỉ *" htmlFor="address" className="md:col-span-2">
                <Input id="address" name="address" required value={form.address} onChange={handleChange} />
              </Field>
              <Field label="Tỉnh/Thành *" htmlFor="city">
                <NativeSelect id="city" name="city" required value={form.city} onChange={handleChange}>
                  <option value="">Chọn tỉnh/thành</option>
                  {Object.keys(PROVINCES).map((city) => <option key={city}>{city}</option>)}
                </NativeSelect>
              </Field>
              <Field label="Quận/Huyện *" htmlFor="district">
                <NativeSelect id="district" name="district" required value={form.district} onChange={handleChange} disabled={!form.city}>
                  <option value="">Chọn quận/huyện</option>
                  {(PROVINCES[form.city] ?? []).map((district) => <option key={district}>{district}</option>)}
                </NativeSelect>
              </Field>
              <Field label="Ghi chú" htmlFor="note" className="md:col-span-2">
                <TextArea id="note" name="note" rows={3} value={form.note} onChange={handleChange} />
              </Field>
            </div>
          </Panel>

          <Panel>
            <PanelTitle icon={CreditCard}>Phương thức thanh toán</PanelTitle>
            <div className="space-y-3">
              {PAYMENT_METHODS.map(({ id, icon: Icon, title, description }) => {
                const active = form.paymentMethod === id;
                return (
                  <label key={id} className={cn('flex cursor-pointer items-center gap-3 rounded-lg border p-4 transition', active ? 'border-primary bg-accent' : 'border-border-strong hover:bg-canvas')}>
                    <input type="radio" name="paymentMethod" value={id} checked={active} onChange={handleChange} className="size-4 accent-primary" />
                    <Icon className={cn('size-6', active ? 'text-primary' : 'text-muted-foreground')} />
                    <div>
                      <p className="font-semibold">{title}</p>
                      <p className="text-[13px] text-muted-foreground">{description}</p>
                    </div>
                  </label>
                );
              })}
            </div>
          </Panel>
        </div>

        <Panel className="lg:sticky lg:top-24">
          <PanelTitle>Đơn hàng ({cartItems.length} sản phẩm)</PanelTitle>
          <div className="mb-4 max-h-72 space-y-3 overflow-y-auto pr-1 pt-2">
            {cartItems.map((item) => (
              <div key={item.id} className="flex gap-3">
                <div className="relative shrink-0">
                  <ProductImage src={item.image} alt={item.name} className="size-16 rounded-lg" iconSize={20} />
                  <span className="absolute -right-2 -top-2 flex size-5 items-center justify-center rounded-full bg-primary text-[11px] font-bold text-white">{item.quantity}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="line-clamp-2 text-sm">{item.name}</p>
                  <p className="text-sm font-semibold text-primary">{formatPrice(item.price)}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="space-y-2 border-t border-border pt-4 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Tạm tính</span><span className="font-semibold">{formatPrice(cartTotal)}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Phí vận chuyển</span><span className="font-semibold text-success">Miễn phí</span></div>
            <div className="flex justify-between border-t border-border pt-3 text-xl font-bold"><span>Tổng cộng</span><span className="text-primary">{formatPrice(cartTotal)}</span></div>
          </div>
          <Button type="submit" size="lg" className="mt-5 w-full" disabled={submitting}>
            {submitting ? 'Đang đặt hàng...' : 'Đặt hàng'}
          </Button>
        </Panel>
      </form>
    </Container>
  );
}
