""" pyreport

This module provides utilities for generating exploratory data analysis (EDA) visualizations
using Altair for both numerical and categorical data. It supports clean, consistent, and 
automated generation of plots such as:

- Pair plots (scatter plot grids for numerical feature combinations)
- Histograms
- Box plots
- Violin plots
- Density plots
- Count plots (for categorical features with optional percentage labels)

Each visualization function allows for customization such as selecting specific columns,
setting layout parameters (e.g., plots per row), limiting the number of plots or categories,
and rendering the final output as an HTML string or interactive browser view.

This module is useful for quickly summarizing patterns, distributions, and relationships 
within a pandas DataFrame, and can be easily embedded into larger data profiling tools 
or reporting workflows.

Dependencies:
    - numpy
    - pandas
    - altair

Author: Sagar Paudel
Date: 2025-04-19
"""

import os
import re
import uuid
import requests
import textwrap
import random
from datetime import datetime
from typing import List, Optional, Union
import numpy as np
import pandas as pd

import http.server
import socketserver
import webbrowser
import threading

import altair as alt
from plotly.basedatatypes import BaseFigure as PlotlyFigure
import plotly.graph_objects as go
from plotly.subplots import make_subplots

__version__ = "1.0.0"
__author__ = "Sagar Paudel"

# Configuration
css_url = "https://raw.githubusercontent.com/paudelsagar/pyreport/refs/heads/main/css/report.css"
js_url = "https://raw.githubusercontent.com/paudelsagar/pyreport/refs/heads/main/js/report.js"

plotly_config = {'displaylogo': False}

