import { Brain, ShieldCheck, User, type LucideIcon } from 'lucide-react';

// Role id giữ như backend. 1 = Seller không dùng trên giao diện.
export const ROLE = {
  BUYER: 2,
  ADMIN: 3,
  DATA_SCIENTIST: 4,
} as const;

export type RoleId = (typeof ROLE)[keyof typeof ROLE];

export interface RoleOption {
  id: RoleId;
  label: string;
  icon: LucideIcon;
  home: string;
}

export const ROLE_OPTIONS: RoleOption[] = [
  { id: ROLE.BUYER, label: 'Buyer', icon: User, home: '/' },
  { id: ROLE.ADMIN, label: 'Admin', icon: ShieldCheck, home: '/admin' },
  { id: ROLE.DATA_SCIENTIST, label: 'Data Scientist', icon: Brain, home: '/data-science' },
];

export function roleOf(roleId?: number | null): RoleId {
  const id = Number(roleId);
  return id === ROLE.ADMIN || id === ROLE.DATA_SCIENTIST ? id : ROLE.BUYER;
}

export function homeOf(roleId?: number | null): string {
  return ROLE_OPTIONS.find((option) => option.id === roleOf(roleId))?.home ?? '/';
}

export interface NavItem {
  to: string;
  label: string;
  end?: boolean;
}

const BUYER_NAV: NavItem[] = [
  { to: '/', label: 'Trang chủ', end: true },
  { to: '/products', label: 'Sản phẩm' },
  { to: '/wishlist', label: 'Wishlist' },
  { to: '/orders', label: 'Đơn hàng' },
];

export const NAV_BY_ROLE: Record<RoleId, NavItem[]> = {
  [ROLE.BUYER]: BUYER_NAV,
  [ROLE.ADMIN]: [
    ...BUYER_NAV,
    { to: '/admin', label: 'Admin' },
    { to: '/dashboard', label: 'Dashboard' },
  ],
  [ROLE.DATA_SCIENTIST]: [
    { to: '/', label: 'Trang chủ', end: true },
    { to: '/products', label: 'Sản phẩm' },
    { to: '/data-science', label: 'Data Science', end: true },
    { to: '/data-science/model', label: 'Model' },
    { to: '/data-science/schedule', label: 'Lịch chạy' },
    { to: '/data-science/errors', label: 'Phân tích lỗi' },
  ],
};

/** Ai được vào nhóm route nào. */
export const ACCESS = {
  shop: [ROLE.BUYER, ROLE.ADMIN, ROLE.DATA_SCIENTIST] as RoleId[],
  buyer: [ROLE.BUYER, ROLE.ADMIN] as RoleId[],
  admin: [ROLE.ADMIN] as RoleId[],
  dataScience: [ROLE.DATA_SCIENTIST, ROLE.ADMIN] as RoleId[],
};
