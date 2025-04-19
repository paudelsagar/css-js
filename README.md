# PyReport

**PyReport** is a powerful and flexible Python library designed to simplify the generation of automated, visually-rich, and fully customizable HTML reports. Built with data scientists, analysts, and developers in mind, PyReport enables the rapid creation of professional and interactive exploratory data analysis (EDA) reports. It seamlessly integrates with pandas, Plotly, Altair, and offers a clean, responsive layout inspired by Bootstrap.


## 🚀 Features

- 📊 **Chart Integration**: Incorporates Plotly and Altair for generating dynamic and responsive visualizations.
- 🧱 **Grid Layout System**: Offers a responsive grid-based system to structure rows, columns, and cards effortlessly.
- 🗃️ **Hierarchical Sectioning**: Organize content with customizable section headers, each supporting icons and nesting levels.
- 📋 **Styled DataFrames**: Display pandas DataFrames in beautifully styled, scrollable tables.
- 📈 **Supported Plot Types**:
  - Histograms (Plotly & Altair)
  - Box plots (Plotly & Altair)
  - Violin plots (Plotly)
  - Density/KDE plots (Altair)
  - Pair plots (Altair)
  - Correlation heatmaps (upcoming)
- 🧠 **Smart Plot Controls**: Flexible plotting interface to filter variables, set color themes, and manage layout.
- 🌐 **Web-Ready Output**: Instantly launch the report in your browser using the built-in HTTP server.
- 🖌️ **Custom HTML Support**: Inject any HTML block to personalize or extend your report.
- 🧪 **Lightweight & Extensible**: Easily plug into other workflows, scripts, or pipelines.



## 📦 Installation

Install from PyPI (once published):

```bash
pip install pyreport
```

Or install directly from source for the latest version:

```bash
git clone https://github.com/paudelsagar/pyreport.git
cd pyreport
pip install -e .
```



## 🧰 Basic Usage

### Create a report instance

```python
from pyreport import Report

report = Report(
    title="EDA Report",
    author="Sagar Paudel",
    data_source="Customer Credit Dataset",
    objective="Analyze and visualize credit usage behaviors",
)
```



### Add content to the report

```python
report.add_section("Data Overview", icon="📦")
report.add_dataframe(df.head(), title="Sample of the Dataset")
report.histogram(df)
report.boxplot(df)
report.violin(df)
report.densityplot(df)
report.pairplot(df)
```



### Save and launch the report

```python
# Opens the interactive report in your browser
report.run_server()
```



## 🔧 API Overview

### 📁 Report Structure

- `add_section(title, level=1, icon="📁")`: Create structured sections with hierarchy and optional icons.
- `add_content(html_str)`: Add custom HTML strings or entire blocks.
- `add_row([...], classes=[...])`: Define a row with one or more columns.
- `add_column(html_str, card=True)`: Add a column (optionally styled as a card) with HTML content.



### 📊 DataFrame Integration

- `add_dataframe(df, title=None)`: Render pandas DataFrame in a scrollable, styled table with optional title.



### 📉 Plotly Visualization

- `add_plotly_figure(fig)`: Embed interactive Plotly graphs into the report.
- `histogram(df)`, `box(df)`, `violin(df)`: Quickly generate common statistical plots using Plotly.



### 📈 Altair Visualization

- `pairplot(df)`: Show scatter plots for feature pairs in a matrix layout.
- `histoplot(df)`: Altair histogram grid for all numeric columns.
- `boxplot(df)`: Altair-based boxplot visualizations.
- `densityplot(df)`: KDE-style density plots for numeric distributions.



### 🌍 Report Output

- `run_server(port=None)`: Start a local HTTP server and open the report in your default web browser.



## 📁 Example Walkthrough

```python
import pandas as pd
from pyreport import Report

# Sample Dataset
df = pd.DataFrame({
    "age": [25, 32, 47, 51, 62],
    "income": [40000, 52000, 75000, 63000, 82000],
    "score": [200, 250, 180, 300, 270]
})

# Create the report
report = Report(
    title="Credit Risk EDA",
    author="Lead Analyst",
    data_source="Simulated Client Records",
    objective="Exploratory analysis of income and risk score distributions"
)

# Add content and visualizations
report.add_section("Numerical Features Distribution")
report.histogram(df)
report.boxplot(df)
report.pairplot(df)
report.run_server()
```



## 📌 Roadmap and Future Plans

PyReport is actively being improved! Here's what's next:

-  Command-line interface (CLI) for easy usage
-  Jupyter notebook integration with inline rendering
-  Export to static PDF/Markdown/PNG
-  Light and dark themes toggle
-  Additional chart types: heatmaps, timelines, radar charts
-  Report templates and branding support



## 📃 License

PyReport is released under the MIT License. Feel free to use, modify, and contribute.



## 🙌 Acknowledgments

Developed with ❤️ by [Sagar Paudel](https://sagar-paudel.com.np/). This project was inspired by the growing need for intuitive, fast, and customizable data reporting tools in modern data science workflows.



## 🔗 Connect with Us

- **GitHub**: [github.com/paudelsagar/pyreport](https://github.com/paudelsagar/pyreport)
- **LinkedIn**: [linkedin.com/in/sagar-paudel18/](https://www.linkedin.com/in/sagar-paudel18/)
- **Portfolio**: [sagar-paudel.com.np](https://sagar-paudel.com.np/)