class Report:
    def __init__(self, title: str, author: str, data_source: str, objective: str,
                 filepath: str = "./eda-report.html") -> None:
        """
        Initializes a new HTML report template with inlined CSS and JS.

        Args:
            title (str): Title of the report.
            author (str): Author's name.
            data_source (str): Source of the data used in the report.
            objective (str): Purpose or goal of the report.
            filepath (str, optional): Path to the HTML file to be created. Defaults to './eda-report.html'.
        """      
        self.filepath = filepath
                   
        css_content = requests.get(css_url).text
        js_content = requests.get(js_url).text

        self.template = f"""
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="author" content="{author}">
                <title>{title}</title>
                <style>
                    {css_content}
                </style>
            </head>
            <body>
                <div class="container-fluid">
                    <content></content>
                </div>
            </body>
            <script>
                {js_content}
            </script>
        </html>
        """

        with open(self.filepath, "w") as f:
            f.write(self.template)

        report_info = self._show_report_info(title, author, data_source, objective)

        self.add_content(report_info)

    def add_content(self, content: Union[str, None]) -> None:
        """
        Inserts the provided HTML content into the report by replacing the <content></content> placeholder.

        Args:
            content (str): The HTML content to insert into the report.
        """
        with open(self.filepath, "r") as f:
            full_html = f.read()

        content = f"""
        {content}
        <content></content>
        """

        # Replace the placeholder using a regular expression
        full_html = full_html.replace("<content></content>", content)

        with open(self.filepath, "w") as f:
            f.write(full_html)

    def add_section(self, title: str, level: int = 1, icon: str = "📁",
                    return_html: bool = False) -> Union[None, str]:
        """
        Adds a titled section to the report with hierarchical styling and optional icon.
    
        Args:
            title (str): The title of the section.
            level (int, optional): The hierarchical level (1-5). Defaults to 1.
            icon (str, optional): An emoji or icon to show beside the title. Defaults to "📁".
            return_html (bool, optional): If True, returns the HTML string instead of adding it. Defaults to False.
    
        Returns:
            Union[None, str]: Returns HTML if return_html is True; otherwise, adds it directly to the report.
        """
        assert 1 <= level <= 5, "Level must be between 1 and 5"
        full_html = f"""
        <div class="report-section level-{level}">
            <div class="section-header">
                <span class="icon">{icon}</span>
                <span class="title">{title}</span>
            </div>
        </div>
        """
        full_html = textwrap.dedent(full_html)

        if return_html:
            return full_html

        self.add_content(full_html)
    
    def add_row(self, contents: List[str], classes: Optional[Union[List[str], str]] = None) -> None:
        """
        Adds a row of HTML content to the report layout using Bootstrap-like column classes.
    
        Args:
            contents (List[str]): A list of HTML content blocks to be wrapped in columns.
            classes (Union[List[str], str], optional): 
                Either a single string applied to all columns or a list of classes corresponding to each content block.
                If not provided, a default responsive class is used.
    
        Raises:
            ValueError: If `classes` is a list and its length does not match the number of contents.
        """
        if not classes:
            classes = ["col-xl-6 col-lg-6 col-md-12 col-sm col-xs"] * len(contents)
            
        elif type(classes) == str:
            classes = [classes] * len(contents)
            
        elif len(contents) != len(classes):
            raise ValueError("Length of cols and classes must be equal!!!")
    
        full_contents = ""
        for content, class_name in zip(contents, classes):
            full_contents += f"""
            <div class="{class_name}">
                {content}
            </div>
            """
    
        full_html = f"""
        <div class="row">
            {full_contents}
        </div>
        """
        
        self.add_content(full_html)
    
    def add_column(self, content: str, card: bool = True) -> None:
        """
        Wraps the given HTML content inside a styled column and card container,
        then inserts it into the HTML report.

        The structure follows a Bootstrap-like grid layout with a single column (`col-xs`)
        wrapped in a `row` and styled using the `card` class.

        Args:
            content (str): The raw HTML content to embed inside the column layout.
            card (bool, optional): Whether to wrap the content in a Bootstrap card container. Defaults to
            `True`, which is the default behavior.

        Returns:
            None: The function modifies the report in-place by injecting formatted HTML via `self.add_content`.
        """
        
        if card:
            content = f"""
            <div class="card">
                <div style="overflow: auto;">
                    {content}
                </div>
            </div>
            """
        
        full_html = f"""
        <div class="row">
            <div class="col">
                {content}
            </div>
        </div>
        """
        self.add_content(full_html)
    
    def _show_report_info(self, title: str, author: str, data_source: str,
                         objective: str, return_html: bool = True) -> Optional[str]:
        """
        Displays or returns the HTML block for the report header containing basic metadata.
    
        Args:
            title (str): Title of the report.
            author (str): Author name to be shown.
            data_source (str): Source of the data.
            objective (str): Goal or objective of the report.
            return_html (bool, optional): If True, returns the HTML string; else only displays. Defaults to True.
    
        Returns:
            Optional[str]: The HTML string if return_html is True; otherwise None.
        """
        
        html = f"""
        <div class="report-header">
            <div class="title-bar">
                <div class="title"><span class="icon">📊</span> {title}</div>
                <div class="meta">
                    <span><b>Date:</b> {datetime.today().strftime("%B %d, %Y %H:%M:%S")}</span>
                    <span><b>Data:</b> {data_source}</span>
                    <span><b>Author:</b> {author}</span>
                    <span><b>Goal:</b> {objective}</span>
                </div>
            </div>
        </div>
        """
        html = textwrap.dedent(html)
        display(HTML(html))

        if return_html:
            return html
    
    def add_dataframe(self, df: pd.DataFrame, title: Optional[str] = None,
                      max_rows: int = 20, max_height: int = 500,
                      return_html: bool = False, add_row: bool = True) -> Optional[str]:
        """
        Add a pandas DataFrame to the HTML report as a styled card component.
    
        Args:
            df (pd.DataFrame): The DataFrame to be rendered.
            title (Optional[str], optional): Optional title to display above the table. Defaults to None.
            max_rows (int, optional): Maximum number of rows to display in the HTML table. Defaults to 20.
            max_height (int, optional): Maximum height of the table container (scrolls if exceeded). Defaults to 500.
            return_html (bool, optional): If True, returns the HTML string instead of adding to report content. Defaults to False.
            add_row (bool, optional): If True, adds a row to the report content. Defaults to True.
    
        Returns:
            Optional[str]: Rendered HTML string if return_html is True, else None.
        """
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
            
        # Generate the HTML table from the DataFrame
        html_table = df.to_html(max_rows=max_rows, escape=False, index=False)

        # Conditionally add title only if provided
        title_html = (
            f'<div class="card-header">{title}</div>'
            if title else ""
        )
        
        if add_row:
            # Combine the HTML template and the generated DataFrame table
            full_html = f"""
            <div class="row">
                <div class="col">
                    <div class="card">
                        {title_html}
                        <div style="overflow: auto; max-height: {max_height}px;">
                            {html_table}
                        </div>
                        <div class="card-description">
                            <button class="toggle-btn" onclick="openModal(this)" data-details="">Explaination</button>
                        </div>
                    </div>
                </div>
            </div>
            """
        else:
            full_html = f"""
            <div class="card">
                {title_html}
                <div style="overflow: auto; max-height: {max_height}px;">
                    {html_table}
                </div>
                <div class="card-description">
                    <button class="toggle-btn" onclick="openModal(this)" data-details="">Explaination</button>
                </div>
            </div>
            """
            
        full_html = full_html.replace('\n', '').strip()

        if return_html:
            return full_html
        
        self.add_content(full_html)
    
    def add_plotly_figure(self, fig: PlotlyFigure, return_html: bool = False,
                          add_row: bool = True) -> Optional[str]:
        """
        Adds a Plotly figure to the report in a styled card layout.
    
        Args:
            fig (BaseFigure): A valid Plotly figure (e.g., go.Figure).
            return_html (bool, optional): If True, returns the HTML string instead of writing it to the file. Defaults to False.
            add_row (bool, optional): If True, adds the figure in a row layout. Defaults to True.
    
        Returns:
            Optional[str]: The generated HTML string if `return_html` is True, otherwise None.
    
        Raises:
            TypeError: If `fig` is not an instance of Plotly's BaseFigure.
        """
        
        if not isinstance(fig, PlotlyFigure):
            raise TypeError("fig must be a valid Plotly figure object (e.g., go.Figure)")
        
        fig.update_layout(template="plotly_white",
                          title=dict(font=dict(size=18, weight=500), xanchor="left", yanchor="top",
                                     x=0, y=0.97, pad={"l": 10}))

        if add_row:
            full_html = f"""
            <div class="row">
                <div class="col">
                    <div class="card">
                        {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                        <div class="card-description">
                            <button class="toggle-btn" onclick="openModal(this)" data-details="">Explaination</button>
                        </div>
                    </div>
                </div>
            </div>
            """
        else:
            full_html = f"""
            <div class="card">
                {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                <div class="card-description">
                    <button class="toggle-btn" onclick="openModal(this)" data-details="">Explaination</button>
                </div>
            </div>
            """

        if return_html:
            return full_html
        
        self.add_content(full_html)
    
    def countplot(self, df: pd.DataFrame, title: Optional[str] = None,
                  height: int = 400, include_cols: Optional[List[str]] = None,
                  exclude_cols: Optional[List[str]] = None,
                  max_plots: Optional[int] = None, max_categories: int = 20,
                  class_name: Optional[str] = None) -> None:
        """
        Generates and inserts a grid of Plotly count plots (bar plots) for all categorical columns in the provided DataFrame.

        Each chart is embedded inside a styled HTML card, and all cards are arranged in a responsive grid layout.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            title (Optional[str]): The title of the grid of charts. Defaults to None.
            height (int, optional): The height of each count plot chart in pixels. Defaults to 300.
            include_cols (Optional[List[str]], optional): A list of column names to include in the count plots. If not provided, all categorical columns will be used.
            exclude_cols (Optional[List[str]], optional): A list of column names to exclude from the count plots. If not provided, no columns will be excluded.
            max_plots (Optional[int], optional): Maximum number of count plots to generate. If None, plot all available.
            max_categories (int, optional): Maximum number of categories to display in each count plot. Defaults to 20.
            class_name (Optional[str], optional): CSS class for the outer container div of each count plot card. Defaults to "col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs".

        Returns:
            None: The function modifies the HTML report by injecting new content via `self.add_content`.
        """
        if not class_name:
            class_name = "col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs"
        
        # Conditionally add title only if provided
        title_html = (
            f'<div class="card-header">{title}</div>'
            if title else ""
        )
                    
        # Identify categorical columns
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if include_cols:
            cat_cols = include_cols
        elif exclude_cols:
            cat_cols = [col for col in cat_cols if col not in exclude_cols]
        
        if max_plots:
            cat_cols = cat_cols[:max_plots]

        contents = ""
        for col in cat_cols:
            # Calculate frequency for each category
            count_data = df[col].value_counts().reset_index()
            count_data.columns = [col, 'count']

            # Limit the categories to the top 'max_categories' if needed
            if len(count_data) > max_categories:
                count_data = count_data.head(max_categories)

            # Calculate percentage for each category
            total_count = count_data['count'].sum()
            count_data['percentage'] = (count_data['count'] / total_count) * 100

            # Create the count plot (bar chart)
            fig = px.bar(count_data, x=col, y='percentage', title=f"Count Plot of {col}",
                         labels={'percentage': 'Percentage'})
            
            # Use hover data to show the actual count
            fig.update_traces(hovertemplate=f'{col}: %{{x}}<br>Count: %{{customdata[0]}}<br>Percentage: %{{y}}%')

            # Add custom data for hover to display counts
            fig.update_traces(customdata=count_data[['count']])

            fig.update_layout(height=height, template="plotly_white",
                              title=dict(font=dict(size=18, weight=500),
                                         xanchor="left", yanchor="top",
                                         x=0, y=0.97, pad={"l": 10}),
                              margin=dict(t=50, b=10, l=10, r=10))
            
            # Add the chart HTML to the content
            contents += f"""
            <div class="{class_name}">
                <div class="card">
                    {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                </div>
            </div>
            """

        # Combine everything into a full HTML grid
        full_html = f"""
        <div class="row">
            {title_html}
            {contents}
        </div>
        """

        # Add the final content to your report
        self.add_content(full_html)
   
    def donut(self, df: pd.DataFrame, title: Optional[str] = None,
              height: int = 400, include_cols: Optional[List[str]] = None,
              exclude_cols: Optional[List[str]] = None,
              dunut_hole: float = 0.4,
              max_plots: Optional[int] = None, max_categories: int = 20,
              class_name: Optional[str] = None) -> None:
        """
        Generates and inserts a grid of Plotly donut charts for all categorical columns in the provided DataFrame.

        For each categorical column, a donut chart is created showing the distribution of category frequencies as percentages.
        The charts are embedded within styled HTML cards and arranged in a responsive grid layout within the report.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            title (Optional[str]): Optional title displayed above the grid of charts.
            height (int, optional): Height of each donut chart in pixels. Defaults to 400.
            include_cols (Optional[List[str]], optional): A list of categorical column names to include in the plots.
                If not provided, all categorical columns will be used.
            exclude_cols (Optional[List[str]], optional): A list of categorical column names to exclude from the plots.
            dunut_hole (float, optional): Size of the hole in the donut chart (0 for full pie, up to 1 for fully hollow). Defaults to 0.4.
            max_plots (Optional[int], optional): Maximum number of donut charts to generate. If None, plots all available.
            max_categories (int, optional): Maximum number of categories to display per chart. Others are excluded. Defaults to 20.
            class_name (Optional[str], optional): CSS class for the outer container div of each chart card.
                Controls layout responsiveness. Defaults to "col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs".

        Returns:
            None: The method injects the generated donut charts into the HTML report via `self.add_content`.
        """
        if not class_name:
            class_name = "col-xl-6 col-lg-6 col-md-6 col-sm-12 col-xs"

        title_html = f'<div class="card-header">{title}</div>' if title else ""

        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if include_cols:
            cat_cols = include_cols
        elif exclude_cols:
            cat_cols = [col for col in cat_cols if col not in exclude_cols]

        if max_plots:
            cat_cols = cat_cols[:max_plots]

        contents = ""
        for col in cat_cols:
            count_data = df[col].value_counts().reset_index()
            count_data.columns = [col, 'count']

            if len(count_data) > max_categories:
                count_data = count_data.head(max_categories)

            total_count = count_data['count'].sum()
            count_data['percentage'] = (count_data['count'] / total_count) * 100

            # Create a donut chart
            fig = px.pie(count_data, names=col, values='count',
                         hole=dunut_hole, title=f'Dunut Chart of {col}')

            fig.update_traces(
                textinfo='percent',
                hovertemplate=f'{col}: %{{label}}<br>Count: %{{value}}<br>Percentage: %{{percent}}'
            )

            fig.update_layout(
                height=height,
                template="plotly_white",
                margin=dict(t=50, b=10, l=10, r=10),
                title=dict(font=dict(size=18, weight=500),
                           xanchor="left", yanchor="top",
                           x=0, y=0.97, pad={"l": 10}),
                showlegend=True
            )

            contents += f"""
            <div class="{class_name}">
                <div class="card">
                    {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                </div>
            </div>
            """

        full_html = f"""
        <div class="row">
            {title_html}
            {contents}
        </div>
        """

        self.add_content(full_html)

    def histogram(self, df: pd.DataFrame,
                  title: Optional[str] = None,
                  bins: Optional[int] = None,
                  include_cols: Optional[List[str]] = None,
                  exclude_cols: Optional[List[str]] = None,
                  max_plots: Optional[int] = None,
                  height: int = 300, class_name: Optional[str] = None) -> None:
        """
        Generates and inserts a grid of Plotly histogram charts for all numeric columns in the provided DataFrame.

        Each chart is embedded inside a styled HTML card, and all cards are arranged in a responsive grid layout.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            title (str, optional): The title of the histogram grid. Defaults to None.
            bins (Optional[int], optional): Number of bins for the histograms. Defaults to Plotly's auto-binning.
            include_cols (Optional[List[str]], optional): List of column names to include in the histogram.
            exclude_cols (Optional[List[str]], optional): List of column names to exclude from the histogram.
            max_plots (Optional[int], optional): Maximum number of histogram plots to generate. If None, plot all available.
            height (int, optional): The height of each histogram chart in pixels. Defaults to 300.
            class_name (Optional[str], optional): CSS class for the outer container div of each histogram card.
                                                Defaults to "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs".

        Returns:
            None: The function modifies the HTML report by injecting new content via `self.add_content`.
        """
        if not class_name:
            class_name = "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs"
            
        # Conditionally add title only if provided
        title_html = (
            f'<div class="card-header">{title}</div>'
            if title else ""
        )
            
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if include_cols:
            numeric_cols = include_cols
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
            
        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        contents = ""
        for col in numeric_cols:
            fig = px.histogram(df, x=col, nbins=bins)
            fig.update_layout(height=height, template="plotly_white",
                              title=dict(font=dict(size=18, weight=500), xanchor="left", yanchor="top",
                                     x=0, y=0.97, pad={"l": 10}),
                              margin=dict(t=20, b=10, l=10, r=10))
            contents += f"""
            <div class="{class_name}">
                <div class="card">
                    {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                </div>
            </div>
            """

        full_html = f"""
        <div class="row">
            {title_html}
            {contents}
        </div>
        """

        self.add_content(full_html)
        
    def box(self, df: pd.DataFrame,
            title: Optional[str] = None,
            height: int = 300,
            include_cols: Optional[List[str]] = None,
            exclude_cols: Optional[List[str]] = None,
            max_plots: Optional[int] = None,
            class_name: Optional[str] = None) -> None:
        """
        Generates and inserts a grid of Plotly box plots for all numeric columns in the provided DataFrame.

        Each chart is embedded inside a styled HTML card, and all cards are arranged in a responsive grid layout.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            title (Optional[str], optional): The title of the grid. Defaults to None.
            height (int, optional): The height of each box plot chart in pixels. Defaults to 300.
            include_cols (Optional[List[str]], optional): A list of column names to include in the box
            plots. If not provided, all numeric columns in the DataFrame will be used.
            exclude_cols (Optional[List[str]], optional): A list of column names to exclude from the
            box plots. If not provided, no columns will be excluded.
            max_plots (Optional[int], optional): Maximum number of box plots to generate. If None, plot all available.
            class_name (Optional[str], optional): CSS class for the outer container div of each box plot card.
                                                Defaults to "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs".

        Returns:
            None: The function modifies the HTML report by injecting new content via `self.add_content`.
        """
        if not class_name:
            class_name = "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs"
        
        # Conditionally add title only if provided
        title_html = (
            f'<div class="card-header">{title}</div>'
            if title else ""
        )
            
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if include_cols:
            numeric_cols = include_cols
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        contents = ""
        for col in numeric_cols:
            fig = px.box(df, y=col)
            fig.update_layout(height=height, template="plotly_white",
                              title=dict(font=dict(size=18, weight=500), xanchor="left", yanchor="top",
                                     x=0, y=0.97, pad={"l": 10}),
                              margin=dict(t=20, b=10, l=10, r=10))
            contents += f"""
            <div class="{class_name}">
                <div class="card">
                    {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                </div>
            </div>
            """

        full_html = f"""
        <div class="row">
            {title_html}
            {contents}
        </div>
        """

        self.add_content(full_html)
    
    def violin(self, df: pd.DataFrame,
               title: Optional[str] = None,
               height: int = 300,
               include_cols: Optional[List[str]] = None,
               exclude_cols: Optional[List[str]] = None,
               max_plots: Optional[int] = None,
               class_name: Optional[str] = None) -> None:
        """
        Generates and inserts a grid of Plotly violin plots for all numeric columns in the provided DataFrame.

        Each chart is embedded inside a styled HTML card, and all cards are arranged in a responsive grid layout.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            title (Optional[str]): The title of the grid of charts. Defaults to None.
            height (int, optional): The height of each violin plot chart in pixels. Defaults to 300.
            include_cols (Optional[List[str]], optional): A list of column names to include in the violin
            plots. If not provided, all numeric columns in the DataFrame will be used.
            exclude_cols (Optional[List[str]], optional): A list of column names to exclude from the
            violin plots. If not provided, no columns will be excluded.
            max_plots (Optional[int], optional): Maximum number of violin plots to generate. If None, plot all available.
            class_name (Optional[str], optional): CSS class for the outer container div of each violin plot card.
                                                Defaults to "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs".

        Returns:
            None: The function modifies the HTML report by injecting new content via `self.add_content`.
        """
        if not class_name:
            class_name = "col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs"
        
        # Conditionally add title only if provided
        title_html = (
            f'<div class="card-header">{title}</div>'
            if title else ""
        )
            
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if include_cols:
            numeric_cols = include_cols
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        contents = ""
        for col in numeric_cols:
            fig = px.violin(df, y=col, box=True, points="outliers")
            fig.update_layout(height=height, template="plotly_white",
                              title=dict(font=dict(size=18, weight=500), xanchor="left", yanchor="top",
                                     x=0, y=0.97, pad={"l": 10}),
                              margin=dict(t=20, b=10, l=10, r=10))
            contents += f"""
            <div class="{class_name}">
                <div class="card">
                    {fig.to_html(full_html=False, include_plotlyjs=True, config=plotly_config)}
                </div>
            </div>
            """

        full_html = f"""
        <div class="row">
            {title_html}
            {contents}
        </div>
        """

        self.add_content(full_html)
    
    def pairplot(self, df: pd.DataFrame, include_cols: Optional[List[str]] = None,
                 exclude_cols: Optional[List[str]] = None, columns_per_row: int = 6,
                 max_plots: Optional[int] = None, width: int = 100, height: int = 100,
                 mark_point_size: int = 1, mark_point_opacity: float = 0.8,
                 return_html: bool = False) -> Optional[str]:
        """
        Generates a grid of scatter plots (pairplot) using Altair for combinations of numerical features
        in the input DataFrame. Each feature is paired against all other features except itself.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to visualize.
            include_cols (Optional[List[str]], optional): A list of specific numeric columns to include. 
                If provided, only these columns will be used for plotting. Defaults to None.
            exclude_cols (Optional[List[str]], optional): A list of columns to exclude from plotting.
                Ignored if `include_cols` is provided. Defaults to None.
            columns_per_row (int, optional): Number of scatter plots to display per row. Defaults to 6.
            max_plots (Optional[int], optional): Maximum number of feature pairs to plot. Useful for large datasets. Defaults to None.
            width (int, optional): Width of each subplot in pixels. Defaults to 100.
            height (int, optional): Height of each subplot in pixels. Defaults to 100.
            mark_point_size (int, optional): Size of each scatter point. Defaults to 1.
            mark_point_opacity (float, optional): Opacity of each scatter point (0 to 1). Defaults to 0.8.
            return_html (bool, optional): If True, returns the chart as an HTML string. Otherwise, shows it in a browser. Defaults to False.

        Returns:
            Optional[str]: An HTML string representation of the chart if `return_html` is True, otherwise None.
        """

        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if include_cols:
            numeric_cols = [col for col in numeric_cols if col in include_cols]
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

        # Generate feature pair combinations where each feature is paired with all others, skipping itself
        pair_combos = []
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                pair_combos.append((numeric_cols[i], numeric_cols[j]))
        
        if max_plots:
            pair_combos = pair_combos[:max_plots]

        # Create scatter plots for each pair
        charts = []
        for y, x in pair_combos:
            chart = alt.Chart(df).mark_point(size=mark_point_size, opacity=mark_point_opacity).encode(
                x=alt.X(x, scale=alt.Scale(zero=False), axis=alt.Axis(titleFontWeight='normal')),
                y=alt.Y(y, scale=alt.Scale(zero=False), axis=alt.Axis(titleFontWeight='normal')),
            ).properties(
                width=width,
                height=height
            )
            charts.append(chart)
        
        # Arrange charts into a grid
        pairplot_fig = alt.vconcat(*[
            alt.hconcat(*charts[i: i+columns_per_row])
            for i in range(0, len(charts), columns_per_row)
        ])

        # Create title chart aligned to the left
        title_chart = alt.Chart(pd.DataFrame({'text': ['Pairplot of Numerical Features']})).mark_text(
            align='left', x=-50,
            fontSize=18,
            fontWeight=500 # 'normal', 'bold', 'lighter', 'bolder', 100, 200, 300, 400, 500, 600, 700, 800, 900
        ).encode(
            text='text:N'
        ).properties(
            width=columns_per_row * width,
            height=30
        )

        # Combine title and chart grid
        final_plot = alt.vconcat(title_chart, pairplot_fig)

        if return_html:
            # renderer: canvas, svg, png, json, none
            return final_plot.to_html(output_div=f"altair-{uuid.uuid4().hex}",
                                      fullhtml=False, requirejs=False, inline=False,
                                      embed_options={'renderer': 'png'})

        final_plot.show()
        
    def histoplot(self, df: pd.DataFrame, include_cols: Optional[List[str]] = None,
                  exclude_cols: Optional[List[str]] = None, columns_per_row: int = 4,
                  max_plots: Optional[int] = None, width: int = 200, height: int = 150,
                  bin_step: Optional[float] = None, return_html: bool = False) -> Optional[str]:
        """
        Generates a grid of histograms using Altair for each numerical feature in the input DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame containing data to visualize.
            include_cols (Optional[List[str]], optional): Specific numeric columns to include. Defaults to None.
            exclude_cols (Optional[List[str]], optional): Columns to exclude from plotting. Ignored if `include_cols` is provided. Defaults to None.
            columns_per_row (int, optional): Number of histogram plots per row. Defaults to 6.
            max_plots (Optional[int], optional): Maximum number of features to include. Useful for large datasets. Defaults to None.
            width (int, optional): Width of each histogram in pixels. Defaults to 100.
            height (int, optional): Height of each histogram in pixels. Defaults to 100.
            bin_step (Optional[float], optional): Step size for binning. If None, Altair will use automatic binning. Defaults to None.
            return_html (bool, optional): If True, returns the chart as HTML string. Otherwise displays in browser. Defaults to False.

        Returns:
            Optional[str]: HTML string if `return_html` is True; otherwise None.
        """
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if include_cols:
            numeric_cols = [col for col in numeric_cols if col in include_cols]
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        charts = []
        for col in numeric_cols:
            chart = alt.Chart(df).mark_bar(opacity=0.75).encode(
                x=alt.X(col, bin=alt.Bin(step=bin_step) if bin_step else True,
                        axis=alt.Axis(titleFontWeight='normal')),
                y=alt.Y('count()', axis=alt.Axis(title='Count', titleFontWeight='normal'))
            ).properties(
                width=width,
                height=height
            )
            charts.append(chart)

        grid = alt.vconcat(*[
            alt.hconcat(*charts[i:i + columns_per_row])
            for i in range(0, len(charts), columns_per_row)
        ])

        title_chart = alt.Chart(pd.DataFrame({
            'text': ['Histogram of Numerical Features']})).mark_text(
            align='left', x=-50,
            fontSize=18,
            fontWeight=500
        ).encode(
            text='text:N'
        ).properties(
            width=columns_per_row * width,
            height=30
        )

        final_plot = alt.vconcat(title_chart, grid)

        if return_html:
            return final_plot.to_html(output_div=f"altair-{uuid.uuid4().hex}",
                                      fullhtml=False, requirejs=False, inline=False,
                                      embed_options={'renderer': 'png'})

        final_plot.show()
    
    def boxplot(self, df: pd.DataFrame, include_cols: Optional[List[str]] = None,
                exclude_cols: Optional[List[str]] = None, columns_per_row: int = 4,
                max_plots: Optional[int] = None, width: int = 180, height: int = 150,
                return_html: bool = False) -> Optional[str]:
        """
        Generates a grid of box plots using Altair for each numerical feature in the input DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame containing data to visualize.
            include_cols (Optional[List[str]], optional): Specific numeric columns to include. Defaults to None.
            exclude_cols (Optional[List[str]], optional): Columns to exclude from plotting. Ignored if `include_cols` is provided. Defaults to None.
            columns_per_row (int, optional): Number of box plots per row. Defaults to 6.
            max_plots (Optional[int], optional): Maximum number of features to include. Useful for large datasets. Defaults to None.
            width (int, optional): Width of each box plot in pixels. Defaults to 100.
            height (int, optional): Height of each box plot in pixels. Defaults to 100.
            return_html (bool, optional): If True, returns the chart as an HTML string. Otherwise displays in browser. Defaults to False.

        Returns:
            Optional[str]: HTML string if `return_html` is True; otherwise None.
        """
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if include_cols:
            numeric_cols = [col for col in numeric_cols if col in include_cols]
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        charts = []
        for col in numeric_cols:
            box = alt.Chart(df).mark_boxplot(size=30).encode(
                y=alt.Y(col, axis=alt.Axis(titleFontWeight='normal'))
            ).properties(
                width=width,
                height=height
            )
            charts.append(box)

        grid = alt.vconcat(*[
            alt.hconcat(*charts[i:i + columns_per_row])
            for i in range(0, len(charts), columns_per_row)
        ])

        title_chart = alt.Chart(pd.DataFrame({
            'text': ['Boxplot of Numerical Features']})).mark_text(
            align='left', x=-50,
            fontSize=18,
            fontWeight=500
        ).encode(
            text='text:N'
        ).properties(
            width=columns_per_row * width,
            height=30
        )

        final_plot = alt.vconcat(title_chart, grid)

        if return_html:
            return final_plot.to_html(output_div=f"altair-{uuid.uuid4().hex}",
                                      fullhtml=False, requirejs=False, inline=False,
                                      embed_options={'renderer': 'png'})

        final_plot.show()
    
    def densityplot(self, df: pd.DataFrame, include_cols: Optional[List[str]] = None,
                    exclude_cols: Optional[List[str]] = None, columns_per_row: int = 4,
                    max_plots: Optional[int] = None, width: int = 150, height: int = 150,
                    return_html: bool = False) -> Optional[str]:
        """
        Generates a grid of KDE-based density plots using Altair for numerical features in a DataFrame.

        Args:
            df (pd.DataFrame): Input DataFrame.
            include_cols (Optional[List[str]], optional): Specific numeric columns to include. Defaults to None.
            exclude_cols (Optional[List[str]], optional): Columns to exclude. Ignored if `include_cols` is provided. Defaults to None.
            columns_per_row (int, optional): Number of plots per row. Defaults to 6.
            max_plots (Optional[int], optional): Maximum number of features to plot. Defaults to None.
            width (int, optional): Width of each plot. Defaults to 100.
            height (int, optional): Height of each plot. Defaults to 100.
            return_html (bool, optional): If True, returns the chart as HTML. Otherwise, displays it. Defaults to False.

        Returns:
            Optional[str]: HTML string if `return_html` is True; otherwise None.
        """
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if include_cols:
            numeric_cols = [col for col in numeric_cols if col in include_cols]
        elif exclude_cols:
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

        if max_plots:
            numeric_cols = numeric_cols[:max_plots]

        charts = []
        for col in numeric_cols:
            chart = alt.Chart(df).transform_density(
                density=col,
                as_=[col, 'density']
            ).mark_area(opacity=0.6).encode(
                x=alt.X(col, axis=alt.Axis(titleFontWeight='normal')),
                y=alt.Y('density:Q', axis=alt.Axis(title='Density', titleFontWeight='normal'))
            ).properties(
                width=width,
                height=height
            )
            charts.append(chart)

        grid = alt.vconcat(*[
            alt.hconcat(*charts[i:i + columns_per_row])
            for i in range(0, len(charts), columns_per_row)
        ])

        title_chart = alt.Chart(pd.DataFrame({
            'text': ['Density Plot of Numerical Features']})).mark_text(
            align='left', x=-50,
            fontSize=18,
            fontWeight=500
        ).encode(
            text='text:N'
        ).properties(
            width=columns_per_row * width,
            height=30
        )

        final_plot = alt.vconcat(title_chart, grid)

        if return_html:
            return final_plot.to_html(output_div=f"altair-{uuid.uuid4().hex}",
                                      fullhtml=False, requirejs=False, inline=False,
                                      embed_options={'renderer': 'png'})
        
        final_plot.show()
    
    def run_server(self, port: Optional[int] = None) -> None:
        """
        Launches a local HTTP server to serve the report HTML file.

        Args:
            port (int, optional): The port number to run the server on. If None, a random port between 8000 and 8999 is used.
        """
        port = port or random.randint(8000, 8999)
        directory, filename = os.path.split(os.path.abspath(self.filepath))
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
        
        def open_browser():
            url = f"http://0.0.0.0:{port}/{filename}"
            webbrowser.open_new_tab(url)

        thread = threading.Thread(target=open_browser)
        thread.start()

        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving '{filename}' at http://0.0.0.0:{port}")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Shutting down server.")
                httpd.shutdown()
                
