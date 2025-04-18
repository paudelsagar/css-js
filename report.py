import re
import requests
import textwrap
from datetime import datetime
from typing import List, Optional, Union
import pandas as pd
from plotly.basedatatypes import BaseFigure as PlotlyFigure


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

        css_url = "https://raw.githubusercontent.com/paudelsagar/css-js/refs/heads/main/css/report.css"
        js_url = "https://raw.githubusercontent.com/paudelsagar/css-js/refs/heads/main/js/report.js"

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

        report_info = self.show_report_info(title, author, data_source, objective)

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
        
        full_html = re.sub(r"<content>\s*</content>", content, full_html)

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
             
    def show_report_info(self, title: str, author: str, data_source: str,
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
                <h2><span class="icon">📊</span> {title}</h2>
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
                      return_html: bool = False) -> Optional[str]:
        """
        Add a pandas DataFrame to the HTML report as a styled card component.
    
        Args:
            df (pd.DataFrame): The DataFrame to be rendered.
            title (Optional[str], optional): Optional title to display above the table. Defaults to None.
            max_rows (int, optional): Maximum number of rows to display in the HTML table. Defaults to 20.
            max_height (int, optional): Maximum height of the table container (scrolls if exceeded). Defaults to 500.
            return_html (bool, optional): If True, returns the HTML string instead of adding to report content. Defaults to False.
    
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

        # Combine the HTML template and the generated DataFrame table
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
    
    def add_plotly_figure(self, fig: PlotlyFigure, return_html: bool = False) -> Optional[str]:
        """
        Adds a Plotly figure to the report in a styled card layout.
    
        Args:
            fig (BaseFigure): A valid Plotly figure (e.g., go.Figure).
            return_html (bool, optional): If True, returns the HTML string instead of writing it to the file.
                                          Defaults to False.
    
        Returns:
            Optional[str]: The generated HTML string if `return_html` is True, otherwise None.
    
        Raises:
            TypeError: If `fig` is not an instance of Plotly's BaseFigure.
        """
        
        if not isinstance(fig, PlotlyFigure):
            raise TypeError("fig must be a valid Plotly figure object (e.g., go.Figure)")
        
        config={'displaylogo': False}
        
        fig.update_layout(template="plotly_white",
                          title=dict(font=dict(size=20), xanchor="left", yanchor="top",
                                     x=0, y=0.97, pad={"l": 10}))

        full_html = f"""
        <div class="card">
            {fig.to_html(full_html=False, include_plotlyjs=True, config=config)}
            <div class="card-description">
                <button class="toggle-btn" onclick="openModal(this)" data-details="">Explaination</button>
            </div>
        </div>
        """

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