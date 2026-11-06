export const MISSING = '—';

const isNumber = (value: unknown): value is number =>
  typeof value === 'number' && Number.isFinite(value);

/** Giá VND — backend quy đổi ước lượng từ giá chuẩn hóa của H&M (settings.HM_PRICE_TO_VND). */
export function formatPrice(value?: number | null): string {
  if (!isNumber(value)) return MISSING;
  return `${Math.round(value).toLocaleString('vi-VN')}₫`;
}

export const PRICE_NOTE = 'Giá quy đổi ước lượng từ giá chuẩn hóa của dataset H&M';

export function formatNumber(value?: number | null, digits = 0): string {
  if (!isNumber(value)) return MISSING;
  return value.toLocaleString('vi-VN', { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

/** Metrics dạng 0.0–1.0, hiển thị 4 chữ số thập phân. */
export function formatMetric(value?: number | null): string {
  return isNumber(value) ? value.toFixed(4) : MISSING;
}

export function formatDateTime(value?: string | null): string {
  if (!value) return MISSING;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? MISSING : date.toLocaleString('vi-VN');
}

export function shortId(id: string): string {
  return id.replace(/-/g, '').slice(0, 8);
}

export function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}
