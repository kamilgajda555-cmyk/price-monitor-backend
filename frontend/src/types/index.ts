export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  sku?: string;
  ean?: string;
  category?: string;
  brand?: string;
  description?: string;
  base_price?: number;
  image_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductWithPrices extends Product {
  current_prices: CurrentPrice[];
  price_trend?: string;
  min_price?: number;
  max_price?: number;
  avg_price?: number;
}

export interface CurrentPrice {
  source_id: number;
  source_name: string;
  price: number;
  checked_at: string;
}

export interface Source {
  id: number;
  name: string;
  type?: string;
  base_url?: string;
  is_active: boolean;
  scraper_config?: any;
  created_at: string;
}

export interface ProductSource {
  id: number;
  product_id: number;
  source_id: number;
  source_url: string;
  source_product_id?: string;
  selector_config?: any;
  is_active: boolean;
  last_checked?: string;
  last_price?: number;
  created_at: string;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  source_id: number;
  source_name?: string;
  price: number;
  currency: string;
  availability: boolean;
  checked_at: string;
}

export interface Alert {
  id: number;
  user_id: number;
  product_id?: number;
  alert_type: string;
  condition: any;
  is_active: boolean;
  last_triggered?: string;
  created_at: string;
}

export interface DashboardStats {
  total_products: number;
  active_products: number;
  total_sources: number;
  active_sources: number;
  total_price_checks_today: number;
  products_with_price_drop: number;
  products_with_price_increase: number;
  average_price_change: number;
}

export interface PriceAlert {
  product_id: number;
  product_name: string;
  source_name: string;
  old_price: number;
  new_price: number;
  change_percent: number;
  checked_at: string;
}
