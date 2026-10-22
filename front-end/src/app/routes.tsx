import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import { RequireRole } from '@/components/layout/RequireRole';
import { useAuth } from '@/context/AuthContext';
import { ACCESS, homeOf } from '@/config/roles';
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { HomePage } from '@/pages/buyer/HomePage';
import { ProductsPage } from '@/pages/buyer/ProductsPage';
import { ProductDetailPage } from '@/pages/buyer/ProductDetailPage';
import { WishlistPage } from '@/pages/buyer/WishlistPage';
import { CheckoutPage } from '@/pages/buyer/CheckoutPage';
import { OrdersPage } from '@/pages/buyer/OrdersPage';
import { AdminPage } from '@/pages/admin/AdminPage';
import { DashboardPage } from '@/pages/admin/DashboardPage';
import { DataSciencePage } from '@/pages/data-science/DataSciencePage';
import { ModelMetricsPage } from '@/pages/data-science/ModelMetricsPage';
import { TrainingSchedulePage } from '@/pages/data-science/TrainingSchedulePage';
import { ErrorAnalysisPage } from '@/pages/data-science/ErrorAnalysisPage';

/**
 * Bảng route theo sơ đồ (HUB_UI_SPEC mục 3–4):
 *  Buyer: / · /products · /products/:id · /wishlist · /checkout · /orders
 *  Admin: /admin · /dashboard
 *  Data Scientist: /data-science · /data-science/model · /data-science/schedule · /data-science/errors
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<RequireRole roles={ACCESS.shop}><AppLayout /></RequireRole>}>
        <Route index element={<HomePage />} />
        <Route path="products" element={<ProductsPage />} />
        <Route path="products/:id" element={<ProductDetailPage />} />

        <Route element={<RequireRole roles={ACCESS.buyer} />}>
          <Route path="wishlist" element={<WishlistPage />} />
          <Route path="checkout" element={<CheckoutPage />} />
          <Route path="orders" element={<OrdersPage />} />
        </Route>

        <Route element={<RequireRole roles={ACCESS.admin} />}>
          <Route path="admin" element={<AdminPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
        </Route>

        <Route path="data-science" element={<RequireRole roles={ACCESS.dataScience} />}>
          <Route index element={<DataSciencePage />} />
          <Route path="model" element={<ModelMetricsPage />} />
          <Route path="schedule" element={<TrainingSchedulePage />} />
          <Route path="errors" element={<ErrorAnalysisPage />} />
        </Route>
      </Route>

      <Route path="*" element={<FallbackRedirect />} />
    </Routes>
  );
}

function FallbackRedirect() {
  const { user } = useAuth();
  return <Navigate to={user ? homeOf(user.role_id) : '/login'} replace />;
}
