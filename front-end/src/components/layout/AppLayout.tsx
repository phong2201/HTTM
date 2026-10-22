import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { CartDrawer } from './CartDrawer';
import { Container } from '@/components/common/Page';
import { Notice } from '@/components/common/Notice';
import { useShop } from '@/context/ShopContext';

export function AppLayout() {
  const { productsError } = useShop();

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <CartDrawer />
      {productsError && (
        <Container className="pt-4">
          <Notice tone="destructive">Không kết nối được API sản phẩm: {productsError}</Notice>
        </Container>
      )}
      <main className="pb-16">
        <Outlet />
      </main>
    </div>
  );
}
