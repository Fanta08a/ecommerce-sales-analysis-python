import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ==========================================
# 1. DATA LOADING
# ==========================================

df = pd.read_csv("data/ecommerce_sales_2025.csv")

print("\n===== DATA LOADING =====")
print(df.head(10))


# ==========================================
# 2. DATA EXPLORATION
# ==========================================

print("\n===== DATA EXPLORATION =====")

print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])

print("\nColumn names:")
print(df.columns)

print("\nData types:")
print(df.dtypes)

print("\nDescriptive statistics:")
print(df.describe())


# ==========================================
# 3. DATA QUALITY CHECK
# ==========================================

print("\n===== DATA QUALITY CHECK =====")

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nDuplicate order IDs:", df["order_id"].duplicated().sum())


# ==========================================
# 4. DATA VALIDATION & CLEANING
# ==========================================

print("\n===== DATA VALIDATION =====")

print("\nOrder statuses:")
print(df["order_status"].value_counts())

print("\nInvalid prices:")
print(df[df["unit_price_czk"] <= 0])

print("\nInvalid quantities:")
print(df[df["quantity"] <= 0])

print("\nInvalid costs:")
print(df[df["unit_cost_czk"] < 0])

print("\nInvalid discounts:")
print(
    df[
        (df["discount_pct"] < 0)
        | (df["discount_pct"] > 100)
    ]
)

# Convert order dates to datetime
df["order_date"] = pd.to_datetime(
    df["order_date"],
    errors="coerce"
)

print("\nInvalid dates:", df["order_date"].isna().sum())


# ==========================================
# 5. SALES ANALYSIS
# ==========================================

print("\n===== SALES ANALYSIS =====")

# 5.1 Completed orders

completed_orders = df[
    df["order_status"] == "Completed"
].copy()

completed_orders_count = completed_orders.shape[0]


# 5.2 Revenue after discounts

completed_orders["revenue_czk"] = (
    completed_orders["unit_price_czk"]
    * completed_orders["quantity"]
    * (1 - completed_orders["discount_pct"] / 100)
)


# 5.3 Total revenue

total_revenue = completed_orders["revenue_czk"].sum()


# 5.4 Average Order Value

average_order_value = (
    total_revenue / completed_orders_count
    if completed_orders_count > 0
    else 0
)


# 5.5 Total cost

completed_orders["total_cost_czk"] = (
    completed_orders["unit_cost_czk"]
    * completed_orders["quantity"]
)


# 5.6 Gross profit

completed_orders["gross_profit_czk"] = (
    completed_orders["revenue_czk"]
    - completed_orders["total_cost_czk"]
)

total_gross_profit = completed_orders["gross_profit_czk"].sum()


# 5.7 Gross profit margin

gross_profit_margin = (
    total_gross_profit / total_revenue * 100
    if total_revenue > 0
    else 0
)


# 5.8 Total units sold

total_units_sold = completed_orders["quantity"].sum()


# 5.9 Print KPIs

print("\n===== KEY PERFORMANCE INDICATORS =====")

print(f"Total Revenue: {total_revenue:,.2f} CZK")
print(f"Completed Orders: {completed_orders_count}")
print(f"Average Order Value: {average_order_value:,.2f} CZK")
print(f"Total Units Sold: {total_units_sold}")
print(f"Gross Profit: {total_gross_profit:,.2f} CZK")
print(f"Gross Profit Margin: {gross_profit_margin:.2f}%")


# ==========================================
# 5.10 REVENUE BY CATEGORY
# ==========================================

