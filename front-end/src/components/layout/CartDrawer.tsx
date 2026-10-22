import { useNavigate } from 'react-router-dom';
import { Minus, Plus, Trash2, X } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { ProductImage } from '@/components/common/ProductImage';
import { useShop } from '@/context/ShopContext';
import { formatPrice } from '@/lib/format';

/** Màn 07 · Giỏ hàng (drawer phải 448px, overlay đen 50%). */
export function CartDrawer() {
  const { isCartOpen, closeCart, cartItems, cartTotal, updateQuantity, removeFromCart } = useShop();
  const navigate = useNavigate();

  const checkout = () => {
    closeCart();
    navigate('/checkout');
  };

  return (
    <>
      <div
        onClick={closeCart}
        className={cn('fixed inset-0 z-50 bg-black/50 transition-opacity', isCartOpen ? 'opacity-100' : 'pointer-events-none opacity-0')}
      />
      <aside
        aria-hidden={!isCartOpen}
        className={cn(
          'fixed right-0 top-0 z-50 flex h-full w-full max-w-[448px] flex-col bg-card shadow-xl transition-transform duration-300',
          isCartOpen ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        <div className="flex items-center justify-between border-b border-border p-5">
          <h2 className="text-xl font-bold">Giỏ hàng ({cartItems.length})</h2>
          <button onClick={closeCart} className="rounded-lg p-2 hover:bg-canvas" aria-label="Đóng giỏ hàng">
            <X className="size-5" />
          </button>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto p-5">
          {cartItems.length === 0 ? (
            <EmptyState {...EMPTY.cart} />
          ) : (
            cartItems.map((item) => (
              <div key={item.id} className="flex gap-3 rounded-[10px] bg-muted p-3">
                <ProductImage src={item.image} alt={item.name} className="size-20 shrink-0 rounded-lg" iconSize={24} />
                <div className="flex min-w-0 flex-1 flex-col">
                  <p className="line-clamp-2 text-sm font-semibold">{item.name}</p>
                  <p className="mt-1 font-bold text-primary">{formatPrice(item.price)}</p>
                  <div className="mt-auto flex items-center gap-1">
                    <button onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))} className="rounded-md border border-border-strong bg-card p-1 hover:bg-canvas" aria-label="Giảm">
                      <Minus className="size-3.5" />
                    </button>
                    <span className="w-8 text-center text-sm font-semibold">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="rounded-md border border-border-strong bg-card p-1 hover:bg-canvas" aria-label="Tăng">
                      <Plus className="size-3.5" />
                    </button>
                    <button onClick={() => removeFromCart(item.id)} className="ml-auto rounded-md p-1.5 text-danger hover:bg-danger-soft" aria-label="Xóa">
                      <Trash2 className="size-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {cartItems.length > 0 && (
          <div className="space-y-3 border-t border-border p-5">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Tạm tính</span>
              <span className="font-semibold">{formatPrice(cartTotal)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Phí vận chuyển</span>
              <span className="font-semibold text-success">Miễn phí</span>
            </div>
            <div className="flex justify-between border-t border-border pt-3 text-xl font-bold">
              <span>Tổng cộng</span>
              <span className="text-primary">{formatPrice(cartTotal)}</span>
            </div>
            <Button size="lg" className="w-full" onClick={checkout}>Thanh toán</Button>
          </div>
        )}
      </aside>
    </>
  );
}
