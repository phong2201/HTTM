import type { BackendProduct } from '@/services/api';

/** Sản phẩm dùng trên giao diện — đặt tên theo cột H&M. */
export interface Product {
  id: string;
  name: string;
  price: number;
  image?: string | null;
  rating?: number | null;
  reviews?: number | null;
  productType: string;
  productGroup?: string | null;
  colour?: string | null;
  pattern?: string | null;
  indexGroup?: string | null;
  description?: string | null;
  salesLastWeek?: number | null;
  createdAt?: string;
}

export interface CartItem extends Product {
  quantity: number;
}

/** Sản phẩm trong khối gợi ý: kèm rank & score từ bảng Recommendations. */
export interface RankedProduct extends Product {
  rank: number;
  score: number;
}

/** 5 nhóm index_group_name của H&M. */
export const INDEX_GROUPS = ['Ladieswear', 'Menswear', 'Baby/Children', 'Sport', 'Divided'] as const;

export function toProduct(p: BackendProduct): Product {
  return {
    id: p.id,
    name: p.prod_name,
    price: Number(p.price ?? 0),
    image: p.image_url,
    rating: null,
    reviews: null,
    productType: p.product_type_name || 'Sản phẩm',
    productGroup: p.product_group_name,
    colour: p.colour_group_name,
    pattern: p.graphical_appearance_name,
    indexGroup: p.index_group_name,
    description: p.detail_desc,
    salesLastWeek: p.sales_last_week ?? null,
    createdAt: p.created_at,
  };
}

export function uniqueValues(products: Product[], pick: (p: Product) => string | null | undefined): string[] {
  return Array.from(new Set(products.map(pick).filter((v): v is string => Boolean(v)))).sort();
}
