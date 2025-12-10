import streamlit as st
import pandas as pd
from pyspark.sql import SparkSession

# Re-create Spark session inside Streamlit (or pass data)
spark = SparkSession.builder.appName("Dashboard").getOrCreate()

# Load pre-computed results (these files must exist from a previous step)
freq_df = spark.read.parquet("freq_itemsets.parquet").toPandas()
rules_df = spark.read.parquet("rules.parquet").toPandas()

st.title("🛒 Retail Transaction & Basket Analysis Dashboard")

tab1, tab2, tab3 = st.tabs(["Sales Overview", "Frequent Itemsets", "Association Rules"])

with tab1:
    st.header("Top Selling Products")
    # Add your sales charts here
    st.bar_chart(freq_df.head(20).set_index("items")["freq"])

with tab2:
    st.header("Top Frequent Itemsets")
    st.dataframe(freq_df.head(50), width='stretch')

with tab3:
    st.header("Strongest Association Rules")
    st.dataframe(rules_df.sort_values("confidence", ascending=False).head(50),
                 width='stretch')
    st.write("Example: If someone buys X → likely to buy Y")
