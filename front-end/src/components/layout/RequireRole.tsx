import type { ReactNode } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { roleOf, type RoleId } from '@/config/roles';
import { Container } from '@/components/common/Page';
import { EmptyState, EMPTY } from '@/components/common/EmptyState';

interface RequireRoleProps {
  /** Bỏ trống = chỉ cần đăng nhập. */
  roles?: RoleId[];
  children?: ReactNode;
}

/** Thay cho ProtectedRoute / AdminRoute cũ; dùng chung cho Buyer, Admin, Data Scientist. */
export function RequireRole({ roles, children }: RequireRoleProps) {
  const { isAuthenticated, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="flex min-h-[50vh] items-center justify-center text-muted-foreground">Đang tải...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles && !roles.includes(roleOf(user?.role_id))) {
    return (
      <Container className="py-10">
        <EmptyState {...EMPTY.forbidden} />
      </Container>
    );
  }

  return <>{children ?? <Outlet />}</>;
}
