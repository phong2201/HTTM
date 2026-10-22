import { useEffect, useState, type FormEvent } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Panel, PanelTitle } from '@/components/common/Page';
import { Field } from '@/components/common/Field';
import { ProductImage } from '@/components/common/ProductImage';
import { apiService, CATALOG_LIMIT, type BackendProduct } from '@/services/api';
import { errorMessage, formatNumber, formatPrice, MISSING } from '@/lib/format';
import { TabToolbar, tableBody, tableHead, type AdminTabProps } from './shared';

/** Các ô của form — đúng tên cột articles.csv của H&M. */
const FORM_FIELDS = [
  { field: 'article_id', label: 'article_id', placeholder: 'vd 0108775015' },
  { field: 'prod_name', label: 'prod_name', required: true },
  { field: 'product_type_name', label: 'product_type_name' },
  { field: 'product_group_name', label: 'product_group_name' },
  { field: 'colour_group_name', label: 'colour_group_name' },
  { field: 'index_group_name', label: 'index_group_name' },
  { field: 'price', label: 'price (VND)', required: true, type: 'number' },
  { field: 'image_url', label: 'image_url' },
] as const;

type FormState = Record<(typeof FORM_FIELDS)[number]['field'], string> & { id: string };

const EMPTY_FORM: FormState = {
  id: '', article_id: '', prod_name: '', product_type_name: '', product_group_name: '',
  colour_group_name: '', index_group_name: '', price: '', image_url: '',
};

/** Màn 12 · Admin · Sản phẩm. */
export function ProductsTab({ reloadKey, tabBar, onSuccess, onError }: AdminTabProps) {
  const [products, setProducts] = useState<BackendProduct[]>([]);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiService.getProducts(0, CATALOG_LIMIT).then(setProducts).catch((err) => onError(errorMessage(err, 'Không tải được sản phẩm')));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reloadKey]);

  const edit = (p: BackendProduct) => setForm({
    id: p.id,
    article_id: p.article_id ?? '',
    prod_name: p.prod_name ?? '',
    product_type_name: p.product_type_name ?? '',
    product_group_name: p.product_group_name ?? '',
    colour_group_name: p.colour_group_name ?? '',
    index_group_name: p.index_group_name ?? '',
    price: String(p.price ?? ''),
    image_url: p.image_url ?? '',
  });

  const save = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    const articleId = form.article_id.trim();
    const payload: Partial<BackendProduct> = {
      article_id: articleId || null,
      product_code: articleId ? articleId.slice(0, 7) : null,
      prod_name: form.prod_name,
      product_type_name: form.product_type_name || null,
      product_group_name: form.product_group_name || null,
      colour_group_name: form.colour_group_name || null,
      index_group_name: form.index_group_name || null,
      price: Number(form.price),
      image_url: form.image_url || null,
      is_active: true,
    };
    try {
      const saved = form.id ? await apiService.updateProduct(form.id, payload) : await apiService.createProduct(payload);
      setProducts((prev) => (form.id ? prev.map((p) => (p.id === saved.id ? saved : p)) : [saved, ...prev]));
      onSuccess(form.id ? 'Đã cập nhật sản phẩm' : 'Đã tạo sản phẩm');
      setForm(EMPTY_FORM);
    } catch (err) {
      onError(errorMessage(err, 'Không lưu được sản phẩm'));
    } finally {
      setSaving(false);
    }
  };

  const remove = async (p: BackendProduct) => {
    if (!confirm(`Xóa sản phẩm ${p.prod_name}?`)) return;
    try {
      await apiService.deleteProduct(p.id);
      setProducts((prev) => prev.filter((item) => item.id !== p.id));
      onSuccess('Đã xóa sản phẩm');
    } catch (err) {
      onError(errorMessage(err, 'Không xóa được sản phẩm'));
    }
  };

  return (
    <>
      <TabToolbar tabBar={tabBar} />
      <div className="grid items-start gap-6 lg:grid-cols-[360px_1fr]">
        <Panel>
          <PanelTitle>{form.id ? 'Sửa sản phẩm' : 'Thêm sản phẩm'}</PanelTitle>
          <form onSubmit={save} className="space-y-3">
            {FORM_FIELDS.map((f) => (
              <Field key={f.field} label={f.label} htmlFor={f.field}>
                <Input
                  id={f.field}
                  type={'type' in f ? f.type : 'text'}
                  step="1000"
                  placeholder={'placeholder' in f ? f.placeholder : undefined}
                  required={'required' in f && f.required}
                  value={form[f.field]}
                  onChange={(e) => setForm((prev) => ({ ...prev, [f.field]: e.target.value }))}
                />
              </Field>
            ))}
            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={saving}>{saving ? 'Đang lưu...' : 'Lưu'}</Button>
              <Button type="button" variant="outline" onClick={() => setForm(EMPTY_FORM)}>Reset</Button>
            </div>
          </form>
        </Panel>

        <div className="max-h-[720px] overflow-auto rounded-[10px] bg-card shadow-card">
          <table className="w-full text-sm">
            <thead className={`${tableHead} sticky top-0`}>
              <tr><th>Tên</th><th>Loại</th><th>Giá</th><th>Bán tuần</th><th>Danh mục</th><th className="w-40">Action</th></tr>
            </thead>
            <tbody className={tableBody}>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="flex max-w-[300px] items-center gap-3">
                      <ProductImage src={p.image_url} alt={p.prod_name} className="size-9 shrink-0 rounded-md" iconSize={14} />
                      <div className="min-w-0">
                        <p className="truncate font-semibold">{p.prod_name}</p>
                        <p className="font-mono text-[11px] text-muted-foreground">{p.article_id ?? MISSING}</p>
                      </div>
                    </div>
                  </td>
                  <td>{p.product_type_name || MISSING}</td>
                  <td className="whitespace-nowrap font-semibold text-primary">{formatPrice(p.price)}</td>
                  <td className="tabular-nums">{formatNumber(p.sales_last_week)}</td>
                  <td>{p.index_group_name || MISSING}</td>
                  <td>
                    <div className="flex gap-1">
                      <Button variant="outline" size="sm" onClick={() => edit(p)}>Sửa</Button>
                      <Button variant="ghost" size="sm" className="text-danger hover:bg-danger-soft hover:text-danger" onClick={() => remove(p)}>Xóa</Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
