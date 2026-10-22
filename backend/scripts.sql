-- Schema PostgreSQL sinh tự động từ backend/models — KHÔNG sửa tay.
-- Sinh lại:  cd backend && python scripts/dump_schema.py
-- Backend tự tạo bảng (Base.metadata.create_all) khi khởi động; file này để tham khảo / dựng DB bằng tay.

CREATE TYPE role AS ENUM ('SELLER', 'BUYER', 'ADMIN', 'DATA_SCIENTIST');
CREATE TYPE interactiontype AS ENUM ('VIEWED', 'ADDED_TO_CART', 'REMOVED_FROM_CART', 'ADDED_TO_WISHLIST', 'REMOVED_FROM_WISHLIST', 'PURCHASED');
CREATE TYPE orderstatus AS ENUM ('PENDING', 'DELIVERING', 'COMPLETED', 'CANCELLED');

CREATE TABLE model_versions (
	id UUID NOT NULL, 
	version_tag VARCHAR(50) NOT NULL, 
	image_feat_path VARCHAR(500), 
	text_feat_path VARCHAR(500), 
	meta_feat_path VARCHAR(500), 
	gnn_emb_path VARCHAR(500), 
	model_weights_path VARCHAR(500), 
	is_active BOOLEAN, 
	product_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (version_tag)
);

CREATE TABLE products (
	id UUID NOT NULL, 
	article_id VARCHAR(10), 
	product_code VARCHAR(7), 
	prod_name VARCHAR(255) NOT NULL, 
	product_type_name VARCHAR(100), 
	product_group_name VARCHAR(100), 
	colour_group_name VARCHAR(100), 
	graphical_appearance_name VARCHAR(100), 
	index_group_name VARCHAR(100), 
	detail_desc TEXT, 
	price FLOAT NOT NULL, 
	image_url VARCHAR(500), 
	sales_last_week INTEGER DEFAULT '0' NOT NULL, 
	quantity_in_stock INTEGER DEFAULT '0' NOT NULL, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_products_article_id ON products (article_id);
CREATE INDEX ix_products_index_group_name ON products (index_group_name);
CREATE INDEX ix_products_product_code ON products (product_code);
CREATE INDEX ix_products_product_group_name ON products (product_group_name);

CREATE TABLE users (
	id UUID NOT NULL, 
	role_id role NOT NULL, 
	username VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	gender VARCHAR(50), 
	age INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);

CREATE TABLE carts (
	id SERIAL NOT NULL, 
	user_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	quantity INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	CONSTRAINT _user_product_cart_uc UNIQUE (user_id, product_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE eda_reports (
	id UUID NOT NULL, 
	eda_type VARCHAR(20), 
	version_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	report_files JSONB, 
	PRIMARY KEY (id), 
	FOREIGN KEY(version_id) REFERENCES model_versions (id)
);

CREATE TABLE feedbacks (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	rank INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(product_id) REFERENCES products (id)
);

CREATE TABLE interactions (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	interaction_type interactiontype NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE orders (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	order_date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
	status orderstatus NOT NULL, 
	total_amount FLOAT NOT NULL, 
	note TEXT, 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE user_customer_links (
	user_id UUID NOT NULL, 
	customer_id VARCHAR(64) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	UNIQUE (customer_id)
);

CREATE TABLE user_recommendations (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	score FLOAT NOT NULL, 
	rank INTEGER NOT NULL, 
	version_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(product_id) REFERENCES products (id), 
	FOREIGN KEY(version_id) REFERENCES model_versions (id)
);

CREATE TABLE wishlists (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	CONSTRAINT _user_product_wishlist_uc UNIQUE (user_id, product_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE TABLE order_items (
	id SERIAL NOT NULL, 
	order_id UUID NOT NULL, 
	product_id UUID NOT NULL, 
	quantity INTEGER NOT NULL, 
	unit_price FLOAT NOT NULL, 
	subtotal FLOAT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT
);
