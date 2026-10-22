import { useState, type FormEvent } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Heart, LogOut, PackageCheck, Search, ShoppingCart, User } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/app/components/ui/dropdown-menu';
import { useAuth } from '@/context/AuthContext';
import { useShop } from '@/context/ShopContext';
import { NAV_BY_ROLE, ROLE, roleOf } from '@/config/roles';

export function Logo({ size = 26 }: { size?: number }) {
  return (
    <Link to="/" className="font-black leading-none tracking-tight text-primary" style={{ fontSize: size }}>
      HUB
    </Link>
  );
}

export function Header() {
  const { user, logout } = useAuth();
  const { cartCount, openCart } = useShop();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const role = roleOf(user?.role_id);
  const nav = NAV_BY_ROLE[role];
  const canBuy = role !== ROLE.DATA_SCIENTIST;

  const submitSearch = (event: FormEvent) => {
    event.preventDefault();
    const q = query.trim();
    navigate(q ? `/products?q=${encodeURIComponent(q)}` : '/products');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-card">
      <div className="mx-auto flex h-16 max-w-[1280px] items-center gap-6 px-4 xl:px-0">
        <Logo />
        <nav className="hidden items-center gap-5 lg:flex">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => cn('whitespace-nowrap text-sm transition-colors hover:text-primary', isActive ? 'font-semibold text-primary' : 'text-foreground')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <form onSubmit={submitSearch} className="relative hidden flex-1 md:block">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm kiếm sản phẩm..."
            className="h-10 w-full rounded-lg border border-border-strong bg-card pl-9 pr-3 text-sm outline-none placeholder:text-faint focus-visible:border-primary focus-visible:ring-[3px] focus-visible:ring-primary/20"
          />
        </form>

        <div className="ml-auto flex items-center gap-2 md:ml-0">
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-lg px-2 py-2 text-sm font-medium outline-none hover:bg-canvas">
              <User className="size-5" />
              <span className="hidden max-w-[120px] truncate sm:inline">{user?.username}</span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52">
              <DropdownMenuLabel>
                <p className="text-sm font-semibold">{user?.username}</p>
                <p className="truncate text-xs font-normal text-muted-foreground">{user?.email}</p>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              {/* Menu chính ẩn trên màn nhỏ → lặp lại ở đây */}
              <div className="lg:hidden">
                {nav.map((item) => (
                  <DropdownMenuItem key={item.to} onSelect={() => navigate(item.to)}>{item.label}</DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
              </div>
              {canBuy && (
                <>
                  <DropdownMenuItem onSelect={() => navigate('/wishlist')}><Heart /> Wishlist</DropdownMenuItem>
                  <DropdownMenuItem onSelect={() => navigate('/orders')}><PackageCheck /> Đơn hàng</DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem variant="destructive" onSelect={handleLogout}><LogOut /> Đăng xuất</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {canBuy && (
            <button onClick={openCart} className="relative rounded-lg p-2 hover:bg-canvas" aria-label="Mở giỏ hàng">
              <ShoppingCart className="size-6" />
              {cartCount > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-primary px-1 text-[11px] font-bold text-white">
                  {cartCount}
                </span>
              )}
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
