import { useCallback, useEffect, useState } from 'react';
import { AlarmClock, Check, Cloud, Loader2, Play, Save, Settings2, TreePine, TriangleAlert, Workflow } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from '@/app/components/ui/badge';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Switch } from '@/app/components/ui/switch';
import { cn } from '@/app/components/ui/utils';
import { Container, PageHeader, Panel, PanelTitle } from '@/components/common/Page';
import { Field, NativeSelect } from '@/components/common/Field';
import { Notice } from '@/components/common/Notice';
import { apiService, type TrainingConfig, type TrainingStatus } from '@/services/api';
import { errorMessage, formatDateTime, MISSING } from '@/lib/format';

const STEPS = [
  'Chọn subset & chia theo thời gian',
  'Sinh ứng viên',
  'Tạo feature',
  'Huấn luyện Random Forest',
  'Đánh giá vs baseline',
  'Ghi bảng Recommendations',
];

/** Giá trị khởi tạo form cấu hình (tham số đầu vào, không phải số liệu) — bị ghi đè bởi API nếu có. */
const DEFAULT_CONFIG: TrainingConfig = {
  schedule_enabled: true,
  schedule_time: '02:00',
  runner: 'kaggle',
  subset: 'sample',
  customer_frac: 0.1,
  top_n: 12,
  weeks: 4,
  train_weeks: 3,
  candidates_per_customer: 50,
  neg_pos_ratio: 5,
  n_estimators: 200,
  max_depth: 12,
  min_samples_leaf: 5,
};

const STATE_LABELS: Record<string, string> = { idle: 'Chưa chạy', running: 'Đang chạy', done: 'Hoàn tất', failed: 'Lỗi' };

const RF_FIELDS: Array<{ key: keyof TrainingConfig; label: string; step?: string }> = [
  { key: 'weeks', label: 'Số tuần dữ liệu' },
  { key: 'train_weeks', label: 'Số tuần nhãn train' },
  { key: 'candidates_per_customer', label: 'Số ứng viên/khách' },
  { key: 'neg_pos_ratio', label: 'Tỉ lệ dương:âm (1:x)', step: 'any' },
  { key: 'n_estimators', label: 'n_estimators' },
  { key: 'max_depth', label: 'max_depth' },
  { key: 'min_samples_leaf', label: 'min_samples_leaf' },
];

function nextRunAt(time: string): string {
  const [h, m] = time.split(':').map(Number);
  if (Number.isNaN(h) || Number.isNaN(m)) return MISSING;
  const next = new Date();
  next.setHours(h, m, 0, 0);
  if (next.getTime() <= Date.now()) next.setDate(next.getDate() + 1);
  return next.toLocaleString('vi-VN');
}

