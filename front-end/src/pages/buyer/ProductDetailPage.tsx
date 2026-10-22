import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Heart, MessageSquare, ShoppingCart } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';
import { Container, Panel, PanelTitle } from '@/components/common/Page';
import { NativeSelect } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { ProductImage } from '@/components/common/ProductImage';
import { Stars } from '@/components/common/Stars';
import { useAuth } from '@/context/AuthContext';
import { useShop } from '@/context/ShopContext';
import { apiService, type FeedbackResponse } from '@/services/api';
import { toProduct, type Product } from '@/lib/product';
import { errorMessage, formatDateTime, formatPrice, MISSING, PRICE_NOTE } from '@/lib/format';

/** Màn 05 · Chi tiết sản phẩm. */
export function ProductDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const { addToCart, isWishlisted, toggleWishlist } = useShop();
  const [product, setProduct] = useState<Product | null>(null);
  const [feedbacks, setFeedbacks] = useState<FeedbackResponse[]>([]);
  const [rank, setRank] = useState(5);
  const [notice, setNotice] = useState<{ tone: 'success' | 'destructive'; text: string } | null>(null);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    if (!id) return;
    setProduct(null);
    setLoadError('');
    apiService.getProductById(id).then((p) => setProduct(toProduct(p))).catch((err) => setLoadError(errorMessage(err, 'Không tải được sản phẩm')));
    apiService.getFeedbacksByProduct(id).then(setFeedbacks).catch(() => setFeedbacks([]));
  }, [id]);

  if (loadError) return <Container className="py-8"><Notice tone="destructive">Không kết nối được API sản phẩm: {loadError}</Notice></Container>;
  if (!product) return <Container className="py-8 text-muted-foreground">Đang tải sản phẩm...</Container>;

  const liked = isWishlisted(product.id);
  const avgRating = feedbacks.length ? feedbacks.reduce((sum, f) => sum + f.rank, 0) / feedbacks.length : null;

  const handleWishlist = async () => {
    const nowLiked = await toggleWishlist(product);
    setNotice({ tone: 'success', text: nowLiked ? 'Đã thêm vào Wishlist' : 'Đã bỏ khỏi Wishlist' });
  };

  const submitFeedback = async () => {
    if (!user?.id) return setNotice({ tone: 'destructive', text: 'Cần đăng nhập để đánh giá sản phẩm' });
    try {
      const saved = await apiService.createFeedback(user.id, product.id, rank);
      setFeedbacks((prev) => [saved, ...prev.filter((f) => f.user_id !== user.id)]);
      setNotice({ tone: 'success', text: 'Đã lưu đánh giá' });
    } catch (err) {
      setNotice({ tone: 'destructive', text: errorMessage(err, 'Không gửi được đánh giá') });
    }
  };

  const info = [
    { label: 'Màu', value: product.colour },
    { label: 'Loại', value: product.productType },
    { label: 'Nhóm', value: product.productGroup },
    { label: 'Họa tiết', value: product.pattern },
  ];

  return (
    <Container className="py-8">
      <div className="grid gap-10 lg:grid-cols-[592px_1fr]">
        <div className="rounded-[10px] bg-card p-4 shadow-card">
          <ProductImage src={product.image} alt={product.name} className="aspect-square w-full rounded-lg" iconSize={64} />
        </div>

        <div className="space-y-5">
          <p className="text-sm text-muted-foreground">{product.indexGroup || MISSING} / {product.productType}</p>
          <h1 className="text-[34px] font-black leading-tight tracking-tight">{product.name}</h1>
          <div className="flex items-center gap-2">
            <Stars value={avgRating} size={18} />
            <span className="text-sm text-muted-foreground">{avgRating?.toFixed(1) ?? MISSING} ({feedbacks.length} đánh giá)</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-[34px] font-black text-primary">{formatPrice(product.price)}</span>
            <span className="text-sm text-muted-foreground" title={PRICE_NOTE}>giá quy đổi ước lượng</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {info.map(({ label, value }) => (
              <div key={label} className="rounded-lg border border-border bg-card px-4 py-3">
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="font-semibold">{value || MISSING}</p>
              </div>
            ))}
          </div>
          <p className="leading-7 text-foreground/80">{product.description || 'Chưa có mô tả.'}</p>
          <div className="flex flex-wrap gap-3">
            <Button size="lg" onClick={() => addToCart(product)}><ShoppingCart /> Thêm vào giỏ</Button>
            <Button size="lg" variant="outlineRed" onClick={handleWishlist} className={cn(liked && 'bg-accent')}>
              <Heart className={cn(liked && 'fill-primary')} /> Yêu thích
            </Button>
          </div>
          {notice && <Notice tone={notice.tone}>{notice.text}</Notice>}
        </div>
      </div>

      <Panel className="mt-10">
        <PanelTitle icon={MessageSquare}>Đánh giá sản phẩm</PanelTitle>
        <div className="mb-6 flex flex-wrap items-center gap-3">
          <NativeSelect value={rank} onChange={(e) => setRank(Number(e.target.value))} className="w-32">
            {[5, 4, 3, 2, 1].map((value) => <option key={value} value={value}>{value} sao</option>)}
          </NativeSelect>
          <Button onClick={submitFeedback}>Gửi đánh giá</Button>
        </div>
        {feedbacks.length === 0 ? (
          <p className="text-sm text-muted-foreground">Chưa có đánh giá.</p>
        ) : (
          <div className="divide-y divide-border">
            {feedbacks.map((f) => (
              <div key={f.id} className="flex items-start justify-between gap-4 py-3">
                <div>
                  <Stars value={f.rank} />
                  <p className="mt-1 text-sm text-muted-foreground">User: {f.user_id}</p>
                </div>
                <span className="shrink-0 text-xs text-faint">{formatDateTime(f.updated_at || f.created_at)}</span>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </Container>
  );
}
