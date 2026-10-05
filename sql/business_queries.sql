/*
============================================================
E-Commerce Sales Analysis
SQL Business Analysis
============================================================

Purpose:
Analyse sales performance, customer behaviour, geographic
distribution, delivery performance, and customer satisfaction
using the processed Olist e-commerce dataset.

Database: SQLite
============================================================
*/


-- ==========================================================
-- 1. OVERALL BUSINESS PERFORMANCE
-- ==========================================================

-- 1.1 Total delivered orders
SELECT
    COUNT(*) AS delivered_orders
FROM orders
WHERE order_status = 'delivered';


-- 1.2 Total product sales from delivered orders
SELECT
    ROUND(SUM(oi.price), 2) AS total_product_sales
FROM order_items AS oi
JOIN orders AS o
    ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered';


-- 1.3 Average order value
-- First calculate product sales per order, then average them.
WITH order_sales AS (
    SELECT
        oi.order_id,
        SUM(oi.price) AS order_value
    FROM order_items AS oi
    JOIN orders AS o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.order_id
)
SELECT
    ROUND(AVG(order_value), 2) AS average_order_value
FROM order_sales;


-- ==========================================================
-- 2. SALES TREND
-- ==========================================================

-- Monthly product sales and delivered orders
SELECT
    strftime('%Y-%m', o.order_purchase_timestamp) AS month,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.price), 2) AS product_sales
FROM orders AS o
JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;


-- ==========================================================
-- 3. PRODUCT PERFORMANCE
-- ==========================================================

-- Top 10 categories by product sales
SELECT
    p.product_category_name_english AS category,
    COUNT(*) AS items_sold,
    ROUND(AVG(oi.price), 2) AS average_item_price,
    ROUND(SUM(oi.price), 2) AS product_sales
FROM order_items AS oi
JOIN orders AS o
    ON oi.order_id = o.order_id
JOIN products AS p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY p.product_category_name_english
ORDER BY product_sales DESC
LIMIT 10;


-- ==========================================================
-- 4. GEOGRAPHIC PERFORMANCE
-- ==========================================================

-- Delivered orders by customer state
SELECT
    c.customer_state,
    COUNT(*) AS delivered_orders
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY delivered_orders DESC;


-- Product sales by customer state
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS delivered_orders,
    ROUND(SUM(oi.price), 2) AS product_sales
FROM orders AS o
JOIN customers AS c
    ON o.customer_id = c.customer_id
JOIN order_items AS oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY product_sales DESC;


-- ==========================================================
-- 5. CUSTOMER BEHAVIOUR
-- ==========================================================

-- Repeat customer rate
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(*) AS order_count
    FROM orders AS o
    JOIN customers AS c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT
    COUNT(*) AS customers,
    SUM(
        CASE
            WHEN order_count > 1 THEN 1
            ELSE 0
        END
    ) AS repeat_customers,
    ROUND(
        100.0 * SUM(
            CASE
                WHEN order_count > 1 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS repeat_customer_rate_pct
FROM customer_orders;


-- ==========================================================
-- 6. DELIVERY PERFORMANCE
-- ==========================================================

-- Overall delivery KPIs
SELECT
    COUNT(*) AS delivered_orders_with_delivery_date,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    SUM(is_late_delivery) AS late_deliveries,
    ROUND(
        100.0 * SUM(is_late_delivery) / COUNT(*),
        2
    ) AS late_delivery_rate_pct
FROM orders
WHERE order_status = 'delivered'
  AND delivery_days IS NOT NULL;


-- Categories with the highest late-delivery rate
-- Minimum 100 delivered orders to avoid tiny categories
-- dominating the ranking.
SELECT
    p.product_category_name_english AS category,
    COUNT(DISTINCT o.order_id) AS delivered_orders,
    COUNT(
        DISTINCT CASE
            WHEN o.is_late_delivery = 1
            THEN o.order_id
        END
    ) AS late_orders,
    ROUND(
        100.0
        * COUNT(
            DISTINCT CASE
                WHEN o.is_late_delivery = 1
                THEN o.order_id
            END
        )
        / COUNT(DISTINCT o.order_id),
        2
    ) AS late_delivery_rate_pct
FROM orders AS o
JOIN order_items AS oi
    ON o.order_id = oi.order_id
JOIN products AS p
    ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
  AND o.delivery_days IS NOT NULL
GROUP BY p.product_category_name_english
HAVING COUNT(DISTINCT o.order_id) >= 100
ORDER BY late_delivery_rate_pct DESC;


-- ==========================================================
-- 7. DELIVERY EXPERIENCE VS CUSTOMER REVIEWS
-- ==========================================================

-- Compare review scores for on-time vs late deliveries.
-- Reviews are aggregated to order level first to avoid
-- duplicating orders with multiple review records.
WITH order_reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS review_score
    FROM reviews
    GROUP BY order_id
)
SELECT
    CASE
        WHEN o.is_late_delivery = 1
            THEN 'Late'
        ELSE 'On time'
    END AS delivery_status,
    COUNT(*) AS orders,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM orders AS o
JOIN order_reviews AS r
    ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.delivery_days IS NOT NULL
GROUP BY delivery_status
ORDER BY avg_review_score DESC;