/** Màn 17 · Lịch chạy & huấn luyện. */
export function TrainingSchedulePage() {
  const [config, setConfig] = useState<TrainingConfig>(DEFAULT_CONFIG);
  const [status, setStatus] = useState<TrainingStatus | null>(null);
  const [statusError, setStatusError] = useState('');
  const [busy, setBusy] = useState<'save' | 'train' | null>(null);

  const loadStatus = useCallback((withConfig = false) => {
    apiService.getTrainingStatus()
      .then((data) => {
        setStatus(data);
        setStatusError('');
        if (withConfig && data.config) setConfig((prev) => ({ ...prev, ...data.config }));
      })
      .catch((err) => setStatusError(errorMessage(err, 'Không lấy được trạng thái huấn luyện')));
  }, []);

  useEffect(() => loadStatus(true), [loadStatus]);

  // Đang chạy → hỏi lại trạng thái mỗi 5 giây
  const isRunning = status?.state === 'running';
  useEffect(() => {
    if (!isRunning) return;
    const timer = window.setInterval(() => loadStatus(), 5000);
    return () => window.clearInterval(timer);
  }, [isRunning, loadStatus]);

  const run = async (kind: 'save' | 'train') => {
    setBusy(kind);
    try {
      if (kind === 'save') {
        await apiService.saveTrainingConfig(config);
        toast.success('Đã lưu cấu hình');
      } else {
        await apiService.saveTrainingConfig(config);
        const response = await apiService.triggerAITraining();
        toast.success(response.message || 'Đã kích hoạt huấn luyện');
        loadStatus();
      }
    } catch (err) {
      toast.error(errorMessage(err, kind === 'save' ? 'Không lưu được cấu hình' : 'Không kích hoạt được training'));
    } finally {
      setBusy(null);
    }
  };

  const resolve = async (action: 'overwrite' | 'keep') => {
    try {
      const response = await apiService.resolveTrainingException(action);
      toast.success(response.message);
      loadStatus();
    } catch (err) {
      toast.error(errorMessage(err, 'Không xử lý được ngoại lệ'));
    }
  };

  const setNumber = (key: keyof TrainingConfig, value: string) => setConfig((prev) => ({ ...prev, [key]: value === '' ? '' : Number(value) }));

  const done = Math.max(0, Math.min(STEPS.length, status?.completed_steps ?? 0));
  const running = isRunning;
  const exceptions = status?.exceptions;

  return (
    <Container className="py-8">
      <PageHeader
        icon={AlarmClock}
        title="Lịch chạy & huấn luyện"
        description="Gợi ý được tính sẵn và ghi vào bảng Recommendations"
        actions={
          <>
            <Button variant="outline" onClick={() => run('save')} disabled={busy !== null}><Save /> Lưu cấu hình</Button>
            <Button onClick={() => run('train')} disabled={busy !== null || running}><Play /> {busy === 'train' ? 'Đang kích hoạt...' : 'Train AI'}</Button>
          </>
        }
      />
      {statusError && <Notice tone="warning" className="mb-5">Không lấy được trạng thái huấn luyện: {statusError}.</Notice>}

      <div className="grid items-start gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <Panel>
            <PanelTitle icon={AlarmClock}>Lịch tự động</PanelTitle>
            <label className="mb-5 flex items-center justify-between gap-3 rounded-lg bg-muted px-4 py-3">
              <span className="text-sm font-semibold">Chạy mỗi ngày lúc {config.schedule_time}</span>
              <Switch checked={config.schedule_enabled} onCheckedChange={(checked) => setConfig((prev) => ({ ...prev, schedule_enabled: checked }))} />
            </label>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Giờ chạy" htmlFor="schedule_time">
                <Input id="schedule_time" type="time" value={config.schedule_time} onChange={(e) => setConfig((prev) => ({ ...prev, schedule_time: e.target.value }))} />
              </Field>
              <Field label="Lần chạy kế tiếp">
                <p className="flex h-10 items-center text-sm font-semibold">
                  {config.schedule_enabled ? (status?.next_run ? formatDateTime(status.next_run) : nextRunAt(config.schedule_time)) : MISSING}
                </p>
              </Field>
              <Field label="Top n" htmlFor="top_n">
                <Input id="top_n" type="number" min={1} max={50} value={config.top_n} onChange={(e) => setNumber('top_n', e.target.value)} />
              </Field>
            </div>
          </Panel>

          <Panel>
            <PanelTitle icon={Cloud}>Nơi chạy & dữ liệu</PanelTitle>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Chạy trên" htmlFor="runner">
                <NativeSelect id="runner" value={config.runner} onChange={(e) => setConfig((prev) => ({ ...prev, runner: e.target.value as TrainingConfig['runner'] }))}>
                  <option value="kaggle">Kaggle</option>
                  <option value="local">Máy local</option>
                </NativeSelect>
              </Field>
              <Field label="Dữ liệu" htmlFor="subset">
                <NativeSelect id="subset" value={config.subset} onChange={(e) => setConfig((prev) => ({ ...prev, subset: e.target.value as TrainingConfig['subset'] }))}>
                  <option value="sample">Lấy mẫu khách</option>
                  <option value="full">Toàn bộ khách</option>
                </NativeSelect>
              </Field>
              <Field label="Tỉ lệ mẫu (0–1)" htmlFor="customer_frac">
                <Input id="customer_frac" type="number" min={0.01} max={1} step={0.01} disabled={config.subset === 'full'} value={config.customer_frac} onChange={(e) => setNumber('customer_frac', e.target.value)} />
              </Field>
            </div>
            <p className="mt-3 text-[13px] text-muted-foreground">
              {config.runner === 'kaggle'
                ? 'Backend đẩy script lên Kaggle (dataset H&M gắn sẵn), chờ chạy xong rồi tải kết quả về. Cần kaggle.json trên máy chạy backend.'
                : 'Chạy ngay trên máy chạy backend, đọc dữ liệu ở data/hm.'}
            </p>
          </Panel>

          <Panel>
            <PanelTitle icon={TreePine}>Cấu hình Random Forest</PanelTitle>
            <div className="grid gap-4 sm:grid-cols-2">
              {RF_FIELDS.map(({ key, label, step }) => (
                <Field key={key} label={label} htmlFor={key}>
                  <Input id={key} type="number" min={0} step={step} value={config[key] as number} onChange={(e) => setNumber(key, e.target.value)} />
                </Field>
              ))}
            </div>
          </Panel>
        </div>

        <div className="space-y-6">
          <Panel>
            <PanelTitle
              icon={Workflow}
              aside={running ? <Badge variant="info">Đang chạy</Badge> : <Badge variant={status?.state === 'failed' ? 'danger' : status?.state === 'done' ? 'success' : 'neutral'}>{STATE_LABELS[status?.state ?? ''] ?? MISSING}</Badge>}
            >
              Tiến trình · {status?.run_id ?? 'run_—'}
            </PanelTitle>
            <ol className="mb-5 space-y-3">
              {STEPS.map((step, i) => {
                const state = i < done ? 'done' : i === done && running ? 'running' : 'waiting';
                return (
                  <li key={step} className="flex items-center gap-3 text-sm">
                    <span className={cn(
                      'flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-bold',
                      state === 'done' && 'bg-success text-white',
                      state === 'running' && 'bg-primary text-white',
                      state === 'waiting' && 'bg-muted text-faint',
                    )}>
                      {state === 'done' ? <Check className="size-4" /> : state === 'running' ? <Loader2 className="size-4 animate-spin" /> : i + 1}
                    </span>
                    <span className={cn(state === 'waiting' ? 'text-muted-foreground' : 'font-semibold')}>{step}</span>
                  </li>
                );
              })}
            </ol>
            <div className="h-2.5 overflow-hidden rounded-full bg-muted">
              <div className="h-full rounded-full transition-[width]" style={{ width: `${(done / STEPS.length) * 100}%`, background: 'linear-gradient(90deg, #E8112D, #FF7A3D)' }} />
            </div>
            <div className="mt-2 flex justify-between gap-3 text-xs text-muted-foreground">
              <span>{running && status?.current_step ? `${status.current_step}${status.runner === 'kaggle' ? ' · Kaggle' : ''}` : status?.active_run_id ? `Đang dùng: ${status.active_run_id}` : ''}</span>
              <span>{status ? `${done}/${STEPS.length} bước` : MISSING}</span>
            </div>
          </Panel>

          <Panel>
            <PanelTitle icon={TriangleAlert}>Ngoại lệ</PanelTitle>
            {!exceptions?.worse_than_baseline && !exceptions?.data_error ? (
              <p className="text-sm text-muted-foreground">Không có ngoại lệ ở lần chạy gần nhất.</p>
            ) : (
              <div className="space-y-3">
                {exceptions.worse_than_baseline && (
                  <Notice tone="warning" title="Metrics kém hơn baseline">Kết quả mới chưa được ghi vào bảng Recommendations.</Notice>
                )}
                {exceptions.data_error && <Notice tone="destructive" title="Dữ liệu lỗi">{exceptions.data_error}</Notice>}
                <div className="flex gap-2 pt-1">
                  {exceptions.worse_than_baseline ? (
                    <>
                      <Button variant="danger" onClick={() => resolve('overwrite')}><Settings2 /> Vẫn ghi đè</Button>
                      <Button variant="outline" onClick={() => resolve('keep')}>Giữ bản cũ</Button>
                    </>
                  ) : (
                    <Button variant="outline" onClick={() => resolve('keep')}>Bỏ qua · giữ bản hiện tại</Button>
                  )}
                </div>
              </div>
            )}
          </Panel>
        </div>
      </div>
    </Container>
  );
}
