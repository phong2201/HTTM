import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Search, X } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';
import { Container, PageHeader } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';
import { NativeSelect, controlClass } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { ProductCard } from '@/components/product/ProductCard';
import { ProductGrid } from '@/components/product/ProductGrid';
import { useShop } from '@/context/ShopContext';
import { apiService } from '@/services/api';
import { INDEX_GROUPS, toProduct, uniqueValues, type Product } from '@/lib/product';
import { errorMessage } from '@/lib/format';

const PAGE_SIZE = 20;

const SORTS = {
  bestseller: 'Bán chạy tuần',
  price_asc: 'Giá tăng',
  price_desc: 'Giá giảm',
  newest: 'Mới nhất',
} as const;
type SortKey = keyof typeof SORTS;

const FILTERS = [
  { key: 'index_group', label: 'Danh mục' },
  { key: 'product_group', label: 'Nhóm sản phẩm' },
  { key: 'colour', label: 'Màu sắc' },
] as const;
type FilterKey = 'q' | (typeof FILTERS)[number]['key'];

function sortProducts(items: Product[], sort: SortKey): Product[] {
  const sorted = [...items];
  if (sort === 'price_asc') sorted.sort((a, b) => a.price - b.price);
  if (sort === 'price_desc') sorted.sort((a, b) => b.price - a.price);
  if (sort === 'newest') sorted.sort((a, b) => (b.createdAt ?? '').localeCompare(a.createdAt ?? ''));
  if (sort === 'bestseller') sorted.sort((a, b) => (b.salesLastWeek ?? 0) - (a.salesLastWeek ?? 0));
  return sorted;
}

/** Màn 04 · Sản phẩm (tìm kiếm & lọc). */
export function ProductsPage() {
  const [params, setParams] = useSearchParams();
  const { products: catalog } = useShop();
  const [results, setResults] = useState<Product[] | null>(null);
  const [error, setError] = useState('');

  const applied = {
    q: params.get('q') ?? '',
    index_group: params.get('index_group') ?? '',
    product_group: params.get('product_group') ?? '',
    colour: params.get('colour') ?? '',
  };
  const sort = (params.get('sort') as SortKey) in SORTS ? (params.get('sort') as SortKey) : 'bestseller';
  const page = Math.max(1, Number(params.get('page')) || 1);
  const [draft, setDraft] = useState(applied);
  const filterKey = [applied.q, applied.index_group, applied.product_group, applied.colour].join('|');

  useEffect(() => {
    setDraft(applied);
    setResults(null);
    apiService.searchProducts({ q: applied.q, index_group: applied.index_group, product_group: applied.product_group, colour: applied.colour })
      .then((items) => { setResults(items.map(toProduct)); setError(''); })
      .catch((err) => { setResults([]); setError(errorMessage(err, 'Không tải được sản phẩm')); });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterKey]);

  const options = useMemo(() => ({
    index_group: uniqueValues(catalog, (p) => p.indexGroup).concat(INDEX_GROUPS).filter((v, i, all) => all.indexOf(v) === i),
    product_group: uniqueValues(catalog, (p) => p.productGroup),
    colour: uniqueValues(catalog, (p) => p.colour),
  }), [catalog]);

  const sorted = useMemo(() => sortProducts(results ?? [], sort), [results, sort]);
  const pageCount = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const visible = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const update = (changes: Record<string, string>) => {
    const next = new URLSearchParams(params);
    Object.entries(changes).forEach(([key, value]) => (value ? next.set(key, value) : next.delete(key)));
    if (!('page' in changes)) next.delete('page');
    setParams(next);
  };

  const applyFilters = (event: FormEvent) => {
    event.preventDefault();
    update({ ...draft, sort: sort === 'bestseller' ? '' : sort });
  };

  const chips = (['q', ...FILTERS.map((f) => f.key)] as FilterKey[])
    .filter((key) => applied[key])
    .map((key) => ({ key, label: key === 'q' ? `“${applied.q}”` : applied[key] }));

  return (
    <Container className="py-8">
      <PageHeader title="Tất cả sản phẩm" description={`${results ? sorted.length : '—'} sản phẩm thời trang`} />

      <form onSubmit={applyFilters} className="mb-3 grid gap-3 rounded-[10px] bg-card p-4 shadow-card md:grid-cols-2 lg:grid-cols-[1.6fr_1fr_1fr_1fr_1fr_auto]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-faint" />
          <input value={draft.q} onChange={(e) => setDraft({ ...draft, q: e.target.value })} placeholder="Tìm kiếm" className={cn(controlClass, 'pl-9 placeholder:text-faint')} />
        </div>
        {FILTERS.map(({ key, label }) => (
          <NativeSelect key={key} aria-label={label} value={draft[key]} onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}>
            <option value="">{label}</option>
            {options[key].map((value) => <option key={value} value={value}>{value}</option>)}
          </NativeSelect>
        ))}
        <NativeSelect aria-label="Sắp xếp" value={sort} onChange={(e) => update({ sort: e.target.value === 'bestseller' ? '' : e.target.value })}>
          {Object.entries(SORTS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
        </NativeSelect>
        <Button type="submit">Lọc</Button>
      </form>

      {chips.length > 0 && (
        <div className="mb-5 flex flex-wrap gap-2">
          {chips.map(({ key, label }) => (
            <button key={key} onClick={() => update({ [key]: '' })} className="flex items-center gap-1 rounded-full bg-accent px-3 py-1 text-[13px] font-semibold text-primary hover:bg-accent/70">
              {label} <X className="size-3.5" />
            </button>
          ))}
        </div>
      )}

      {error && <Notice tone="destructive" className="mb-4">Không kết nối được API sản phẩm: {error}</Notice>}

      <div className="mt-5">
        {results === null ? (
          <p className="text-sm text-muted-foreground">Đang tải sản phẩm...</p>
        ) : visible.length === 0 ? (
          <EmptyState {...EMPTY.products} />
        ) : (
          <ProductGrid>{visible.map((product) => <ProductCard key={product.id} product={product} />)}</ProductGrid>
        )}
      </div>

      {pageCount > 1 && <Pagination page={page} pageCount={pageCount} onChange={(next) => update({ page: next > 1 ? String(next) : '' })} />}
    </Container>
  );
}

function Pagination({ page, pageCount, onChange }: { page: number; pageCount: number; onChange: (page: number) => void }) {
  const pages = Array.from({ length: pageCount }, (_, i) => i + 1)
    .filter((p) => p === 1 || p === pageCount || Math.abs(p - page) <= 1);

  return (
    <nav className="mt-8 flex items-center justify-center gap-1.5">
      <Button variant="outline" size="icon" disabled={page <= 1} onClick={() => onChange(page - 1)} aria-label="Trang trước"><ChevronLeft /></Button>
      {pages.map((p, i) => (
        <span key={p} className="flex items-center gap-1.5">
          {i > 0 && p - pages[i - 1] > 1 && <span className="px-1 text-muted-foreground">…</span>}
          <Button variant={p === page ? 'default' : 'outline'} size="icon" onClick={() => onChange(p)}>{p}</Button>
        </span>
      ))}
      <Button variant="outline" size="icon" disabled={page >= pageCount} onClick={() => onChange(page + 1)} aria-label="Trang sau"><ChevronRight /></Button>
    </nav>
  );
}
