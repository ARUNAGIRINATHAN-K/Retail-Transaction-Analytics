# Basket Analysis with PySpark

This repository contains a PySpark implementation of basket analysis using the FP-Growth algorithm to identify frequently bought item combinations in retail transaction data. The project analyzes a dataset of ~10,000 transactions to uncover patterns like `{Diapers} → {Popcorn}` and category-level trends (e.g., `{Snacks, Beverages}`).

![Build Status](https://github.com/your_username/basket-analysis/actions/workflows/main.yml/badge.svg)
![Code Coverage](https://img.shields.io/badge/coverage-80%25-green)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![Repo Size](https://img.shields.io/github/repo-size/your_username/basket-analysis)
![Issues](https://img.shields.io/github/issues/your_username/basket-analysis)

## Overview

The project uses PySpark's MLlib to perform market basket analysis on retail data (`Retail_pos_basket_data.csv`). It identifies:
- **Frequent Itemsets**: Common product combinations (e.g., `{Spinach, Tissue}` with support 4.05%).
- **Association Rules**: Implications like `{Diapers} → {Popcorn}` (confidence 1.0, lift 12.33).
- **Category-Level Patterns**: Broader trends (e.g., `{Grains & Staples, Household}` with support 16.22%).

The code is scalable for large datasets and outputs results to CSV files for further analysis.

## Dataset

The dataset contains ~10,000 rows with columns:
- `order_id`: Unique transaction ID
- `product_name`: Product purchased (e.g., Milk, Bread)
- `category`: Product category (e.g., Dairy & Eggs, Bakery)
- `order_date`, `order_hour_of_day`, `user_id`: Additional metadata

A sample of 74 transactions was analyzed, revealing 47 itemsets and 35 rules at the item level, and 50 itemsets and 24 rules at the category level.

## Setup

### Prerequisites
- Python 3.6+
- PySpark (`pip install pyspark`)
- Java 8 or 11
- Dataset: `Retail_pos_basket_data.csv` (update path in code)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/basket-analysis.git
   cd basket-analysis
   ```
2. Install dependencies:
   ```bash
   pip install pyspark
   ```
3. Ensure Java is installed:
   ```bash
   java -version
   ```

## Usage

1. Place `Retail_pos_basket_data.csv` in the project directory or update the path in `basket_analysis_full.py`.
2. Run the script:
   ```bash
   spark-submit basket_analysis_full.py
   ```
3. Check outputs in:
   - `item_frequent_itemsets_output/`: Frequent product combinations
   - `item_association_rules_output/`: Product association rules
   - `category_frequent_itemsets_output/`: Frequent category combinations
   - `category_association_rules_output/`: Category association rules

## Example Output

### Item-Level (Top 5)
| Itemset                  | Support |
|--------------------------|---------|
| [Tissue]                 | 0.1216  |
| [Apple]                  | 0.0946  |
| [Chicken Breast]         | 0.0946  |
| [Tea]                    | 0.0946  |
| [Spinach, Tissue]        | 0.0405  |

| Rule                     | Confidence | Lift   |
|--------------------------|------------|--------|
| [Diapers] → [Popcorn]    | 1.0000     | 12.3333|
| [Coffee] → [Chocolate]   | 0.7500     | 7.9286 |
| [Pasta] → [Pastry]       | 0.6667     | 5.4815 |
| [Notebook] → [Baby Food] | 0.6667     | 8.2222 |
| [Diapers] → [Chocolate]  | 0.6667     | 7.0476 |

### Category-Level (Top 5)
| Category Itemset                  | Support |
|-----------------------------------|---------|
| [Grains & Staples]                | 0.3243  |
| [Fruits & Vegetables]             | 0.2973  |
| [Bakery]                          | 0.2432  |
| [Beverages]                       | 0.2297  |
| [Grains & Staples, Household]     | 0.1622  |

| Rule                              | Confidence | Lift   |
|-----------------------------------|------------|--------|
| [Stationery] → [Fruits & Vegetables] | 0.6250  | 2.1023 |
| [Snacks] → [Beverages]            | 0.5455     | 2.3747 |
| [Dairy & Eggs] → [Meat & Seafood] | 0.4286     | 2.2653 |
| [Snacks] → [Fruits & Vegetables]  | 0.4091     | 1.3758 |
| [Household] → [Grains & Staples]  | 0.3750     | 1.1562 |

## Business Applications
- **Product Placement**: Place Cookies near Chicken Breast or Spinach near Tissue.
- **Promotions**: Bundle Diapers with Popcorn or offer discounts on Chocolate with Coffee purchases.
- **Inventory**: Stock more Tissue, Apple, and Grains & Staples for high demand.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request. Check the [Issues](https://github.com/your_username/basket-analysis/issues) badge for open tasks.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.