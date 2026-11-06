// API configuration and base setup
/** Số sản phẩm tối đa tải về một lần (catalog H&M của web ~7.000 món). */
export const CATALOG_LIMIT = 10000;
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserData {
  id: string;
  username: string;
  email?: string;
  role_id?: number;
  gender?: string;
  age?: number;
  created_at?: string;
  updated_at?: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  gender?: string;
  age?: number;
}

/** Sản phẩm theo cột articles.csv của H&M (tên/mô tả tiếng Anh). price: VND quy đổi ước lượng. */
export interface BackendProduct {
  id: string;
  article_id?: string | null;
  product_code?: string | null;
  prod_name: string;
  product_type_name?: string | null;
  product_group_name?: string | null;
  colour_group_name?: string | null;
  graphical_appearance_name?: string | null;
  index_group_name?: string | null;
  detail_desc?: string | null;
  price: number;
  image_url?: string | null;
  sales_last_week?: number | null;
  quantity_in_stock?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductSearchParams {
  q?: string;
  index_group?: string;
  product_group?: string;
  colour?: string;
}

export interface CartItemResponse {
  id: number;
  user_id: string;
  product_id: string;
  quantity: number;
  product?: BackendProduct | null;
}

export interface WishlistItemResponse {
  id: string;
  user_id: string;
  product_id: string;
  product?: BackendProduct | null;
}

export interface FeedbackResponse {
  id: string;
  user_id: string;
  product_id: string;
  rank: number;
  created_at: string;
  updated_at: string;
}

export interface OrderResponse {
  id: string;
  user_id: string;
  order_date: string;
  status: number | string;
  total_amount: number;
  note?: string | null;
  items: Array<{
    id: number;
    product_id: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
    product?: BackendProduct | null;
  }>;
  updated_at: string;
}

export interface RecommendationItem {
  product_id: string;
  score: number;
  rank: number;
  product_details?: BackendProduct | null;
}

export interface DashboardMetrics {
  summary: {
    products: number;
    orders: number;
    users: number;
    revenue: number;
    cart_items: number;
    wishlist_items: number;
    feedbacks: number;
  };
  top_products: Array<{
    id: string;
    name: string;
    image_url?: string | null;
    sold: number;
    revenue: number;
  }>;
}

export interface SalesStats {
  key: string;
  orders: number;
  cancelled_orders: number;
  items: number;
  customers: number;
  revenue: number;
  top_products?: Array<{ id: string; name: string; sold: number; revenue: number }>;
  closed_at?: string;
}

/** Doanh số: hôm nay / kỳ hiện tại tính tới giờ + các kỳ đã chốt sổ (backend/services/sales_service.py). */
export interface SalesSummary {
  today: SalesStats;
  month: SalesStats;
  year: SalesStats;
  previous_month: SalesStats | null;
  previous_year: SalesStats | null;
  closed_months: SalesStats[];
  closed_years: SalesStats[];
}

// ---- Data Science · pipeline H&M + Random Forest (backend/routers/hm_ai.py) ----

export interface MetricSet {
  map12?: number | null;
  recall12?: number | null;
  precision12?: number | null;
  ndcg12?: number | null;
  candidate_recall?: number | null;
}

export interface ModelRun {
  run_id: string;
  created_at: string;
  subset?: string | null;
  n_estimators?: number | null;
  max_depth?: number | null;
  val_map12?: number | null;
  status: 'written' | 'worse_than_baseline' | 'data_error' | string;
}

export interface ModelMetrics {
  run_id?: string | null;
  created_at?: string | null;
  metrics: MetricSet;
  baselines?: {
    bestseller?: MetricSet | null;
    repurchase?: MetricSet | null;
  } | null;
  split?: { train?: string | null; val?: string | null; test?: string | null } | null;
  runs: ModelRun[];
}

export interface TrainingConfig {
  schedule_enabled: boolean;
  schedule_time: string;
  /** Nơi chạy pipeline: Kaggle (dataset gắn sẵn) hoặc máy local (cần data/hm). */
  runner: 'kaggle' | 'local';
  subset: 'sample' | 'full';
  customer_frac: number;
  top_n: number;
  weeks: number;
  /** Số tuần nhãn dùng để train (các tuần ngay trước tuần val). */
  train_weeks: number;
  candidates_per_customer: number;
  neg_pos_ratio: number;
  n_estimators: number;
  max_depth: number;
  min_samples_leaf: number;
}

export interface TrainingStatus {
  run_id?: string | null;
  runner?: 'kaggle' | 'local' | null;
  state: 'idle' | 'running' | 'done' | 'failed' | string;
  /** Số bước đã xong (0–6). */
  completed_steps: number;
  current_step?: string | null;
  error?: string | null;
  active_run_id?: string | null;
  next_run?: string | null;
  config?: Partial<TrainingConfig> | null;
  exceptions?: {
    worse_than_baseline?: boolean;
    data_error?: string | null;
  } | null;
}

export interface EdaReports {
  run_id?: string | null;
  original: Array<{ file: string; url: string }>;
  normalized: Array<{ file: string; url: string }>;
}

/** Nhận xét tính từ kết quả run (backend ghép câu từ số liệu thật). */
export interface Insights {
  run_id: string;
  trend: string[];
  optimization: string[];
}

export interface ErrorAnalysis {
  by_customer: Array<{ segment: string; customers?: number | null; map12?: number | null; recall12?: number | null }>;
  by_product_group: Array<{ product_group_name: string; purchases?: number | null; precision12?: number | null; recall12?: number | null }>;
  feature_importance: Array<{ feature: string; importance: number }>;
  candidate_recall: Array<{ source: string; recall?: number | null }>;
}

class APIService {
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getHeaders(): HeadersInit {
    const token = this.getToken();
    const headers: HeadersInit = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  private async parseResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();
    if (!response.ok) {
      const detail = typeof payload === 'object' ? payload.detail || payload.message : payload;
      throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || fallbackMessage);
    }
    return payload as T;
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });
    return this.parseResponse<LoginResponse>(response, 'Login failed');
  }

  async register(data: RegisterData): Promise<UserData> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<UserData>(response, 'Registration failed');
  }

  async getCurrentUser(): Promise<UserData> {
    const response = await fetch(`${API_BASE_URL}/users/me`, { headers: this.getHeaders() });
    return this.parseResponse<UserData>(response, 'Failed to fetch current user');
  }

  async listUsers(): Promise<UserData[]> {
    const response = await fetch(`${API_BASE_URL}/users`, { headers: this.getHeaders() });
    return this.parseResponse<UserData[]>(response, 'Failed to fetch users');
  }

  async getProducts(skip = 0, limit = 100): Promise<BackendProduct[]> {
    const response = await fetch(`${API_BASE_URL}/products/?skip=${skip}&limit=${limit}`, { headers: this.getHeaders() });
    return this.parseResponse<BackendProduct[]>(response, 'Failed to fetch products');
  }

  async getProductById(id: string): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, { headers: this.getHeaders() });
    return this.parseResponse<BackendProduct>(response, 'Failed to fetch product');
  }

  async addToCart(productId: string, quantity: number): Promise<CartItemResponse> {
    const response = await fetch(`${API_BASE_URL}/cart`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    return this.parseResponse<CartItemResponse>(response, 'Failed to add to cart');
  }

  async getCart(): Promise<CartItemResponse[]> {
    const response = await fetch(`${API_BASE_URL}/cart`, { headers: this.getHeaders() });
    return this.parseResponse<CartItemResponse[]>(response, 'Failed to fetch cart');
  }

  async updateCartItem(productId: string, quantity: number): Promise<CartItemResponse> {
    const response = await fetch(`${API_BASE_URL}/cart/${productId}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    return this.parseResponse<CartItemResponse>(response, 'Failed to update cart');
  }

  async removeCartItem(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/cart/${productId}`, { method: 'DELETE', headers: this.getHeaders() });
    return this.parseResponse<{ message: string }>(response, 'Failed to remove cart item');
  }

  async addToWishlist(productId: string): Promise<WishlistItemResponse> {
    const response = await fetch(`${API_BASE_URL}/wishlist`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId }),
    });
    return this.parseResponse<WishlistItemResponse>(response, 'Failed to add to wishlist');
  }

  async getWishlist(): Promise<WishlistItemResponse[]> {
    const response = await fetch(`${API_BASE_URL}/wishlist`, { headers: this.getHeaders() });
    return this.parseResponse<WishlistItemResponse[]>(response, 'Failed to fetch wishlist');
  }

  async removeWishlistItem(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/wishlist/${productId}`, { method: 'DELETE', headers: this.getHeaders() });
    return this.parseResponse<{ message: string }>(response, 'Failed to remove wishlist item');
  }

  async createOrder(items: Array<{ product_id: string; quantity: number }>, note?: string): Promise<OrderResponse> {
    const response = await fetch(`${API_BASE_URL}/orders`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ items, note }),
    });
    return this.parseResponse<OrderResponse>(response, 'Failed to create order');
  }

  async getMyOrders(): Promise<OrderResponse[]> {
    const response = await fetch(`${API_BASE_URL}/orders/me`, { headers: this.getHeaders() });
    return this.parseResponse<OrderResponse[]>(response, 'Failed to fetch orders');
  }

  async getAllOrders(): Promise<OrderResponse[]> {
    const response = await fetch(`${API_BASE_URL}/orders`, { headers: this.getHeaders() });
    return this.parseResponse<OrderResponse[]>(response, 'Failed to fetch all orders');
  }

  async createFeedback(userId: string, productId: string, rank: number): Promise<FeedbackResponse> {
    const response = await fetch(`${API_BASE_URL}/feedback/${userId}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_id: productId, rank }),
    });
    return this.parseResponse<FeedbackResponse>(response, 'Failed to submit feedback');
  }

  async getFeedbacksByProduct(productId: string): Promise<FeedbackResponse[]> {
    const response = await fetch(`${API_BASE_URL}/feedback/product/${productId}`, { headers: this.getHeaders() });
    return this.parseResponse<FeedbackResponse[]>(response, 'Failed to fetch feedbacks');
  }

  async getRecommendations(userId: string, k = 10): Promise<RecommendationItem[]> {
    const response = await fetch(`${API_BASE_URL}/predict/${userId}?k=${k}`, { headers: this.getHeaders() });
    return this.parseResponse<RecommendationItem[]>(response, 'Failed to fetch recommendations');
  }


  async updateUserRole(username: string, role_id: number): Promise<{ username: string; new_role: number }> {
    const response = await fetch(`${API_BASE_URL}/auth/${username}/role`, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify({ role_id }),
    });
    return this.parseResponse<{ username: string; new_role: number }>(response, 'Failed to update user role');
  }

  async deleteUser(userId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to delete user');
  }

  async createProduct(data: Partial<BackendProduct>): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<BackendProduct>(response, 'Failed to create product');
  }

  async updateProduct(productId: string, data: Partial<BackendProduct>): Promise<BackendProduct> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.parseResponse<BackendProduct>(response, 'Failed to update product');
  }

  async deleteProduct(productId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to delete product');
  }

  async updateOrderStatus(orderId: string, statusValue: number): Promise<OrderResponse> {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/status?status_value=${statusValue}`, {
      method: 'PATCH',
      headers: this.getHeaders(),
    });
    return this.parseResponse<OrderResponse>(response, 'Failed to update order status');
  }

  async getSalesSummary(): Promise<SalesSummary> {
    const response = await fetch(`${API_BASE_URL}/dashboard/sales`, { headers: this.getHeaders() });
    return this.parseResponse<SalesSummary>(response, 'Failed to fetch sales summary');
  }

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await fetch(`${API_BASE_URL}/dashboard/metrics`, { headers: this.getHeaders() });
    return this.parseResponse<DashboardMetrics>(response, 'Failed to fetch dashboard metrics');
  }

  /**
   * Spec: GET /product/search?name=…&attr=… — backend chưa có.
   * TODO(backend): thay bằng endpoint search thật; hiện lọc phía client từ getProducts.
   */
  async searchProducts(params: ProductSearchParams): Promise<BackendProduct[]> {
    const products = await this.getProducts(0, CATALOG_LIMIT);
    const q = params.q?.trim().toLowerCase();
    const matches = (value: string | null | undefined, expected?: string) =>
      !expected || (value ?? '').toLowerCase() === expected.toLowerCase();
    return products.filter((p) =>
      (!q || p.prod_name.toLowerCase().includes(q)) &&
      matches(p.index_group_name, params.index_group) &&
      matches(p.product_group_name, params.product_group) &&
      matches(p.colour_group_name, params.colour)
    );
  }

  /** Bán chạy tuần theo run pipeline H&M đang dùng; 404 khi chưa chạy pipeline. */
  async getBestSellers(limit = 5): Promise<BackendProduct[]> {
    const response = await fetch(`${API_BASE_URL}/products/best-sellers?limit=${limit}`, { headers: this.getHeaders() });
    return this.parseResponse<BackendProduct[]>(response, 'Failed to fetch best sellers');
  }

  /**
   * Bước Feedback sau mua. Spec: POST /order/evaluate — backend chưa có,
   * nên ghi điểm cho từng sản phẩm trong đơn qua /feedback. TODO(backend): lưu nhận xét.
   */
  async evaluateOrder(userId: string, order: OrderResponse, rank: number, _comment?: string): Promise<FeedbackResponse[]> {
    const productIds = Array.from(new Set(order.items.map((item) => item.product_id)));
    return Promise.all(productIds.map((productId) => this.createFeedback(userId, productId, rank)));
  }

  async triggerAITraining(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/ai/trigger-training`, { method: 'POST', headers: this.getHeaders() });
    return this.parseResponse<{ message: string }>(response, 'Failed to trigger training');
  }

  async getModelMetrics(): Promise<ModelMetrics> {
    const response = await fetch(`${API_BASE_URL}/ai/metrics/latest`, { headers: this.getHeaders() });
    return this.parseResponse<ModelMetrics>(response, 'Failed to fetch model metrics');
  }

  async getTrainingStatus(): Promise<TrainingStatus> {
    const response = await fetch(`${API_BASE_URL}/ai/training/status`, { headers: this.getHeaders() });
    return this.parseResponse<TrainingStatus>(response, 'Failed to fetch training status');
  }

  async saveTrainingConfig(config: TrainingConfig): Promise<TrainingConfig> {
    const response = await fetch(`${API_BASE_URL}/ai/training/config`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(config),
    });
    return this.parseResponse<TrainingConfig>(response, 'Failed to save training config');
  }

  /** Xử lý ngoại lệ: ghi đè bằng run kém baseline hay giữ bản cũ. */
  async resolveTrainingException(action: 'overwrite' | 'keep'): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/ai/training/resolve`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ action }),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to resolve training exception');
  }

  async getErrorAnalysis(): Promise<ErrorAnalysis> {
    const response = await fetch(`${API_BASE_URL}/ai/error-analysis`, { headers: this.getHeaders() });
    return this.parseResponse<ErrorAnalysis>(response, 'Failed to fetch error analysis');
  }

  async getInsights(): Promise<Insights> {
    const response = await fetch(`${API_BASE_URL}/ai/insights`, { headers: this.getHeaders() });
    return this.parseResponse<Insights>(response, 'Failed to fetch insights');
  }

  async getEdaReports(): Promise<EdaReports> {
    const response = await fetch(`${API_BASE_URL}/ai/reports/eda`, { headers: this.getHeaders() });
    return this.parseResponse<EdaReports>(response, 'Failed to fetch EDA reports');
  }

  /** user_id → customer_id (H&M) của tài khoản Buyer. Chỉ Admin. */
  async getCustomerLinks(): Promise<Record<string, string>> {
    const response = await fetch(`${API_BASE_URL}/ai/customer-links`, { headers: this.getHeaders() });
    return this.parseResponse<Record<string, string>>(response, 'Failed to fetch customer links');
  }

  /** Khối "Adjust n": ghi lại Recommendations với Top n mới. */
  async recomputeRecommendations(topN: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/ai/recommendations/recompute`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ top_n: topN }),
    });
    return this.parseResponse<{ message: string }>(response, 'Failed to recompute recommendations');
  }
}

export const apiService = new APIService();
