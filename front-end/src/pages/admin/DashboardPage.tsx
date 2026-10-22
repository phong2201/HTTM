import { useEffect, useState } from 'react';
import { CalendarDays, CircleDollarSign, Heart, MessageSquare, Package, ShoppingBag, Users } from 'lucide-react';
import { Badge } from '@/app/components/ui/badge';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { Notice } from '@/components/common/Notice';
import { StatCard } from '@/components/common/StatCard';
import { tableBody, tableHead } from '@/components/common/table';
import { apiService, type DashboardMetrics, type SalesStats, type SalesSummary } from '@/services/api';
import { errorMessage, formatDateTime, formatNumber, formatPrice, MISSING } from '@/lib/format';

/** Màn 14 · Dashboard quản trị. Thiếu số → `—`. */
export function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [sales, setSales] = useState<SalesSummary | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiService.getDashboardMetrics().then(setMetrics).catch((err) => setError(errorMessage(err, 'Không tải được dashboard')));
    apiService.getSalesSummary().then(setSales).catch((err) => setError(errorMessage(err, 'Không tải được doanh số')));
  }, []);

  const s = metrics?.summary;
  const stats = [
    { label: 'Tổng doanh thu', value: formatPrice(s?.revenue), icon: CircleDollarSign },
    { label: 'Đơn hàng', value: formatNumber(s?.orders), icon: ShoppingBag },
    { label: 'Người dùng', value: formatNumber(s?.users), icon: Users },
    { label: 'Sản phẩm', value: formatNumber(s?.products), icon: Package },
    { label: 'Wishlist', value: formatNumber(s?.wishlist_items), icon: Heart },
    { label: 'Feedback', value: formatNumber(s?.feedbacks), icon: MessageSquare },
  ];
  const topProducts = sales?.month.top_products?.length ? sales.month.top_products : metrics?.top_products ?? [];

  return (
    <Container className="py-8">
      <PageHeader title="Dashboard Quản Trị" description="Doanh số tính theo giờ Việt Nam, không gồm đơn đã hủy" />
      {error && <Notice tone="destructive" className="mb-4">{error}</Notice>}

      <div className="mb-6 grid gap-5 md:grid-cols-3">
        <PeriodCard title="Hôm nay" subtitle={sales?.today.key} stats={sales?.today} />
        <PeriodCard title="Tháng này" subtitle={sales?.month.key} stats={sales?.month} previous={sales?.previous_month} previousLabel="tháng trước" />
        <PeriodCard title="Năm nay" subtitle={sales?.year.key} stats={sales?.year} previous={sales?.previous_year} previousLabel="năm trước" />
      </div>

      <div className="mb-8 grid items-start gap-6 lg:grid-cols-[2fr_1fr]">
        <Panel>
          <PanelTitle icon={CalendarDays}>Doanh thu theo tháng</PanelTitle>
          <MonthChart months={sales?.closed_months ?? []} current={sales?.month} />
        </Panel>
        <Panel>
          <PanelTitle>Top sản phẩm {sales?.month.top_products?.length ? 'tháng này' : ''}</PanelTitle>
          {topProducts.length === 0 ? (
            <p className="text-sm text-muted-foreground">{MISSING}</p>
          ) : (
            <ol className="divide-y divide-border">
              {topProducts.slice(0, 5).map((product, index) => (
                <li key={product.id} className="flex items-center justify-between gap-3 py-3">
                  <div className="flex min-w-0 items-center gap-3">
                    <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-bold text-primary">{index + 1}</span>
                    <div className="min-w-0">
                      <p className="truncate font-semibold">{product.name}</p>
                      <p className="text-[13px] text-muted-foreground">Đã bán: {formatNumber(product.sold)}</p>
                    </div>
                  </div>
                  <span className="shrink-0 text-sm font-bold text-success">{formatPrice(product.revenue)}</span>
                </li>
              ))}
            </ol>
          )}
        </Panel>
      </div>

      <h2 className="mb-4 text-lg font-bold">Tổng quan hệ thống</h2>
      <div className="mb-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((stat, i) => <StatCard key={stat.label} index={i} {...stat} />)}
      </div>

      <Panel>
        <PanelTitle>Sổ đã chốt</PanelTitle>
        <ClosedPeriods months={sales?.closed_months ?? []} years={sales?.closed_years ?? []} />
      </Panel>
    </Container>
  );
}

