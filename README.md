# 🛒 E-Commerce Sales Data Analysis

This project explores a large real-world e-commerce dataset through a full data analytics pipeline — from data understanding and cleaning to extracting insights via exploratory data analysis (EDA).

---

## 📂 Dataset Overview

The dataset contains anonymized customer orders made at a large e-commerce platform over several months. It includes 5 interlinked CSV files:

- `orders.csv` – Purchase to delivery timeline of orders
- `order_items.csv` – Product-level details per order
- `products.csv` – Product metadata (dimensions, category, weight)
- `customers.csv` – Customer ZIP code, city, and state
- `payments.csv` – Payment method, installments, and values

---

## 🔍 Project Structure

```bash
├── data/
│   ├── raw/           # Original unprocessed CSVs
│   └── processed/     # Cleaned and filtered files
├── notebooks/
│   ├── 01_data_overview.ipynb
│   ├── 02_data_cleaning.ipynb
│   └── 03_eda.ipynb
├── visuals/           # Plots and diagrams (optional)
└── README.md

## ✨ Objectives
- Clean and preprocess messy, inconsistent, and duplicated data entries
- Derive insights on order timelines, product pricing, delivery gaps, and payment behavior
- Identify outliers, trends, and meaningful relationships through visual exploration

## 🛠️ Tools & Libraries
- Python (pandas, matplotlib, seaborn, numpy)
- Jupyter Notebooks
- Optional: Streamlit for future interactive dashboards

✅ Current Status
- ✅ Data cleaning completed across all five files
- ✅ Outliers handled and inconsistencies resolved
- 🔜 EDA in progress
- 🔜 Insight summary and storytelling

## 📌 Notes
This is a learning project done as a deep-dive into a structured data analytics workflow. It focuses on clarity, reasoning, and explainability over flashy visuals or automation.

## 🙋‍♂️ Author
<strong style='font-size: 2rem; font-weight: 700'>Jatin Yadav</strong>
Computer Science Engineering Student & aspiring data analyst
LinkedIn[https://www.linkedin.com/in/jatinyadav459/] | GitHub[https://github.com/JatinY459/]
```
