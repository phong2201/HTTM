import { Link } from 'react-router-dom';
import { Eye, Heart, ShoppingCart, Sparkles } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';
import { ProductImage } from '@/components/common/ProductImage';
import { Stars } from '@/components/common/Stars';
import { useShop } from '@/context/ShopContext';
import { formatPrice, MISSING } from '@/lib/format';
import type { Product } from '@/lib/product';

interface ProductCardProps {
  product: Product;
  /** Badge điểm `#rank · score` — chỉ dùng ở khối gợi ý. */
  rank?: { rank: number; score: number };
  /** Gọi sau khi bỏ thích (vd: Wishlist gỡ thẻ khỏi danh sách). */
  onUnliked?: (product: Product) => void;
}

export function ProductCard({ product, rank, onUnliked }: ProductCardProps) {
  const { addToCart, isWishlisted, toggleWishlist } = useShop();
  const liked = isWishlisted(product.id);
  const detailUrl = `/products/${product.id}`;

  const handleWishlist = async () => {
    const nowLiked = await toggleWishlist(product);
    if (!nowLiked) onUnliked?.(product);
  };

  return (
    <article className="group flex flex-col overflow-hidden rounded-xl border border-border/80 bg-card shadow-card transition-all duration-200 hover:-translate-y-1 hover:border-primary/30 hover:shadow-lg">
      <Link to={detailUrl} className="relative block aspect-square overflow-hidden bg-img-ph">
        <ProductImage
          src={product.image}
          alt={product.name}
          className="size-full transition-transform duration-300 ease-out group-hover:scale-105"
        />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-black/25 to-transparent opacity-0 transition-opacity duration-200 group-hover:opacity-100" />
        {rank && (
          <span className="absolute left-2.5 top-2.5 inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-[#E8112D] to-[#FF7A3D] px-2.5 py-1 text-[11px] font-bold text-white shadow-md">
            <Sparkles className="size-3" />
            #{rank.rank} · {rank.score.toFixed(3)}
          </span>
        )}
        {product.indexGroup && !rank && (
          <span className="absolute left-2.5 top-2.5 rounded-full bg-white/90 px-2.5 py-0.5 text-[11px] font-semibold text-foreground/85 shadow-2xs backdrop-blur-xs">
            {product.indexGroup}
          </span>
        )}
        {liked && (
          <span className="absolute right-2.5 top-2.5 flex size-7 items-center justify-center rounded-full bg-white/90 shadow-xs backdrop-blur-xs">
            <Heart className="size-4 fill-primary text-primary" />
          </span>
        )}
      </Link>

      <div className="flex flex-1 flex-col p-4">
        <div className="mb-1 flex items-center justify-between gap-2">
          <p className="truncate text-xs font-medium text-muted-foreground">{product.productType}</p>
          {product.colour && (
            <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
              {product.colour}
            </span>
          )}
        </div>
        <Link
          to={detailUrl}
          className="mb-2 line-clamp-2 min-h-[42px] text-[15px] font-bold leading-snug tracking-tight transition-colors group-hover:text-primary"
        >
          {product.name}
        </Link>
        <div className="mb-2 flex items-center gap-1.5">
          <Stars value={product.rating} />
          <span className="text-xs text-muted-foreground">({product.reviews ?? MISSING})</span>
        </div>
        <p className="mb-3.5 text-lg font-black tracking-tight text-primary">{formatPrice(product.price)}</p>

        <div className="mt-auto flex gap-1.5">
          <Button className="flex-1 shadow-2xs transition-transform active:scale-[0.98]" onClick={() => addToCart(product)}>
            <ShoppingCart className="size-4" /> Giỏ
          </Button>
          <Button variant="outline" size="icon" asChild title="Xem chi tiết" className="hover:border-primary/40 hover:text-primary">
            <Link to={detailUrl} aria-label="Xem chi tiết"><Eye className="size-4" /></Link>
          </Button>
          <Button
            variant="outlineRed"
            size="icon"
            aria-label={liked ? 'Bỏ yêu thích' : 'Yêu thích'}
            title={liked ? 'Bỏ yêu thích' : 'Yêu thích'}
            onClick={handleWishlist}
            className={cn('transition-transform active:scale-95', liked && 'border-accent bg-accent')}
          >
            <Heart className={cn('size-4', liked && 'fill-primary')} />
          </Button>
        </div>
      </div>
    </article>
  );
}
