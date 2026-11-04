import { useEffect, useState } from 'react';
import { Brain, Database, Play, Sparkles, Target, TrendingUp } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { Notice } from '@/components/common/Notice';
import { apiService, type Insights } from '@/services/api';
import { errorMessage } from '@/lib/format';

interface Figure { title: string; src: string }

/** "3_1_2_missing_value_analysis.png" → "3.1.2 · Missing value analysis", sắp theo số mục. */
function toFigures(images: Record<string, string>): Figure[] {
  return Object.entries(images)
    .map(([path, src]) => {
      const file = path.split('/').pop()!.replace(/\.png$/, '');
      const match = file.match(/^(\d+)_(\d+)_(\d+)_(.+)$/);
      const order = match ? [Number(match[1]), Number(match[2]), Number(match[3])] : [0, 0, 0];
      const name = (match?.[4] ?? file).replace(/_/g, ' ');
      return { order, title: `${order.join('.')} · ${name.charAt(0).toUpperCase()}${name.slice(1)}`, src };
    })
    .sort((a, b) => a.order[0] - b.order[0] || a.order[1] - b.order[1] || a.order[2] - b.order[2])
    .map(({ title, src }) => ({ title, src }));
}

const EMPTY = { source: 'chưa có run', original: [] as Figure[], normalized: [] as Figure[] };

const fromApi = (items: Array<{ file: string; url: string }>) => toFigures(Object.fromEntries(items.map((i) => [i.file, i.url])));

/** Màn 15 · Data Science · EDA & tiền xử lý. */
export function DataSciencePage() {
  const [training, setTraining] = useState(false);
  const [notice, setNotice] = useState<{ tone: 'success' | 'destructive'; text: string } | null>(null);
  const [reports, setReports] = useState(EMPTY);
  const [insights, setInsights] = useState<Insights | null>(null);

  useEffect(() => {
    apiService.getEdaReports()
      .then((data) => {
        if (data.run_id && data.original.length + data.normalized.length > 0) {
          setReports({ source: data.run_id, original: fromApi(data.original), normalized: fromApi(data.normalized) });
        }
      })
      .catch(() => undefined); // chưa có run → hiện trạng thái trống
    apiService.getInsights().then(setInsights).catch(() => setInsights(null));
  }, []);

  const triggerTraining = async () => {
    setTraining(true);
    setNotice(null);
    try {
      const response = await apiService.triggerAITraining();
      setNotice({ tone: 'success', text: response.message || 'Đã kích hoạt huấn luyện' });
    } catch (err) {
      setNotice({ tone: 'destructive', text: errorMessage(err, 'Không kích hoạt được training') });
    } finally {
      setTraining(false);
    }
  };

  return (
    <Container className="py-8">
      <PageHeader
        icon={Brain}
        title="Data Science & Analytics"
        description={<>EDA & tiền xử lý dữ liệu · báo cáo <code className="rounded bg-accent px-1.5 py-0.5 text-[13px] font-semibold text-primary">{reports.source}</code></>}
        actions={<Button onClick={triggerTraining} disabled={training}><Play /> {training ? 'Đang kích hoạt...' : 'Train AI'}</Button>}
      />
      {notice && <Notice tone={notice.tone} className="mb-5">{notice.text}</Notice>}

      <div className="mb-8 grid items-start gap-6 lg:grid-cols-2">
        <FigurePanel icon={Database} title="Original · dữ liệu gốc" figures={reports.original} />
        <FigurePanel icon={Sparkles} title="Normalized · sau tiền xử lý" figures={reports.normalized} />
      </div>

      {/* Nhận xét do backend ghép từ số liệu của run — không viết tay */}
      <div className="grid items-start gap-6 md:grid-cols-2">
        {[
          { icon: TrendingUp, title: 'Xu hướng sản phẩm', items: insights?.trend },
          { icon: Target, title: 'Tối ưu hóa gợi ý', items: insights?.optimization },
        ].map(({ icon: Icon, title, items }) => (
          <Panel key={title} className="relative overflow-hidden border-l-4 border-l-primary">
            <div className="mb-3 flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-xl bg-accent text-primary">
                <Icon className="size-5" />
              </span>
              <h3 className="text-lg font-bold tracking-tight">{title}</h3>
            </div>
            {items?.length ? (
              <ul className="list-disc space-y-2 pl-5 text-sm leading-6 text-foreground/85 marker:text-primary">
                {items.map((item) => <li key={item}>{item}</li>)}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">Chưa có kết quả pipeline — bấm Train AI.</p>
            )}
            {insights?.run_id && <p className="mt-4 text-xs font-medium text-faint">Nguồn: {insights.run_id}</p>}
          </Panel>
        ))}
      </div>
    </Container>
  );
}

function FigurePanel({ icon, title, figures }: { icon: typeof Brain; title: string; figures: Figure[] }) {
  const [failed, setFailed] = useState<Record<string, boolean>>({});

  return (
    <Panel>
      <PanelTitle icon={icon} aside={<Badge variant="neutral">{figures.length} hình</Badge>}>{title}</PanelTitle>
      {figures.length === 0 ? (
        <p className="text-sm text-muted-foreground">Chưa có báo cáo — bấm Train AI để sinh.</p>
      ) : (
        <div className="space-y-4">
          {figures.map((figure) => (
            <figure
              key={figure.src}
              className="group overflow-hidden rounded-xl border border-border/90 bg-card transition-all duration-200 hover:border-primary/30 hover:shadow-md"
            >
              <figcaption className="flex items-center justify-between border-b border-border bg-muted/50 px-3.5 py-2 text-[13px] font-bold tracking-tight">
                <span>{figure.title}</span>
              </figcaption>
              {failed[figure.src] ? (
                <div className="flex min-h-40 items-center justify-center bg-img-ph p-4 text-sm text-muted-foreground">Không tải được ảnh</div>
              ) : (
                <img
                  src={figure.src}
                  alt={figure.title}
                  loading="lazy"
                  className="block h-auto w-full transition-transform duration-300 group-hover:scale-[1.01]"
                  onError={() => setFailed((prev) => ({ ...prev, [figure.src]: true }))}
                />
              )}
            </figure>
          ))}
        </div>
      )}
    </Panel>
  );
}
