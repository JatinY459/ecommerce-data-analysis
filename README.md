# 🛒 E-Commerce Exploratory Data Analysis & Interactive Dashboard

This project explores a large real-world e-commerce dataset through a full data analytics pipeline — from data understanding and cleaning to extracting insights via exploratory data analysis (EDA).

---


## 📌 Project Highlights

- ✅ **Real-world E-Commerce Dataset** (Brazil) with 5 interconnected CSV files
- 📊 **Exploratory Data Analysis** with Pandas, Matplotlib & Seaborn
- 🔍 Extracted deep insights across orders, customers, sellers, payments & delivery
- 📈 **Interactive Dashboard** built with Streamlit for dynamic data exploration
- 🧠 Business-focused conclusions & recommendations drawn from analytics

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
│   ├── 03_eda.ipynb
|   └──...
├── Dashboard_Homepage.py
├── visuals/
├── scripts/ # utility python scripts
├── pages/
|   ├── 01_Orders_And_Delivery_Trends.py
|   ├── 02_Customer_Geography_and_Behavior.py
|   └── ...
└── README.md
```


📊 Dashboard Pages (Streamlit)
- Home: Project summary, key metrics, and navigation
- Orders & Delivery Trends: Analyze order status, delays, regional trends, and delivery durations
- Customer Geography & Behavior: Distribution by state/city and repeat purchase patterns
- Products & Categories: Category breakdown, weights/volumes, and listing patterns
- Payments & Shipping: Preferred payment methods, shipping costs and trends
- Seller Activity: Seller distribution, top performers, and product-seller networks


🧪 Tools & Technologies Used
- Python (Pandas, Numpy)
- Visualization: Matplotlib, Seaborn, Plotly 
- Web App (Dashboard): Streamlit
- Data Handling: Jupyter Notebook
- Project Management: Git + GitHub

✅ How to Run the Dashboard Locally
- Clone the Repository
  -```bash git clone https://github.com/your-username/ecommerce-analysis.git cd ecommerce-analysis/dashboard```

- Install Dependencies
  -```bash pip install -r requirements.txt```

- Launch Streamlit App
  -```bash streamlit run Home.py```

## 📌 Notes

This is a learning project done as a deep-dive into a structured data analytics workflow. It focuses on clarity, reasoning, and explainability over flashy visuals or automation.

## 🙋‍♂️ Author

### Jatin Yadav

Computer Science Engineering Student & aspiring data analyst <br>
[LinkedIn](https://www.linkedin.com/in/jatinyadav459/) | [GitHub](https://github.com/JatinY459/)
