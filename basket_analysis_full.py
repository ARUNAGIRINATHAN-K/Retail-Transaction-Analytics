# %%
# =========================
# Retail Basket Analysis (PySpark)
# End-to-end pipeline: load → clean → baskets → FPGrowth → rules → recs → export
# =========================

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T



# %%

# ---------- Parameters (tune here) ----------
INPUT_PATH = "Data/Retail_pos_basket_data.csv.csv"
OUTPUT_DIR = "/content/ouput"   # will be created if not exists

# %%

# Keep items that appear at least this many times before mining
MIN_ITEM_FREQ = 10                         # raise/lower based on dataset size

# %%
# If you prefer absolute min-support (e.g., 0.02 means 2% of baskets), leave as number in (0,1].
# If you prefer absolute count, set MIN_SUPPORT_ABS > 1 and we'll convert to relative later.
MIN_SUPPORT_REL = 0.02
MIN_SUPPORT_ABS = None                     # e.g., 50 (overrides MIN_SUPPORT_REL if set)

MIN_CONFIDENCE = 0.3
TOP_K_RULES = 200                          # for quick inspection/exports


# %%

# ---------- Start Spark ----------
spark = SparkSession.builder.appName("Retail Basket Analysis - PySpark").getOrCreate()
spark.sparkContext.setLogLevel("WARN")


# %%

# ---------- Load ----------
df_raw = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)


# %%

# Make column names uniform
df = df_raw.select([F.col(c).alias(c.strip().lower()) for c in df_raw.columns])


# %%

# Try to auto-detect transaction and item columns
txn_candidates = ["transactionid","transaction_id","invoice","invoice_no","bill_no",
                  "order_id","orderid","basket_id","txn_id","receipt_id","sale_id","ticket_no","trans_id"]
item_candidates = ["item","item_name","product","product_name","sku","description","prod","name"]

def pick_col(candidates, cols):
    s = set(cols)
    for c in candidates:
        if c in s:
            return c
    return None

txn_col = pick_col(txn_candidates, df.columns)
item_col = pick_col(item_candidates, df.columns)

if txn_col is None or item_col is None:
    raise ValueError(f"Could not auto-detect required columns. "
                     f"Found columns: {df.columns}. "
                     f"Please rename your transaction column to one of {txn_candidates} "
                     f"and item column to one of {item_candidates}.")


# %%

# Optional helpers (if present)
qty_col = pick_col(["quantity","qty","count"], df.columns)
price_col = pick_col(["price","amount","unit_price","mrp","rate"], df.columns)
cat_col = pick_col(["category","product_category","cat"], df.columns)
brand_col = pick_col(["brand"], df.columns)

# %%


# ---------- Clean items ----------
# Normalize item strings: trim, lower, collapse spaces
norm = F.udf(lambda s: " ".join(s.strip().split()).lower() if s is not None else None, T.StringType())

df_clean = (
    df
    .withColumn(item_col, norm(F.col(item_col).cast("string")))
    .withColumn(txn_col, F.col(txn_col).cast("string"))
    .filter(F.col(item_col).isNotNull() & (F.length(F.col(item_col)) > 0))
    .filter(F.col(txn_col).isNotNull() & (F.length(F.col(txn_col)) > 0))
)


# %%

# ---------- Optional: drop obvious noise like "na", "misc", etc. ----------
noise = ["na","n/a","none","misc","unknown"]
df_clean = df_clean.filter(~F.col(item_col).isin(noise))


# %%

# ---------- Filter very rare items to reduce noise & speed up ----------
item_freq = (
    df_clean.groupBy(item_col)
            .agg(F.countDistinct(txn_col).alias("txn_count"))
)

df_items_kept = item_freq.filter(F.col("txn_count") >= F.lit(MIN_ITEM_FREQ))
df_clean = df_clean.join(df_items_kept.select(item_col), on=item_col, how="inner")


# %%

# ---------- Build baskets (set not list to avoid duplicates in same txn) ----------
baskets = (
    df_clean.groupBy(txn_col)
            .agg(F.collect_set(F.col(item_col)).alias("items"))
            .filter(F.size(F.col("items")) >= 2)  # baskets of at least 2 items
)

num_txns = baskets.count()
print(f"Total baskets: {num_txns}")


# %%

# ---------- Compute minSupport ----------
if MIN_SUPPORT_ABS is not None and MIN_SUPPORT_ABS > 1:
    min_support = float(MIN_SUPPORT_ABS) / max(1, num_txns)
else:
    min_support = float(MIN_SUPPORT_REL)

print(f"Using minSupport={min_support:.5f}, minConfidence={MIN_CONFIDENCE}")


# %%

# ---------- Mine frequent itemsets & rules via FPGrowth ----------
from pyspark.ml.fpm import FPGrowth