def histogram_plot(df: pd.DataFrame, bins: Optional[int] = None,
                   default_col: Optional[str] = None) -> go.Figure:
    """
    Generates a histogram plot for a specified numerical column in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing numerical data.
        bins (Optional[int], optional): The number of bins for the histogram. Defaults to None.
        default_col (Optional[str], optional): The column to plot. If not provided, the first numerical column is used.

    Returns:
        go.Figure: A Plotly Figure object containing the histogram plot.
    """
    if default_col is None:
        default_col = df.select_dtypes(include='number').columns.tolist()[0]
    
    # Create figure for Histogram
    fig = go.Figure()

    # Add Histogram trace
    fig.add_trace(go.Histogram(x=df[default_col], name='Histogram', visible=True, nbinsx=bins))

    # Column selector (dropdown)
    column_dropdown = [
        dict(label=col,
             method='update',
             args=[
                 {'x': [df[col]]},  # Update the x-axis data for the histogram
                 {'title': f'Distribution of {col}'}  # Update title for the selected column
             ])
        for col in df.select_dtypes(include='number').columns.tolist()
    ]

    column_selector = dict(
        buttons=column_dropdown,
        direction="down",
        x=0.5, y=1.0,
        pad={"r": 0, "t": -40},
        xanchor="center",
        yanchor="top"
    )

    # Update layout with only the column selector dropdown
    fig.update_layout(
        updatemenus=[column_selector],
        title=f"Distribution of {default_col}",
        height=500,
        showlegend=False,
        margin=dict(t=80)
    )

    return fig

