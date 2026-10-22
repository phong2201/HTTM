import { BrowserRouter } from 'react-router-dom';
import { Toaster } from '@/app/components/ui/sonner';
import { AuthProvider } from '@/context/AuthContext';
import { ShopProvider } from '@/context/ShopContext';
import { AppRoutes } from './routes';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ShopProvider>
          <AppRoutes />
          <Toaster theme="light" position="top-right" richColors />
        </ShopProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
