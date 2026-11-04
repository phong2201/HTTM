import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Clock, Sparkles, Star, Truck, UserCheck, Zap } from 'lucide-react';
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
  const hasBestSellerApi = Boolean(bestSellers?.length);
  const bestSellerList = hasBestSellerApi ? bestSellers! : newest.slice(0, 5);
  const coldStart = recommended !== null && recommended.length === 0;

  const categoryCover = (group: string) => products.find((p) => p.indexGroup?.toLowerCase() === group.toLowerCase())?.image;

  return (
    <div className="space-y-12 pb-8">
      {/* 1 · Hero sống động */}
      <section
        className="relative min-h-[410px] overflow-hidden py-12"
        style={{ background: 'linear-gradient(105deg, #E8112D 0%, #FF4B2B 55%, #FF7A3D 100%)' }}
      >
        <div className="pointer-events-none absolute -right-20 -top-24 size-[420px] rounded-full bg-white opacity-[0.14] animate-float-slow" />
        <div className="pointer-events-none absolute -bottom-32 right-40 size-[300px] rounded-full bg-white opacity-[0.12] animate-float-slow" />
        <div className="pointer-events-none absolute right-16 top-1/2 hidden h-64 w-64 -translate-y-1/2 rounded-3xl border border-white/25 bg-white/10 p-5 text-white backdrop-blur-md lg:flex lg:flex-col lg:justify-between">
          <div className="flex items-center justify-between">
            <span className="inline-flex items-center gap-1 rounded-full bg-white/20 px-2.5 py-1 text-xs font-bold">
              <Sparkles className="size-3.5" /> AI Ranker
            </span>
            <span className="text-xs font-semibold text-white/80">Top-12</span>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wider text-white/75">Thuật toán lõi</p>
            <p className="mt-1 text-xl font-black leading-snug">Random Forest + Session Rerank</p>
            <p className="mt-2 text-xs text-white/85">31,8M giao dịch H&amp;M · 32 đặc trưng hành vi</p>
          </div>
          <div className="flex items-center justify-between border-t border-white/20 pt-3 text-xs font-semibold">
            <span>MAP@12: 0.0310</span>
            <span className="rounded bg-white/20 px-1.5 py-0.5">+20.7% vs BL</span>
          </div>
        </div>

        <Container className="relative flex h-full items-center">
          <div className="max-w-xl text-white">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/15 px-3.5 py-1 text-xs font-bold tracking-wide backdrop-blur-xs">
              <Sparkles className="size-3.5" />
              <span>CÁ NHÂN HÓA THỜI GIAN THỰC · H&amp;M DATASET</span>
            </div>
            <h1 className="text-4xl font-black leading-tight tracking-tight md:text-[52px]">
              Thời trang gợi ý cho bạn
            </h1>
            <p className="mb-8 mt-4 text-lg leading-relaxed text-white/90">
              Khám phá sản phẩm được chọn riêng từ lịch sử mua sắm và tương tác tức thời của bạn
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="white" size="lg" asChild className="shadow-lg transition-transform hover:-translate-y-0.5">
                <Link to="/products">
                  Khám phá ngay <ArrowRight className="size-4" />
                </Link>
              </Button>
            </div>
          </div>
        </Container>
      </section>

      {/* 2 · Tính năng */}
      <Container>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, description }) => (
            <div
              key={title}
              className="group flex items-center gap-3.5 rounded-xl border border-border/80 bg-card p-5 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md"
            >
              <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-accent text-primary transition-colors duration-200 group-hover:bg-primary group-hover:text-white">
                <Icon className="size-6" />
              </span>
              <div>
                <h3 className="font-bold tracking-tight">{title}</h3>
                <p className="mt-0.5 text-[13px] text-muted-foreground">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </Container>

      {/* 3 · Danh mục nổi bật */}
      <Container>
        <SectionHeader title="Danh mục nổi bật" viewAllTo="/products" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-5">
          {INDEX_GROUPS.map((group) => (
            <Link
              key={group}
              to={`/products?index_group=${encodeURIComponent(group)}`}
              className="group relative overflow-hidden rounded-xl border border-border/80 bg-card shadow-card transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="relative aspect-square w-full overflow-hidden">
                <ProductImage
                  src={categoryCover(group)}
                  alt={group}
                  className="size-full transition-transform duration-300 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/15 to-transparent" />
                <div className="absolute inset-x-3 bottom-3 flex items-center justify-between text-white">
                  <p className="font-bold tracking-tight drop-shadow-xs">{group}</p>
                  <span className="flex size-7 items-center justify-center rounded-full bg-white/20 backdrop-blur-xs transition-transform group-hover:translate-x-0.5 group-hover:bg-primary">
                    <ArrowRight className="size-3.5" />
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </Container>

      {/* 4 · Bán chạy tuần này */}
      <section className="border-y border-border/60 bg-accent/75 py-12">
        <Container>
          <SectionHeader
            title="Bán chạy tuần này"
            icon={Zap}
            viewAllTo="/products"
            description={bestSellers && !hasBestSellerApi ? 'Chưa có dữ liệu bán chạy tuần — đang hiển thị sản phẩm mới nhất' : 'Top sản phẩm được đặt mua nhiều nhất trong 7 ngày qua'}
          />
          <HomeGrid products={bestSellerList} loading={productsLoading || bestSellers === null} columns={5} />
        </Container>
      </section>

      {/* 5 · Gợi ý dành cho bạn */}
      <section className="py-12" style={{ background: 'linear-gradient(105deg, #FFE8EC 0%, #FFF5EB 100%)' }}>
        <Container>
          <SectionHeader
            title="Gợi ý dành cho bạn"
            icon={Sparkles}
            description={coldStart ? EMPTY.coldStart.description : 'Dựa trên sở thích, lịch sử mua hàng và tương tác phiên của bạn · Random Forest xếp hạng'}
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
        <SectionHeader title="Sản phẩm mới" viewAllTo="/products?sort=newest" description="Cập nhật mới nhất trong danh mục H&M" />
        <HomeGrid products={newest} loading={productsLoading} columns={4} />
      </Container>
    </div>
  );
}

function HomeGrid({ products, loading, columns }: { products: Product[]; loading: boolean; columns: 4 | 5 }) {
  if (loading) {
    return (
      <ProductGrid columns={columns}>
        {Array.from({ length: columns }).map((_, idx) => (
          <div key={idx} className="overflow-hidden rounded-xl border border-border/70 bg-card p-3 shadow-card">
            <div className="aspect-square w-full rounded-lg animate-shimmer" />
            <div className="mt-3 h-3 w-1/2 rounded animate-shimmer" />
            <div className="mt-2 h-4 w-5/6 rounded animate-shimmer" />
            <div className="mt-4 h-6 w-1/3 rounded animate-shimmer" />
            <div className="mt-3 h-9 w-full rounded-lg animate-shimmer" />
          </div>
        ))}
      </ProductGrid>
    );
  }
  if (products.length === 0) return <EmptyState {...EMPTY.products} />;
  return (
    <ProductGrid columns={columns}>
      {products.map((product) => <ProductCard key={product.id} product={product} />)}
    </ProductGrid>
  );
}
