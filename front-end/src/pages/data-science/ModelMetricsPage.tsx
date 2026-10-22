import { useCallback, useEffect, useState } from 'react';
import { Activity, BarChart3, Crosshair, Gauge, Layers, ListOrdered, RefreshCw, Scissors, Target } from 'lucide-react';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { Notice } from '@/components/common/Notice';
import { StatCard } from '@/components/common/StatCard';
import { Bar } from '@/components/common/Gradient';
import { tableBody, tableHead } from '@/components/common/table';
import { apiService, type MetricSet, type ModelMetrics, type ModelRun } from '@/services/api';
import { errorMessage, formatDateTime, formatMetric, formatNumber, MISSING } from '@/lib/format';

const KPIS: Array<{ key: keyof MetricSet; label: string; icon: typeof Target }> = [
  { key: 'map12', label: 'MAP@12', icon: Target },
  { key: 'recall12', label: 'Recall@12', icon: Crosshair },
  { key: 'precision12', label: 'Precision@12', icon: Gauge },
  { key: 'ndcg12', label: 'NDCG@12', icon: ListOrdered },
  { key: 'candidate_recall', label: 'Recall ứng viên', icon: Layers },
];

const SERIES = [
  { key: 'model', label: 'Random Forest', background: 'linear-gradient(90deg, #FF7A3D, #FFC93C)' },
  { key: 'bestseller', label: 'BL1 · Top-12 bán chạy', background: 'linear-gradient(90deg, #FF5E7E, #FFB38A)' },
  { key: 'repurchase', label: 'BL2 · Mua lại gần nhất', background: '#DCCFD2' },
] as const;

const SPLITS = [
  { key: 'train', label: 'Train', bg: '#FFE3D3', fg: '#C2410C', flex: 6 },
  { key: 'val', label: 'Val', bg: '#FFF3C4', fg: '#A16207', flex: 1 },
  { key: 'test', label: 'Test', bg: '#FFE3E8', fg: '#E8112D', flex: 1 },
] as const;

const RUN_STATUS: Record<string, { label: string; tone: 'success' | 'warning' | 'danger' }> = {
  written: { label: 'Đã ghi Recommendations', tone: 'success' },
  worse_than_baseline: { label: 'Kém hơn baseline', tone: 'warning' },
  data_error: { label: 'Lỗi dữ liệu', tone: 'danger' },
};

/** Màn 16 · Model metrics. Chịu được thiếu dữ liệu: mọi số thiếu → `—`. */
export function ModelMetricsPage() {
  const [data, setData] = useState<ModelMetrics | null>(null);
  const [error, setError] = useState('');

  const load = useCallback(() => {
    setError('');
    apiService.getModelMetrics()
      .then(setData)
      .catch((err) => { setData(null); setError(errorMessage(err, 'Chưa có API metrics model')); });
  }, []);

  useEffect(load, [load]);

  const metrics = data?.metrics ?? {};
  const hasComparison = Boolean(data?.baselines);
  const groups = [
    { key: 'map12' as const, label: 'MAP@12' },
    { key: 'recall12' as const, label: 'Recall@12' },
  ];
  const valueOf = (series: (typeof SERIES)[number]['key'], key: 'map12' | 'recall12') =>
    series === 'model' ? metrics[key] : data?.baselines?.[series]?.[key];
  const groupMax = (key: 'map12' | 'recall12') =>
    Math.max(0, ...SERIES.map((s) => valueOf(s.key, key) ?? 0));

  return (
    <Container className="py-8">
      <PageHeader
        icon={BarChart3}
        title="Model metrics"
        description="Đánh giá Random Forest ranker trên tập validation"
        actions={
          <>
            <Badge variant="info">{data?.run_id ?? 'run_—'} · {formatDateTime(data?.created_at)}</Badge>
            <Button variant="outline" onClick={load}><RefreshCw /> Tải lại</Button>
          </>
        }
      />
      {error && <Notice tone="warning" className="mb-5">Không lấy được metrics: {error}. Các số hiển thị “{MISSING}”.</Notice>}

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {KPIS.map(({ key, label, icon }, i) => <StatCard key={key} index={i} icon={icon} label={label} value={formatMetric(metrics[key])} />)}
      </div>

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <Panel>
          <PanelTitle icon={Activity} aside={!hasComparison && <Badge variant="warning">Minh họa · chưa có số thật</Badge>}>
            Random Forest so với baseline
          </PanelTitle>
          <div className="space-y-6">
            {groups.map(({ key, label }) => (
              <div key={key}>
                <p className="mb-2 text-sm font-bold">{label}</p>
                <div className="space-y-2">
                  {SERIES.map((s) => (
                    <div key={s.key} className="grid grid-cols-[170px_1fr_64px] items-center gap-3 text-[13px]">
                      <span className="truncate text-muted-foreground">{s.label}</span>
                      <Bar value={valueOf(s.key, key)} max={groupMax(key)} background={s.background} />
                      <span className="text-right font-semibold tabular-nums">{formatMetric(valueOf(s.key, key))}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel>
          <PanelTitle icon={Scissors}>Chia dữ liệu theo thời gian</PanelTitle>
          <div className="mb-5 flex h-12 overflow-hidden rounded-lg text-sm font-bold">
            {SPLITS.map((s) => (
              <div key={s.key} className="flex items-center justify-center" style={{ flex: s.flex, background: s.bg, color: s.fg }}>{s.label}</div>
            ))}
          </div>
          <ul className="space-y-2 text-sm">
            {SPLITS.map((s) => (
              <li key={s.key} className="flex gap-2">
                <span className="w-12 shrink-0 font-bold" style={{ color: s.fg }}>{s.label}</span>
                <span className="text-muted-foreground">{data?.split?.[s.key] ?? MISSING}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 rounded-lg bg-muted px-3 py-2 text-[13px] text-muted-foreground">Mọi feature chỉ tính từ dữ liệu trước cutoff (chống rò rỉ).</p>
        </Panel>
      </div>

      <Panel>
        <PanelTitle>Lịch sử lần chạy</PanelTitle>
        <RunsTable runs={data?.runs ?? []} />
      </Panel>
    </Container>
  );
}

function RunsTable({ runs }: { runs: ModelRun[] }) {
  if (runs.length === 0) return <p className="text-sm text-muted-foreground">{MISSING} Chưa có lần chạy nào được ghi nhận.</p>;
  return (
    <div className="-mx-6 overflow-x-auto">
      <table className="w-full text-sm">
        <thead className={tableHead}>
          <tr><th>run_id</th><th>Thời gian</th><th>Subset</th><th>n_estimators</th><th>max_depth</th><th>MAP@12 (val)</th><th>Trạng thái</th></tr>
        </thead>
        <tbody className={tableBody}>
          {runs.map((run) => {
            const status = RUN_STATUS[run.status];
            return (
              <tr key={run.run_id}>
                <td className="font-mono text-xs">{run.run_id}</td>
                <td>{formatDateTime(run.created_at)}</td>
                <td>{run.subset ?? MISSING}</td>
                <td className="tabular-nums">{formatNumber(run.n_estimators)}</td>
                <td className="tabular-nums">{formatNumber(run.max_depth)}</td>
                <td className="font-semibold tabular-nums">{formatMetric(run.val_map12)}</td>
                <td><Badge variant={status?.tone ?? 'neutral'}>{status?.label ?? run.status}</Badge></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