function PeriodCard({ title, subtitle, stats, previous, previousLabel }: {
  title: string; subtitle?: string; stats?: SalesStats; previous?: SalesStats | null; previousLabel?: string;
}) {
  const change = stats && previous?.revenue ? stats.revenue / previous.revenue - 1 : null;
  return (
    <div className="rounded-[10px] bg-card p-5 shadow-card">
      <div className="mb-2 flex items-center justify-between">
        <p className="text-sm font-semibold">{title}</p>
        <span className="text-xs text-faint">{subtitle ?? MISSING}</span>
      </div>
      <p className="text-[28px] font-black leading-tight">{formatPrice(stats?.revenue)}</p>
      <p className="mt-1 text-[13px] text-muted-foreground">
        {formatNumber(stats?.orders)} đơn · {formatNumber(stats?.items)} món · {formatNumber(stats?.customers)} khách
        {stats?.cancelled_orders ? ` · ${stats.cancelled_orders} hủy` : ''}
      </p>
      {previousLabel && (
        <p className="mt-2 text-xs">
          {change === null ? (
            <span className="text-faint">Chưa có sổ {previousLabel} để so sánh</span>
          ) : (
            <Badge variant={change >= 0 ? 'success' : 'danger'}>{change >= 0 ? '+' : ''}{(change * 100).toFixed(0)}% so với {previousLabel}</Badge>
          )}
        </p>
      )}
    </div>
  );
}

function MonthChart({ months, current }: { months: SalesStats[]; current?: SalesStats }) {
  const bars = [...months.map((m) => ({ ...m, live: false })), ...(current ? [{ ...current, live: true }] : [])];
  const max = Math.max(1, ...bars.map((b) => b.revenue));
  if (bars.length === 0) return <p className="text-sm text-muted-foreground">{MISSING}</p>;
  return (
    <div className="flex h-56 items-end gap-3">
      {bars.map((b) => (
        <div key={b.key} className="flex min-w-0 flex-1 flex-col items-center gap-1.5" title={`${b.key}: ${formatPrice(b.revenue)} · ${b.orders} đơn`}>
          <span className="text-[11px] font-semibold text-muted-foreground">{b.revenue ? `${(b.revenue / 1e6).toFixed(1)}tr` : ''}</span>
          <div
            className="w-full max-w-14 rounded-t-md"
            style={{
              height: `${Math.max(2, (b.revenue / max) * 170)}px`,
              background: b.live ? 'linear-gradient(180deg, #E8112D, #FF7A3D)' : 'linear-gradient(180deg, #FFB38A, #FFE066)',
            }}
          />
          <span className={`text-[11px] ${b.live ? 'font-bold text-primary' : 'text-muted-foreground'}`}>{b.key.slice(2)}</span>
        </div>
      ))}
    </div>
  );
}

function ClosedPeriods({ months, years }: { months: SalesStats[]; years: SalesStats[] }) {
  const rows = [...years.map((y) => ({ ...y, type: 'Năm' })), ...[...months].reverse().map((m) => ({ ...m, type: 'Tháng' }))];
  if (rows.length === 0) return <p className="text-sm text-muted-foreground">Chưa có kỳ nào kết thúc — sổ tháng được chốt tự động khi sang tháng mới.</p>;
  return (
    <div className="-mx-6 overflow-x-auto">
      <table className="w-full text-sm">
        <thead className={tableHead}><tr><th>Kỳ</th><th>Doanh thu</th><th>Đơn</th><th>Món</th><th>Khách</th><th>Hủy</th><th>Chốt lúc</th></tr></thead>
        <tbody className={tableBody}>
          {rows.map((r) => (
            <tr key={`${r.type}-${r.key}`}>
              <td className="font-semibold">{r.type} {r.key}</td>
              <td className="font-semibold text-primary">{formatPrice(r.revenue)}</td>
              <td className="tabular-nums">{formatNumber(r.orders)}</td>
              <td className="tabular-nums">{formatNumber(r.items)}</td>
              <td className="tabular-nums">{formatNumber(r.customers)}</td>
              <td className="tabular-nums">{formatNumber(r.cancelled_orders)}</td>
              <td className="text-muted-foreground">{formatDateTime(r.closed_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
