import { useState, type FormEvent } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Heart, LogOut, PackageCheck, Search, ShoppingCart, Sparkles, User } from 'lucide-react';
import { cn } from '@/app/components/ui/utils';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/app/components/ui/dropdown-menu';
import { useAuth } from '@/context/AuthContext';
import { useShop } from '@/context/ShopContext';
import { NAV_BY_ROLE, ROLE, roleOf } from '@/config/roles';

export function Logo({ size = 26 }: { size?: number }) {
  return (
    <Link
      to="/"
      className="group inline-flex items-center gap-1.5 font-black leading-none tracking-tight text-primary transition-transform duration-150 hover:scale-[1.03]"
      style={{ fontSize: size }}
    >
      <span>HUB</span>
      <span className="inline-block size-2 rounded-full bg-gradient-to-tr from-[#E8112D] to-[#FF7A3D] transition-transform duration-200 group-hover:scale-125" />
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

  const roleBadgeLabel =
    role === ROLE.DATA_SCIENTIST ? 'Data Scientist' : role === ROLE.ADMIN ? 'Admin' : null;

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
    <header className="sticky top-0 z-40 w-full border-b border-border/80 bg-card/90 backdrop-blur-md transition-shadow">
      <div className="mx-auto flex h-16 max-w-[1280px] items-center gap-5 px-4 xl:px-0">
        <div className="flex items-center gap-2.5">
          <Logo />
          {roleBadgeLabel && (
            <span className="hidden items-center gap-1 rounded-full bg-accent px-2.5 py-0.5 text-[11px] font-bold text-primary sm:inline-flex">
              <Sparkles className="size-3" />
              {roleBadgeLabel}
            </span>
          )}
        </div>

        <nav className="hidden items-center gap-1.5 lg:flex">
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  'relative whitespace-nowrap rounded-lg px-3 py-1.5 text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-accent/80 font-bold text-primary shadow-2xs'
                    : 'text-foreground/80 hover:bg-canvas hover:text-primary',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <form onSubmit={submitSearch} className="relative hidden flex-1 md:block">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-faint transition-colors" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tìm kiếm sản phẩm, danh mục, màu sắc..."
            className="h-10 w-full rounded-full border border-border-strong/80 bg-muted/60 pl-10 pr-4 text-sm outline-none transition-all duration-150 placeholder:text-faint hover:border-border-strong hover:bg-card focus-visible:border-primary focus-visible:bg-card focus-visible:ring-[3px] focus-visible:ring-primary/15"
          />
        </form>

        <div className="ml-auto flex items-center gap-2 md:ml-0">
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1.5 text-sm font-medium shadow-2xs outline-none transition-all duration-150 hover:border-primary/30 hover:bg-canvas">
              <span className="flex size-6 items-center justify-center rounded-full bg-gradient-to-br from-[#E8112D] to-[#FF7A3D] text-xs font-bold text-white">
                {user?.username?.charAt(0).toUpperCase() || <User className="size-3.5" />}
              </span>
              <span className="hidden max-w-[120px] truncate font-semibold sm:inline">{user?.username}</span>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <p className="text-sm font-bold">{user?.username}</p>
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
            <button
              onClick={openCart}
              className="relative flex size-10 items-center justify-center rounded-full border border-border bg-card transition-all duration-150 hover:border-primary/30 hover:bg-canvas"
              aria-label="Mở giỏ hàng"
            >
              <ShoppingCart className="size-5 text-foreground" />
              {cartCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-gradient-to-r from-[#E8112D] to-[#FF7A3D] px-1 text-[11px] font-bold text-white shadow-xs">
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