def violin_plot(df: pd.DataFrame, default_col: Optional[str] = None) -> go.Figure:
    """
    Generates a violin plot for a specified numerical column in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing numerical data.
        default_col (Optional[str], optional): The column to plot. If not provided, the first numerical column is used.

    Returns:
        go.Figure: A Plotly Figure object containing the violin plot.
    """
    
    if default_col is None:
        default_col = df.select_dtypes(include='number').columns.tolist()[0]
    
    # Create figure for Violinplot
    fig = go.Figure()

    # Add violin plot trace
    fig.add_trace(go.Violin(
        y=df[default_col], 
        name='', 
        visible=True, 
        box_visible=True, 
        meanline_visible=True
    ))

    # Column selector (dropdown)
    column_dropdown = [
        dict(label=col,
             method='update',
             args=[
                 {'y': [df[col]]},
                 {'title': f'Violin Plot of {col}'}
             ])
        for col in df.select_dtypes(include='number').columns.tolist()
    ]

    column_selector = dict(
        buttons=column_dropdown,
        direction="down",
        x=0.5, y=1.0,
        pad={"r": 0, "t": -40},
        xanchor="center",
        yanchor="top"
    )

    # Update layout with the column dropdown
    fig.update_layout(
        updatemenus=[column_selector],
        title=f"Violin Plot of {default_col}",
        height=500,
        showlegend=False,
        margin=dict(t=80)
    )

    return fig

