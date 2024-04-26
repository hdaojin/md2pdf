"""
Description: Markdown file coverted to html and pdf file with mistune and wkhtmltopdf
Author: hdaojin
Date: 2021-12-05
Update: 2023-10-10
Version: 2.0.0
"""

import os
import sys
from pathlib import Path
from shutil import copy, rmtree
from string import Template
from configparser import ConfigParser
import asyncio

import click
import mistune, frontmatter
from playwright.async_api import async_playwright



# from pygments import highlight
# from pygments.lexers import PythonLexer
# from pygments.formatters import HtmlFormatter

# Get the directory of the current file
DIRECTORY = Path(__file__).parent

# template directory
TEMPLATE_DIR = DIRECTORY / "templates"

# styles directory
STYLES_DIR = DIRECTORY / "styles"

# Template file name
TEMPLATE_FILE_NAME = "template.html"

# Template css file name
TEMPLATE_FILE_CSS = "template.css"

# Config file
CONFIG_FILE = DIRECTORY / "config.ini"


# Get sections from config file, return a list, porvid the user to choose.
def get_sections():
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    sections = cfg.sections()
    return sections


# Get config in the section wich user choose. It have decided the style of the html and pdf file.
def get_config(section):
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    config = dict(cfg.items(section))
    return config


# Convert markdown file to html file.
def md2html(md_file, output_dir, config):
    # style_files = [
    #     markdown_css_path = STYLES_DIR / config["markdown_css"],
    #     markdown_custom_css_path = STYLES_DIR / config["markdown_custom_css"],
    #     highlight_css_path = STYLES_DIR / config["highlight_css"],
    #     highlight_js_path = STYLES_DIR / config["highlight_js"],
    #     template_path = TEMPLATE_DIR / config["template_name"] / TEMPLATE_FILE_NAME,
    #     template_css_path = TEMPLATE_DIR / config["template_name"] / TEMPLATE_FILE_CSS,
    # ]
    style_files_path = [
        STYLES_DIR / config["markdown_css"],
        STYLES_DIR / config["markdown_custom_css"],
        STYLES_DIR / config["highlight_css"],
        STYLES_DIR / config["highlight_js"],
        TEMPLATE_DIR / config["template_name"] / TEMPLATE_FILE_CSS,
    ]

    template_path = TEMPLATE_DIR / config["template_name"] / TEMPLATE_FILE_NAME

    md_file_dir = md_file.parent
    styles_dir = md_file_dir / "styles"
    html_file = os.path.join(md_file_dir, md_file.stem + ".html")

    if not Path.exists(styles_dir):
        Path.mkdir(styles_dir)

    for style_file in style_files_path:
        copy(style_file, styles_dir)

    # Convert markdown to html using mistune and frontmatter
    # Frontmatter is used to extract metadata from markdown file which is in the format like this:
    # ---
    # document: "Document"
    # date: "2021-12-05"
    # tags: ["tag1", "tag2"]
    # ---
    # mistune is used to convert markdown to html, it is a fast and extensible markdown parser in pure Python.

    with open(md_file, "r", encoding="utf-8") as mf:
        md = mf.read()
        md_meta, md_content = frontmatter.parse(md)
        md_meta = {k.lower(): v for k, v in md_meta.items()}
        html = mistune.html(md_content)


    with open(template_path, "r", encoding="utf-8") as tf:
        template_html = Template(tf.read())
        d = {**config, **md_meta}
        full_html = template_html.safe_substitute(d, content=html)

    with open(html_file, "w", encoding="utf-8") as hf:
        hf.write(full_html)

    return html_file, styles_dir, md_meta


# Convert html file to pdf file.
async def html2pdf(html_file, pdf_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=conf
        page = await browser.new_page()
        await page.goto(html_file)
        await page.pdf(
            path=pdf_file,
            format="A4",
            margin=dict(top="15mm", right="15mm", bottom="15mm", left="15mm"),
        )
        await browser.close()
        return



# Get parameters from the command line using click

sections = get_sections()


@click.command()
@click.option(
    "-t",
    "--template",
    default="DEFAULT",
    show_default="True",
    help=f"select a HTML template: {sections}",
)
@click.argument(
    "md_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
    nargs=1,
)
@click.argument(
    "output_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    required=False,
    nargs=1,
)
def main(template, md_file, output_dir):
    md_file = Path(md_file).resolve()
    if not output_dir:
        output_dir = md_file.parent
    else:
        output_dir = Path(output_dir).resolve()
    if template not in sections and template != "DEFAULT":
        print(f"Error: template {template} is not exist.")
        sys.exit()

    config = get_config(template)
    html_file, styles_dir, meta_data = md2html(md_file, output_dir, config)
    # pdf_file = output_dir / (md_file.stem + '.pdf')
    name_parts = [
        meta_data["document"],
        meta_data["role"],
        meta_data["date"],
        meta_data["author"],
        meta_data["subject"],
        meta_data["task"].replace(" ", "-")
    ]
    # pdf_file = output_dir / ('-'.join(name_parts) + '.pdf')
    pdf_file = os.path.join(output_dir, "-".join(name_parts) + ".pdf")

    if config["generate_pdf"]:
        html2pdf(html_file, pdf_file)

    if config["generate_html"] == "False":
        print(f"Delete {html_file}")
        os.remove(html_file)
        print(f"Delete {styles_dir}")
        rmtree(styles_dir)


if __name__ == "__main__":
    main()
