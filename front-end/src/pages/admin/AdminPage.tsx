import { useState } from 'react';
import { Package, RefreshCw, ShoppingBag, Users, type LucideIcon } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';
import { Container, PageHeader } from '@/components/common/Page';
import { Notice } from '@/components/common/Notice';
import { UsersTab } from './UsersTab';
import { ProductsTab } from './ProductsTab';
import { OrdersTab } from './OrdersTab';
import type { AdminTabProps } from './shared';

type TabKey = 'users' | 'products' | 'orders';

const TABS: Array<{ key: TabKey; label: string; icon: LucideIcon }> = [
  { key: 'users', label: 'Users', icon: Users },
  { key: 'products', label: 'Products', icon: Package },
  { key: 'orders', label: 'Orders', icon: ShoppingBag },
];

/** Màn 11–13 · Admin CRUD. */
export function AdminPage() {
  const [tab, setTab] = useState<TabKey>('users');
  const [reloadKey, setReloadKey] = useState(0);
  const [notice, setNotice] = useState<{ tone: 'success' | 'destructive'; text: string } | null>(null);

  const onSuccess = (text: string) => {
    setNotice({ tone: 'success', text });
    window.setTimeout(() => setNotice((current) => (current?.text === text ? null : current)), 3000);
  };
  const onError = (text: string) => setNotice({ tone: 'destructive', text });

  const tabBar = (
    <div className="inline-flex gap-1 rounded-lg bg-border p-1">
      {TABS.map(({ key, label, icon: Icon }) => (
        <button
          key={key}
          onClick={() => setTab(key)}
          className={cn('flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold transition', tab === key ? 'bg-card text-primary shadow-sm' : 'text-muted-foreground hover:text-foreground')}
        >
          <Icon className="size-4" /> {label}
        </button>
      ))}
    </div>
  );

  const props: AdminTabProps = { reloadKey, tabBar, onSuccess, onError };

  return (
    <Container className="py-8">
      <PageHeader
        title="Admin CRUD"
        description="Quản lý user, sản phẩm và đơn hàng"
        actions={
          <Button variant="outline" onClick={() => { setNotice(null); setReloadKey((k) => k + 1); }}>
            <RefreshCw /> Tải lại
          </Button>
        }
      />
      {notice && <Notice tone={notice.tone} className="mb-4">{notice.text}</Notice>}
      {tab === 'users' && <UsersTab {...props} />}
      {tab === 'products' && <ProductsTab {...props} />}
      {tab === 'orders' && <OrdersTab {...props} />}
    </Container>
  );
}