def histogram_subplot(df: pd.DataFrame, bins: Optional[int] = None, max_cols_per_row: int = 3,
                      horizontal_spacing: float = 0.03, vertical_spacing: float = 0.1) -> go.Figure:
    """
    Generates a subplot of histograms for each numeric column in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing numerical data.
        bins (Optional[int], optional): The number of bins for the histograms. Defaults to None.
        max_cols_per_row (int, optional): The maximum number of columns to display per row in the subplot. Defaults to 3.
        horizontal_spacing (float, optional): The horizontal space between subplots. Defaults to 0.03.
        vertical_spacing (float, optional): The vertical space between subplots. Defaults to 0.1.

    Returns:
        go.Figure: A Plotly Figure object containing the subplot of histograms.
    """
    
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    rows = int(np.ceil(len(numeric_cols) / max_cols_per_row))
    cols = min(len(numeric_cols), max_cols_per_row)

    # Create subplots
    subplot_fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=numeric_cols,
        horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing)

    # Add histogram trace for each numeric column
    for i, col in enumerate(numeric_cols):
        r = i // cols + 1
        c = i % cols + 1
        fig = go.Histogram(
            x=df[col],
            name="",
            nbinsx=bins,
            marker=dict(line=dict(width=0.5, color='gray'))
        )
        subplot_fig.add_trace(fig, row=r, col=c)

    # Update layout for subplots
    subplot_fig.update_layout(
        height=300 * rows,
        title_text="Distribution of All Numeric Features",
        showlegend=False
    )

    return subplot_fig

