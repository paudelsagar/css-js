# 📊 pyreport

**pyreport** is a modular Python library for generating structured, interactive, and presentation-ready **data reports** — seamlessly combining **Altair charts**, **Plotly figures**, and **pandas DataFrames** in a **grid-based HTML layout**.

Ideal for data scientists and analysts, `pyreport` helps you explore, visualize, and share your data through a clean HTML interface — all with just a few lines of code.



**👨‍💻 Author:** Sagar Paudel | Lead Data Scientist | [sagar-paudel.com.np](https://sagar-paudel.com.np/) 



## ✨ Features

- 🧱 **Grid-Based Layout**
   Automatically organizes charts and tables into a responsive card-based grid layout for a clean, report-style structure.
- 📈 **Altair + Plotly Integration**
   Combine the beauty of **Altair** with the interactivity of **Plotly** — all within the same report.
- 📋 **Tabular Output**
   Display any `pandas.DataFrame` as a styled, scrollable table.
- 🧾 **HTML Report Generation**
   Export your complete analysis as a standalone HTML file — perfect for sharing or presenting.
- 🌐 **Built-in Server**
   Spin up a local web server and **host your report** instantly via browser for easy review or collaboration.



## 📦 Installation

```bash
report_py_url = "https://raw.githubusercontent.com/paudelsagar/pyreport/refs/heads/main/report.py"
response = requests.get(report_py_url)
exec(response.text)
```



## 🚀 Quick Start

```python
import pandas as pd
import plotly.express as px

title = "IPL 2008-2023 EDA"
author = "Sagar Paudel"
data_source = "Kaggle"
objective = "To perform exploratory data analysis."

# Initialize Report
report = Report(title, author, data_source, objective)

# Add Section
report.add_section("Dataset Overview")

# Read your dataset
df = pd.read_csv("your_data.csv")

# Add dataframe into report
report.add_dataframe(df, title="📄 Preview of DataFrame", max_rows=20)

# Add plotly figure
fig = px.scatter(df, x="feature1", y="feature2")
report.add_plotly_figure(fig)
```
