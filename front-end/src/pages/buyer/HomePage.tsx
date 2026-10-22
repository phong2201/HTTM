import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Clock, Sparkles, Star, Truck, UserCheck, Zap } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Container, SectionHeader } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { ProductImage } from '@/components/common/ProductImage';
import { ProductCard } from '@/components/product/ProductCard';
import { ProductGrid } from '@/components/product/ProductGrid';
import { useAuth } from '@/context/AuthContext';
import { useShop } from '@/context/ShopContext';
import { apiService, type BackendProduct } from '@/services/api';
import { INDEX_GROUPS, toProduct, type Product, type RankedProduct } from '@/lib/product';

const FEATURES = [
  { icon: Truck, title: 'Giao hàng nhanh', description: 'Miễn phí vận chuyển mọi đơn' },
  { icon: Star, title: 'Sản phẩm chọn lọc', description: 'Danh mục từ dữ liệu H&M' },
  { icon: Clock, title: 'Cập nhật mỗi ngày', description: 'Gợi ý được tính lại lúc 02:00' },
  { icon: UserCheck, title: 'Gợi ý cá nhân', description: 'Random Forest xếp hạng theo lịch sử mua' },
];

const RECOMMENDATION_COUNT = 5;

/** Màn 03 · Trang chủ. */
export function HomePage() {
  const { user } = useAuth();
  const { products, productsLoading } = useShop();
  const [bestSellers, setBestSellers] = useState<Product[] | null>(null);
  const [recommended, setRecommended] = useState<RankedProduct[] | null>(null);

  useEffect(() => {
    apiService.getBestSellers(5)
      .then((items) => setBestSellers(items.map(toProduct)))
      .catch(() => setBestSellers([]));
  }, []);

  useEffect(() => {
    if (!user?.id) return;
    apiService.getRecommendations(user.id, RECOMMENDATION_COUNT)
      .then((items) => setRecommended(items
        .filter((item): item is typeof item & { product_details: BackendProduct } => Boolean(item.product_details))
        .map((item) => ({ ...toProduct(item.product_details), rank: item.rank, score: item.score }))))
      .catch(() => setRecommended([]));
  }, [user?.id]);

  const newest = useMemo(
    () => [...products].sort((a, b) => (b.createdAt ?? '').localeCompare(a.createdAt ?? '')).slice(0, 4),
    [products],
  );
  // TODO(backend): khi có /products/best-sellers thì phần dự phòng này không còn dùng.
  const hasBestSellerApi = Boolean(bestSellers?.length);
  const bestSellerList = hasBestSellerApi ? bestSellers! : newest.slice(0, 5);
  const coldStart = recommended !== null && recommended.length === 0;

  const categoryCover = (group: string) => products.find((p) => p.indexGroup?.toLowerCase() === group.toLowerCase())?.image;

  return (
    <div className="space-y-12">
      {/* 1 · Hero */}
      <section className="relative h-[400px] overflow-hidden" style={{ background: 'linear-gradient(90deg, #E8112D, #FF7A3D)' }}>
        <div className="absolute -right-20 -top-24 size-[420px] rounded-full bg-white opacity-[0.14]" />
        <div className="absolute -bottom-32 right-40 size-[300px] rounded-full bg-white opacity-[0.12]" />
        <Container className="relative flex h-full items-center">
          <div className="max-w-xl text-white">
            <h1 className="text-4xl font-black leading-tight tracking-tight md:text-[52px]">Thời trang gợi ý cho bạn</h1>
            <p className="mb-7 mt-4 text-lg text-white/90">Khám phá sản phẩm được chọn riêng từ lịch sử mua sắm của bạn</p>
            <Button variant="white" size="lg" asChild>
              <Link to="/products">Khám phá ngay</Link>
            </Button>
          </div>
        </Container>
      </section>

      {/* 2 · Tính năng */}
      <Container>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div key={title} className="flex items-center gap-3 rounded-[10px] bg-card p-5 shadow-card">
              <Icon className="size-9 shrink-0 text-primary" />
              <div>
                <h3 className="font-bold">{title}</h3>
                <p className="text-[13px] text-muted-foreground">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </Container>

      {/* 3 · Danh mục nổi bật */}
      <Container>
        <SectionHeader title="Danh mục nổi bật" viewAllTo="/products" />
        <div className="grid grid-cols-3 gap-4 md:grid-cols-5">
          {INDEX_GROUPS.map((group) => (
            <Link key={group} to={`/products?index_group=${encodeURIComponent(group)}`} className="group">
              <ProductImage src={categoryCover(group)} alt={group} className="mb-2 aspect-square w-full rounded-[10px] transition-transform group-hover:scale-[1.03]" />
              <p className="text-center font-semibold group-hover:text-primary">{group}</p>
            </Link>
          ))}
        </div>
      </Container>

      {/* 4 · Bán chạy tuần này */}
      <section className="bg-accent py-10">
        <Container>
          <SectionHeader
            title="Bán chạy tuần này"
            icon={Zap}
            viewAllTo="/products"
            description={bestSellers && !hasBestSellerApi ? 'Chưa có dữ liệu bán chạy tuần — đang hiển thị sản phẩm mới nhất' : undefined}
          />
          <HomeGrid products={bestSellerList} loading={productsLoading || bestSellers === null} columns={5} />
        </Container>
      </section>

      {/* 5 · Gợi ý dành cho bạn */}
      <section className="py-10" style={{ background: 'linear-gradient(90deg, #FFE8EC, #FFF5EB)' }}>
        <Container>
          <SectionHeader
            title="Gợi ý dành cho bạn"
            icon={Sparkles}
            description={coldStart ? EMPTY.coldStart.description : 'Dựa trên sở thích và lịch sử mua hàng của bạn · Random Forest xếp hạng'}
          />
          {coldStart ? (
            <HomeGrid products={bestSellerList} loading={productsLoading} columns={5} />
          ) : (
            <ProductGrid columns={5}>
              {(recommended ?? []).map((product) => (
                <ProductCard key={product.id} product={product} rank={{ rank: product.rank, score: product.score }} />
              ))}
            </ProductGrid>
          )}
        </Container>
      </section>

      {/* 6 · Sản phẩm mới */}
      <Container>
        <SectionHeader title="Sản phẩm mới" viewAllTo="/products?sort=newest" />
        <HomeGrid products={newest} loading={productsLoading} columns={4} />
      </Container>
    </div>
  );
}

function HomeGrid({ products, loading, columns }: { products: Product[]; loading: boolean; columns: 4 | 5 }) {
  if (loading) return <p className="text-sm text-muted-foreground">Đang tải sản phẩm...</p>;
  if (products.length === 0) return <EmptyState {...EMPTY.products} />;
  return (
    <ProductGrid columns={columns}>
      {products.map((product) => <ProductCard key={product.id} product={product} />)}
    </ProductGrid>
  );
}