def violin_subplot(df: pd.DataFrame, max_cols_per_row: int = 3, 
                   horizontal_spacing: float = 0.03, vertical_spacing: float = 0.08) -> go.Figure:
    """
    Generates a subplot of violin plots for each numeric column in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame containing numerical data.
        max_cols_per_row (int, optional): The maximum number of columns to display per row in the subplot. Defaults to 3.
        horizontal_spacing (float, optional): The horizontal space between subplots. Defaults to 0.03.
        vertical_spacing (float, optional): The vertical space between subplots. Defaults to 0.08.

    Returns:
        go.Figure: A Plotly Figure object containing the subplot of violin plots.
    """
    
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    rows = int(np.ceil(len(numeric_cols) / max_cols_per_row))
    cols = min(len(numeric_cols), max_cols_per_row)

    # Create subplots
    subplot_fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=numeric_cols,
        horizontal_spacing=horizontal_spacing, vertical_spacing=vertical_spacing)

    # Function to add violin trace with unique colors for each subplot
    def add_violin_trace(col, row, col_num):
        fig = go.Violin(
            y=df[col],  # For violin plot, use 'y' data
            name=col,  # You can keep this as col for legend or an empty string ""
            box_visible=True,
            meanline_visible=True
        )
        subplot_fig.add_trace(fig, row=row, col=col_num)

        # Remove axis titles, but keep axis ticks
        subplot_fig.update_xaxes(title_text='', showticklabels=False, row=row, col=col_num)

    # Add violin plot for each numeric column, with a unique color for each subplot
    for i, col in enumerate(numeric_cols):
        r = i // cols + 1
        c = i % cols + 1
        add_violin_trace(col, r, c)

    # Update layout to remove axis titles for all subplots
    subplot_fig.update_layout(
        height=300 * rows,
        title_text="Violin Plot of All Numeric Features",
        showlegend=False
    )

    return subplot_fig