fp = FPGrowth(itemsCol="items", minSupport=min_support, minConfidence=MIN_CONFIDENCE)
model = fp.fit(baskets)

freq_itemsets = model.freqItemsets  # columns: items (array<string>), freq (long)
rules = model.associationRules      # columns: antecedent, consequent, confidence, lift


# %%

# ---------- Post-process rules ----------
rules_enh = (
    rules
    .withColumn("ante_len", F.size("antecedent"))
    .withColumn("cons_len", F.size("consequent"))
    .withColumn("rule_str",
        F.concat(F.array_join(F.col("antecedent"), ", "),
                 F.lit(" -> "),
                 F.array_join(F.col("consequent"), ", "))
    )
    .orderBy(F.col("lift").desc(), F.col("confidence").desc())
)


# %%

# Stronger rule slice for business (tune thresholds if needed)
rules_strong = rules_enh.filter(
    (F.col("confidence") >= F.lit(MIN_CONFIDENCE)) & (F.col("lift") > 1.0)
)


# %%

# ---------- Item → item top-N recommendations ----------
# explode antecedent to get "seed item" → recommended consequents
exploded = (
    rules_strong
    .withColumn("seed", F.explode("antecedent"))
    .withColumn("rec", F.explode("consequent"))
    .select("seed","rec","confidence","lift")
)


# %%
# Rank recs per seed item
# window = F.window.partitionBy("seed").orderBy(F.col("lift").desc(), F.col("confidence").desc())
# Note: Spark SQL Window is in pyspark.sql.window.Window (not F.window)
from pyspark.sql.window import Window
win = Window.partitionBy("seed").orderBy(F.col("lift").desc(), F.col("confidence").desc())

item_recs = (
    exploded
    .withColumn("rank", F.row_number().over(win))
    .filter(F.col("rank") <= 5)  # top-5 per item
    .orderBy("seed","rank")
)

# %%

# ---------- Quick KPIs ----------
total_items = df_items_kept.count()
total_rules = rules.count()
strong_rules_cnt = rules_strong.count()

print(f"Kept items >= {MIN_ITEM_FREQ} txn: {total_items}")
print(f"All rules: {total_rules}")
print(f"Strong rules (conf>={MIN_CONFIDENCE}, lift>1): {strong_rules_cnt}")


# %%
# ---------- Save outputs ----------

# Order freq_itemsets BEFORE converting array column to string
freq_itemsets_ordered = (
    freq_itemsets
    .orderBy(F.size("items").desc(), F.col("freq").desc())
    .limit(5000)
)

# Convert array columns to strings before writing to CSV
freq_itemsets_csv = freq_itemsets_ordered.withColumn("items", F.array_join("items", ", "))
rules_enh_csv = rules_enh.withColumn("antecedent", F.array_join("antecedent", ", ")).withColumn("consequent", F.array_join("consequent", ", "))
rules_strong_csv = rules_strong.withColumn("antecedent", F.array_join("antecedent", ", ")).withColumn("consequent", F.array_join("consequent", ", "))
item_recs_csv = item_recs # item_recs doesn't have array columns

(
    freq_itemsets_csv
    .coalesce(1)
    .write.mode("overwrite").option("header", True)
    .csv(f"{OUTPUT_DIR}/freq_itemsets")
)

(
    rules_enh_csv
    .limit(TOP_K_RULES)
    .coalesce(1)
    .write.mode("overwrite").option("header", True)
    .csv(f"{OUTPUT_DIR}/association_rules_top")
)

(
    rules_strong_csv
    .limit(TOP_K_RULES)
    .coalesce(1)
    .write.mode("overwrite").option("header", True)
    .csv(f"{OUTPUT_DIR}/association_rules_strong_top")
)

# The item_recs DataFrame does not contain array columns, so it can be written directly
(
    item_recs_csv
    .coalesce(1)
    .write.mode("overwrite").option("header", True)
    .csv(f"{OUTPUT_DIR}/item_recommendations_top5")
)

# %%

# ---------- Optional: quick inspection in console ----------
print("\n=== Top frequent itemsets ===")
freq_itemsets.orderBy(F.col("freq").desc()).show(15, truncate=False)

print("\n=== Top rules by lift/confidence ===")
rules_enh.select("rule_str","confidence","lift").show(15, truncate=False)

print("\n=== Item → Top-5 recommendations (by lift/conf) ===")
item_recs.show(30, truncate=False)

# ---------- (Optional) Coverage of prediction on known baskets ----------
predicted = model.transform(baskets)  # adds "prediction" column
coverage = predicted.filter(F.size("prediction") > 0).count() / float(num_txns) if num_txns else 0.0
print(f"\nPrediction coverage on historical baskets: {coverage:.2%}")

print(f"\n✅ Done. Outputs written under: {OUTPUT_DIR}")

# spark.stop()  # uncomment if you want Spark to close here


