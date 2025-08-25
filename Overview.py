# %% [markdown]
# Exploratory Data Analysis (EDA) summary

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %%
df = pd.read_csv("Data/Retail_pos_basket_data.csv.csv", parse_dates=["order_date"])

# %% [markdown]
# Data Overview

# %%
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing Values:\n", df.isnull().sum())
print("\nUnique Products:", df['product_name'].nunique())
print("Unique Categories:", df['category'].nunique())
print("Unique Customers:", df['user_id'].nunique())

# %% [markdown]
# Sales Column

# %%
df["sales"] = df["quantity"] * df["price"]

# %% [markdown]
# Sales Overview

# %%
print("\nTotal Revenue:", df["sales"].sum())
print("Average Basket Size:", df.groupby("order_id")["product_id"].count().mean())

# %% [markdown]
# Top Products

# %%
top_products = df.groupby("product_name")["sales"].sum().sort_values(ascending=False).head(10)
print("\nTop Products:\n", top_products)

# %% [markdown]
# Top Customers

# %%
top_customers = df.groupby("user_id")["sales"].sum().sort_values(ascending=False).head(10)
print("\nTop Customers:\n", top_customers)

# %% [markdown]
# Category-Level Analysis

# %%
plt.figure(figsize=(10,6))
sns.barplot(x=df["category"].value_counts().index, y=df["category"].value_counts().values)
plt.xticks(rotation=45)
plt.title("Number of Items Sold per Category")
plt.show()

# %% [markdown]
# Time-Based Analysis

# %% [markdown]
# By Month

# %%
df["month"] = df["order_date"].dt.month
plt.figure(figsize=(10,6))
sns.lineplot(x="month", y="sales", data=df.groupby("month")["sales"].sum().reset_index(), marker="o")
plt.title("Monthly Sales Trend (2023)")
plt.show()

# %% [markdown]
# By Hour

# %%
plt.figure(figsize=(10,6))
sns.barplot(x="order_hour_of_day", y="sales", data=df.groupby("order_hour_of_day")["sales"].sum().reset_index())
plt.title("Sales by Hour of Day")
plt.show()


# %% [markdown]
# Price & Quantity Distribution

# %%
plt.figure(figsize=(10,6))
sns.histplot(df["price"], bins=30, kde=True)
plt.title("Distribution of Product Prices")
plt.show()

# %%

plt.figure(figsize=(10,6))
sns.histplot(df["quantity"], bins=20, kde=False)
plt.title("Distribution of Quantity per Transaction")
plt.show()

# %% [markdown]
# Customer Behavior

# %%
cust_orders = df.groupby("user_id")["order_id"].nunique()
plt.figure(figsize=(10,6))
sns.histplot(cust_orders, bins=30, kde=False)
plt.title("Customer Purchase Frequency (Number of Orders per Customer)")
plt.show()

# %%
from itertools import combinations
from collections import Counter

basket_df = df.groupby("order_id")["product_name"].apply(list)
pairs = Counter()

for items in basket_df:
    for combo in combinations(set(items), 2):
        pairs[combo] += 1

print("\nTop Product Pairs (Co-occurrence):")
print(pairs.most_common(10))


