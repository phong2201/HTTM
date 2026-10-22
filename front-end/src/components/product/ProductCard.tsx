import { Link } from 'react-router-dom';
import { Eye, Heart, ShoppingCart } from 'lucide-react';
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
    <article className="group flex flex-col overflow-hidden rounded-[10px] bg-card shadow-card transition-shadow hover:shadow-md">
      <Link to={detailUrl} className="relative block aspect-square overflow-hidden">
        <ProductImage src={product.image} alt={product.name} className="size-full transition-transform duration-300 group-hover:scale-105" />
        {rank && (
          <span className="absolute left-2 top-2 rounded-full bg-primary px-2.5 py-1 text-xs font-bold text-white">
            #{rank.rank} · {rank.score.toFixed(3)}
          </span>
        )}
        {liked && <Heart className="absolute right-2 top-2 size-5 fill-primary text-primary drop-shadow" />}
      </Link>

      <div className="flex flex-1 flex-col p-4">
        <p className="mb-1 truncate text-xs text-muted-foreground">{product.productType}</p>
        <Link to={detailUrl} className="mb-2 line-clamp-2 min-h-[42px] text-[15px] font-semibold leading-snug hover:text-primary">
          {product.name}
        </Link>
        <div className="mb-2 flex items-center gap-1.5">
          <Stars value={product.rating} />
          <span className="text-xs text-muted-foreground">({product.reviews ?? MISSING})</span>
        </div>
        <p className="mb-3 text-lg font-bold text-primary">{formatPrice(product.price)}</p>

        <div className="mt-auto flex gap-2">
          <Button className="flex-1" onClick={() => addToCart(product)}>
            <ShoppingCart /> Giỏ
          </Button>
          <Button variant="outline" size="icon" asChild title="Xem chi tiết">
            <Link to={detailUrl}><Eye /></Link>
          </Button>
          <Button
            variant="outlineRed"
            size="icon"
            title={liked ? 'Bỏ yêu thích' : 'Yêu thích'}
            onClick={handleWishlist}
            className={cn(liked && 'border-accent bg-accent')}
          >
            <Heart className={cn(liked && 'fill-primary')} />
          </Button>
        </div>
      </div>
    </article>
  );
}
