import { useEffect, useMemo, useState } from 'react';
import { Download, Filter, Layers, SearchX, SlidersHorizontal, Users } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { Bar, gradientAt } from '@/components/common/Gradient';
import { Notice } from '@/components/common/Notice';
import { tableBody, tableHead } from '@/components/common/table';
import { useShop } from '@/context/ShopContext';
import { apiService, type ErrorAnalysis } from '@/services/api';
import { uniqueValues } from '@/lib/product';
import { errorMessage, formatMetric, formatNumber, MISSING } from '@/lib/format';

const CUSTOMER_SEGMENTS = ['cold start', '1–2 giao dịch', '3–10 giao dịch', '>10 giao dịch'];
const CANDIDATE_SOURCES = ['Mua lại', 'Bán chạy tuần', 'Bán chạy theo tuổi', 'Cùng product_code', 'Co-purchase', 'Tất cả nguồn'];

function downloadCsv(filename: string, rows: Array<Array<string | number | null | undefined>>) {
  const escape = (v: string | number | null | undefined) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const blob = new Blob(['﻿' + rows.map((r) => r.map(escape).join(',')).join('\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = Object.assign(document.createElement('a'), { href: url, download: filename });
  a.click();
  URL.revokeObjectURL(url);
}

/** Màn 18 · Phân tích lỗi. */
export function ErrorAnalysisPage() {
  const { products } = useShop();
  const [data, setData] = useState<ErrorAnalysis | null>(null);
  const [error, setError] = useState('');
  const [topN, setTopN] = useState(12);
  const [recomputing, setRecomputing] = useState(false);

  useEffect(() => {
    apiService.getErrorAnalysis().then(setData).catch((err) => setError(errorMessage(err, 'Chưa có API phân tích lỗi')));
  }, []);

  // Thiếu dữ liệu → vẫn liệt kê đủ hàng, số để `—`.
  const customerRows = useMemo(
    () => CUSTOMER_SEGMENTS.map((segment) => data?.by_customer.find((r) => r.segment === segment) ?? { segment }),
    [data],
  );
  const productRows = useMemo(
    () => (data?.by_product_group.length ? data.by_product_group : uniqueValues(products, (p) => p.productGroup).map((product_group_name) => ({ product_group_name }))),
    [data, products],
  ) as ErrorAnalysis['by_product_group'];
  const sourceRows = CANDIDATE_SOURCES.map((source) => data?.candidate_recall.find((r) => r.source === source) ?? { source, recall: null });
  const features = [...(data?.feature_importance ?? [])].sort((a, b) => b.importance - a.importance).slice(0, 8);
  const maxImportance = Math.max(0, ...features.map((f) => f.importance));

  const exportCsv = () => downloadCsv('error-analysis.csv', [
    ['Theo nhóm khách'],
    ['segment', 'customers', 'map12', 'recall12'],
    ...customerRows.map((r) => [r.segment, r.customers, r.map12, r.recall12]),
    [],
    ['Theo nhóm sản phẩm'],
    ['product_group_name', 'purchases', 'precision12', 'recall12'],
    ...productRows.map((r) => [r.product_group_name, r.purchases, r.precision12, r.recall12]),
    [],
    ['Feature importance'],
    ['feature', 'importance'],
    ...features.map((f) => [f.feature, f.importance]),
    [],
    ['Ứng viên bị bỏ sót'],
    ['source', 'recall'],
    ...sourceRows.map((r) => [r.source, r.recall]),
  ]);

  const recompute = async () => {
    setRecomputing(true);
    try {
      const response = await apiService.recomputeRecommendations(topN);
      toast.success(response.message || `Đã tính lại với Top ${topN}`);
    } catch (err) {
      toast.error(errorMessage(err, 'Không tính lại được gợi ý'));
    } finally {
      setRecomputing(false);
    }
  };

  return (
    <Container className="py-8">
      <PageHeader
        icon={SearchX}
        title="Phân tích lỗi"
        description="Model sai ở đâu: theo nhóm khách, nhóm sản phẩm và nguồn ứng viên"
        actions={<Button variant="outline" onClick={exportCsv}><Download /> Xuất CSV</Button>}
      />
      {error && <Notice tone="warning" className="mb-5">Không lấy được dữ liệu phân tích: {error}. Các số hiển thị “{MISSING}”.</Notice>}

      <div className="mb-6 grid items-start gap-6 lg:grid-cols-2">
        <Panel>
          <PanelTitle icon={Users}>Theo nhóm khách</PanelTitle>
          <div className="-mx-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className={tableHead}><tr><th>Nhóm</th><th>Số khách</th><th>MAP@12</th><th>Recall@12</th></tr></thead>
              <tbody className={tableBody}>
                {customerRows.map((r) => (
                  <tr key={r.segment}>
                    <td className="font-semibold">{r.segment}</td>
                    <td className="tabular-nums">{formatNumber('customers' in r ? r.customers : null)}</td>
                    <td className="tabular-nums">{formatMetric('map12' in r ? r.map12 : null)}</td>
                    <td className="tabular-nums">{formatMetric('recall12' in r ? r.recall12 : null)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel>
          <PanelTitle icon={Layers}>Theo nhóm sản phẩm</PanelTitle>
          <div className="-mx-6 max-h-[320px] overflow-auto">
            <table className="w-full text-sm">
              <thead className={tableHead}><tr><th>product_group_name</th><th>Số món mua</th><th>Precision@12</th><th>Recall@12</th></tr></thead>
              <tbody className={tableBody}>
                {productRows.length === 0 ? (
                  <tr><td colSpan={4} className="text-muted-foreground">{MISSING}</td></tr>
                ) : productRows.map((r) => (
                  <tr key={r.product_group_name}>
                    <td className="font-semibold">{r.product_group_name}</td>
                    <td className="tabular-nums">{formatNumber(r.purchases)}</td>
                    <td className="tabular-nums">{formatMetric(r.precision12)}</td>
                    <td className="tabular-nums">{formatMetric(r.recall12)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-2">
        <Panel>
          <PanelTitle icon={SlidersHorizontal}>Feature importance (Random Forest)</PanelTitle>
          {features.length === 0 ? (
            <p className="text-sm text-muted-foreground">{MISSING} Chưa có feature importance từ lần huấn luyện.</p>
          ) : (
            <div className="space-y-3">
              {features.map((f, i) => (
                <div key={f.feature} className="grid grid-cols-[160px_1fr_56px] items-center gap-3 text-[13px]">
                  <span className="truncate font-mono text-xs">{f.feature}</span>
                  <Bar value={f.importance} max={maxImportance} background={gradientAt(i, '90deg')} />
                  <span className="text-right font-semibold tabular-nums">{f.importance.toFixed(3)}</span>
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel>
          <PanelTitle icon={Filter}>Ứng viên bị bỏ sót</PanelTitle>
          <p className="mb-4 text-[13px] text-muted-foreground">Recall của tập ứng viên theo nguồn sinh.</p>
          <div className="mb-6 space-y-3">
            {sourceRows.map((r, i) => (
              <div key={r.source} className="grid grid-cols-[140px_1fr_56px] items-center gap-3 text-[13px]">
                <span className="truncate">{r.source}</span>
                <Bar value={r.recall} background={gradientAt(i, '90deg')} />
                <span className="text-right font-semibold tabular-nums">{formatMetric(r.recall)}</span>
              </div>
            ))}
          </div>
          {/* Khối "Adjust n" trong sơ đồ kiến trúc */}
          <div className="flex flex-wrap items-end gap-3 rounded-lg bg-muted p-4">
            <label className="space-y-1.5">
              <span className="block text-[13px] font-semibold">Điều chỉnh Top n</span>
              <Input type="number" min={1} value={topN} onChange={(e) => setTopN(Number(e.target.value))} className="w-28" />
            </label>
            <Button onClick={recompute} disabled={recomputing || topN < 1}>{recomputing ? 'Đang tính...' : 'Áp dụng & tính lại'}</Button>
          </div>
        </Panel>
      </div>
    </Container>
  );
}
