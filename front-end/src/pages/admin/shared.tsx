import type { ReactNode } from 'react';

export interface AdminTabProps {
  /** Đổi giá trị → tab tải lại dữ liệu. */
  reloadKey: number;
  /** Hàng tabs; tab tự đặt toolbar riêng bên phải. */
  tabBar: ReactNode;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export function TabToolbar({ tabBar, children }: { tabBar: ReactNode; children?: ReactNode }) {
  return (
    <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
      {tabBar}
      {children && <div className="flex flex-wrap items-center gap-2">{children}</div>}
    </div>
  );
}

export { tableHead, tableBody } from '@/components/common/table';