category_revenue = (
    completed_orders
    .groupby("category")["revenue_czk"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== REVENUE BY CATEGORY =====")
print(category_revenue)


# ==========================================
# 5.11 TOP 5 PRODUCTS
# ==========================================

top_products = (
    completed_orders
    .groupby("product")["revenue_czk"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

print("\n===== TOP 5 PRODUCTS =====")
print(top_products)


# ==========================================
# 5.12 REVENUE BY REGION
# ==========================================

region_revenue = (
    completed_orders
    .groupby("region")["revenue_czk"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== REVENUE BY REGION =====")
print(region_revenue)


# ==========================================
# 5.13 SALES CHANNEL PERFORMANCE
# ==========================================

channel_performance = (
    completed_orders
    .groupby("sales_channel")
    .agg(
        total_revenue=("revenue_czk", "sum"),
        total_orders=("order_id", "count"),
        gross_profit=("gross_profit_czk", "sum")
    )
)

channel_performance["aov"] = (
    channel_performance["total_revenue"]
    / channel_performance["total_orders"]
)

channel_performance = channel_performance.sort_values(
    by="total_revenue",
    ascending=False
)

print("\n===== SALES CHANNEL PERFORMANCE =====")
print(channel_performance.round(2))


# ==========================================
# 5.14 MONTHLY REVENUE
# ==========================================

completed_orders["month"] = (
    completed_orders["order_date"].dt.month
)

monthly_revenue = (
    completed_orders
    .groupby("month")["revenue_czk"]
    .sum()
    .reindex(range(1, 13), fill_value=0)
)

print("\n===== MONTHLY REVENUE =====")
print(monthly_revenue)

best_month = monthly_revenue.idxmax()

print("\nBest Month:", best_month)
print("Best Month Revenue:", round(monthly_revenue.max(), 2))


# ==========================================
# 5.15 ORDER STATUS ANALYSIS
# ==========================================

status_counts = df["order_status"].value_counts()

total_orders = len(df)

completed_rate = (
    status_counts.get("Completed", 0) / total_orders * 100
)

cancelled_rate = (
    status_counts.get("Cancelled", 0) / total_orders * 100
)

returned_rate = (
    status_counts.get("Returned", 0) / total_orders * 100
)

print("\n===== ORDER STATUS ANALYSIS =====")

print(f"Completed Rate: {completed_rate:.2f}%")
print(f"Cancellation Rate: {cancelled_rate:.2f}%")
print(f"Return Rate: {returned_rate:.2f}%")


# ==========================================
# 6. DATA VISUALIZATION
# ==========================================

print("\n===== CREATING CHARTS =====")

# Create charts folder
os.makedirs("../data/charts", exist_ok=True)


# ==========================================
# CHART 1. MONTHLY REVENUE
# ==========================================

plt.figure(figsize=(10, 6))

plt.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o",
    linewidth=2,
    color="blue"
)

plt.title("Monthly Revenue Trend - 2025")
plt.xlabel("Month")
plt.ylabel("Revenue (CZK)")

plt.xticks(range(1, 13))
plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.savefig(
    "charts/monthly_revenue.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# CHART 2. REVENUE BY CATEGORY
# ==========================================

plt.figure(figsize=(10, 6))

category_revenue.sort_values().plot(
    kind="barh",
    color="green"
)

plt.title("Revenue by Product Category")
plt.xlabel("Revenue (CZK)")
plt.ylabel("Category")

plt.tight_layout()

plt.savefig(
    "charts/category_revenue.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# CHART 3. TOP 5 PRODUCTS
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    top_products.index,
    top_products.values,
    color="orange"
)

plt.title("Top 5 Products by Revenue")
plt.xlabel("Product")
plt.ylabel("Revenue (CZK)")

plt.xticks(rotation=30, ha="right")

plt.tight_layout()

plt.savefig(
    "charts/top_products.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# CHART 4. SALES CHANNELS
# ==========================================

plt.figure(figsize=(8, 8))

plt.pie(
    channel_performance["total_revenue"],
    labels=channel_performance.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Revenue Share by Sales Channel")

plt.tight_layout()

plt.savefig(
    "charts/sales_channels.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# CHART 5. ORDER VALUE DISTRIBUTION
# ==========================================

plt.figure(figsize=(10, 6))

plt.hist(
    completed_orders["revenue_czk"],
    bins=15,
    color="purple",
    edgecolor="black",
    alpha=0.7
)

plt.title("Order Value Distribution")
plt.xlabel("Order Value (CZK)")
plt.ylabel("Frequency")

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    "charts/order_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ==========================================
# 7. KEY INSIGHTS
# ==========================================

print("\n===== KEY BUSINESS INSIGHTS =====")

print(
    f"1. Total revenue from completed orders "
    f"was {total_revenue:,.2f} CZK."
)

print(
    f"2. The highest revenue category was "
    f"{category_revenue.idxmax()}."
)

print(
    f"3. The best-selling product by revenue "
    f"was {top_products.idxmax()}."
)

print(
    f"4. The strongest sales channel was "
    f"{channel_performance.index[0]}."
)

print(
    f"5. The gross profit margin "
    f"was {gross_profit_margin:.2f}%."
)

print(
    f"6. The cancellation rate "
    f"was {cancelled_rate:.2f}%."
)

print("\nAnalysis completed successfully!")