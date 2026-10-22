import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { toast } from 'sonner';
import { apiService, CATALOG_LIMIT } from '@/services/api';
import { useAuth } from '@/context/AuthContext';
import { toProduct, type CartItem, type Product } from '@/lib/product';
import { errorMessage } from '@/lib/format';

interface ShopContextType {
  products: Product[];
  productsLoading: boolean;
  productsError: string | null;
  cartItems: CartItem[];
  cartCount: number;
  cartTotal: number;
  isCartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  addToCart: (product: Product) => Promise<void>;
  updateQuantity: (id: string, quantity: number) => Promise<void>;
  removeFromCart: (id: string) => Promise<void>;
  clearCart: () => void;
  wishlistIds: Set<string>;
  isWishlisted: (id: string) => boolean;
  toggleWishlist: (product: Product) => Promise<boolean>;
}

const ShopContext = createContext<ShopContextType | undefined>(undefined);

export function ShopProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState<string | null>(null);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [wishlistIds, setWishlistIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!isAuthenticated) return;
    let active = true;
    setProductsLoading(true);
    apiService.getProducts(0, CATALOG_LIMIT)
      .then((items) => {
        if (!active) return;
        setProducts(items.map(toProduct));
        setProductsError(null);
      })
      .catch((error) => active && setProductsError(errorMessage(error, 'Không tải được sản phẩm')))
      .finally(() => active && setProductsLoading(false));
    return () => {
      active = false;
    };
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      setCartItems([]);
      setWishlistIds(new Set());
      return;
    }
    apiService.getCart()
      .then((items) => setCartItems(items
        .filter((item) => item.product)
        .map((item) => ({ ...toProduct(item.product!), quantity: item.quantity }))))
      .catch((error) => console.error('Load cart API error:', error));
    apiService.getWishlist()
      .then((items) => setWishlistIds(new Set(items.map((item) => item.product_id))))
      .catch((error) => console.error('Load wishlist API error:', error));
  }, [isAuthenticated]);

  const addToCart = useCallback(async (product: Product) => {
    try {
      await apiService.addToCart(product.id, 1);
    } catch (error) {
      toast.error(errorMessage(error, 'Không thêm được vào giỏ'));
      return;
    }
    setCartItems((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) return prev.map((item) => (item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
  }, []);

  const updateQuantity = useCallback(async (id: string, quantity: number) => {
    try {
      await apiService.updateCartItem(id, quantity);
      setCartItems((prev) => prev.map((item) => (item.id === id ? { ...item, quantity } : item)));
    } catch (error) {
      toast.error(errorMessage(error, 'Không cập nhật được giỏ hàng'));
    }
  }, []);

  const removeFromCart = useCallback(async (id: string) => {
    try {
      await apiService.removeCartItem(id);
      setCartItems((prev) => prev.filter((item) => item.id !== id));
    } catch (error) {
      toast.error(errorMessage(error, 'Không xóa được sản phẩm khỏi giỏ'));
    }
  }, []);

  /** Trả về trạng thái mới (true = đang trong wishlist). */
  const toggleWishlist = useCallback(async (product: Product) => {
    const liked = wishlistIds.has(product.id);
    try {
      if (liked) await apiService.removeWishlistItem(product.id);
      else await apiService.addToWishlist(product.id);
    } catch (error) {
      toast.error(errorMessage(error, 'Không cập nhật được wishlist'));
      return liked;
    }
    setWishlistIds((prev) => {
      const next = new Set(prev);
      if (liked) next.delete(product.id);
      else next.add(product.id);
      return next;
    });
    return !liked;
  }, [wishlistIds]);

  const value = useMemo<ShopContextType>(() => ({
    products,
    productsLoading,
    productsError,
    cartItems,
    cartCount: cartItems.reduce((sum, item) => sum + item.quantity, 0),
    cartTotal: cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0),
    isCartOpen,
    openCart: () => setIsCartOpen(true),
    closeCart: () => setIsCartOpen(false),
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart: () => setCartItems([]),
    wishlistIds,
    isWishlisted: (id) => wishlistIds.has(id),
    toggleWishlist,
  }), [products, productsLoading, productsError, cartItems, isCartOpen, addToCart, updateQuantity, removeFromCart, wishlistIds, toggleWishlist]);

  return <ShopContext.Provider value={value}>{children}</ShopContext.Provider>;
}

export function useShop() {
  const context = useContext(ShopContext);
  if (!context) throw new Error('useShop must be used within a ShopProvider');
  return context;
}
