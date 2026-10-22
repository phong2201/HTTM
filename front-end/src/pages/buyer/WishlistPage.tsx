import { useEffect, useState } from 'react';
import { Container, PageHeader } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { Notice } from '@/components/common/Notice';
import { ProductCard } from '@/components/product/ProductCard';
import { ProductGrid } from '@/components/product/ProductGrid';
import { apiService } from '@/services/api';
import { toProduct, type Product } from '@/lib/product';
import { errorMessage } from '@/lib/format';

/** Màn 06 · Wishlist. Bấm ♥ lần nữa → removeWishlistItem và gỡ thẻ. */
export function WishlistPage() {
  const [items, setItems] = useState<Product[] | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.getWishlist()
      .then((data) => setItems(data.flatMap((item) => (item.product ? [toProduct(item.product)] : []))))
      .catch((err) => { setItems([]); setError(errorMessage(err, 'Không tải được wishlist')); });
  }, []);

  const removeLocal = (product: Product) => setItems((prev) => prev?.filter((item) => item.id !== product.id) ?? null);

  return (
    <Container className="py-8">
      <PageHeader title="Wishlist" description="Các sản phẩm bạn đã đánh dấu yêu thích" />
      {error && <Notice tone="destructive" className="mb-4">{error}</Notice>}
      {items === null ? (
        <p className="text-sm text-muted-foreground">Đang tải...</p>
      ) : items.length === 0 ? (
        <EmptyState {...EMPTY.wishlist} />
      ) : (
        <ProductGrid>
          {items.map((product) => <ProductCard key={product.id} product={product} onUnliked={removeLocal} />)}
        </ProductGrid>
      )}
    </Container>
  );
}
