"""
Description: Convert markdown file to html and pdf file using mistune, frontmatter and playwright.
Author: hdaojin
Version: 3.0.0
Date: 2021-12-05
Update: 2024-04-26
"""

from configparser import ConfigParser
from pathlib import Path
from shutil import copy, rmtree
from string import Template
import sys
import os
import asyncio

import mistune
import frontmatter
import click
from playwright.async_api import async_playwright
# from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.ini"
TEMPLATE_DIR = BASE_DIR / "templates"
STYLES_DIR = BASE_DIR / "styles"



# Parse the config file "config.ini"
def parse_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    return config

# Command line options using click
@click.command()
@click.option(
    "-t",
    "--template",
    default="DEFAULT",
    show_default=True,
    help=f"Choose a html template: {parse_config().sections()}",
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

def parse_options(template, md_file, output_dir):
    if template not in parse_config().sections() and template != "DEFAULT":
        click.echo(f"Invalid template: {template}")
        sys.exit(1)
    try:
        md_file = Path(md_file).resolve()
    except FileNotFoundError:
        click.echo(f"File not found: {md_file}")
        sys.exit(1)
    if not output_dir:
        output_dir = md_file.parent
    else:
        try:
            output_dir = Path(output_dir).resolve()
        except FileNotFoundError:
            click.echo(f"Directory not found: {output_dir}")
            sys.exit(1)
    return template, md_file, output_dir


# Convert markdown to html using mistune and frontmatter
def md2html(md_file, output_dir, template):
    template_configrations = parse_config()[template]
    style_files = [
        template_configrations["markdown_css"],
        template_configrations["markdown_custom_css"],
        template_configrations["highlight_css"],
        template_configrations["highlight_js"],
        template_configrations["template_dir"] / "template.css",
    ]

    template_file = TEMPLATE_DIR / parse_config()[template]["template_dir"] / "template.html"
    html_file = output_dir / (md_file.stem + ".html")

    # Read the markdown file and convert it to html
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
        md = frontmatter.loads(content)
        md_meta = md.metadata
        md_content = md.content
        # me_meta, md_content = frontmatter.parse(md)
        html_content = mistune.html(md_content)

    # Read the template file and substitute the variables using the template_configrations, md_meta and html_content
    with open(template_file, "r", encoding="utf-8") as tf:
        template = Template(tf.read())
        # Merge two dictionaries 
        # d = {**template_configrations, **md_meta}
        full_html = template.safe_substitute(template_configrations, md_meta, content=html_content)

    # Write the full html content to the html file
    with open(html_file, "w", encoding="utf-8") as hf:
        hf.write(full_html)

    # Create a directory for the style files and copy the style files to the directory for the full html file
    html_file_style_dir = output_dir / (md_file.stem + "_style")
    html_file_style_dir.mkdir(exist_ok=True)
    for style_file in style_files:
        copy(style_file, html_file_style_dir)

    return html_file, html_file_style_dir

# Convert html to pdf using playwright
async def html2pdf(html_file, output_dir):
    pdf_file = output_dir / (html_file.stem + ".pdf")
    print_pdf_browser = parse_config()["print_pdf_browser"]
    print_pdf_browser_path = parse_config()["print_pdf_browser_path"]
    async with async_playwright() as p:
        if print_pdf_browser == "chromium":
            browser = await p.chromium.launch(headless=True, executable_path=print_pdf_browser_path)
        elif print_pdf_browser == "firefox":
            browser = await p.firefox.launch(headless=True, executable_path=print_pdf_browser_path)
        elif print_pdf_browser == "webkit":
            browser = await p.webkit.launch(headless=True, executable_path=print_pdf_browser_path)
        else:
            print("Invalid browser")
            sys.exit(1)

        page = await browser.new_page()
        await page.goto(html_file.as_uri())
        await page.pdf(
            path=pdf_file, 
            format="A4",
            margin={"top": "1mm", "bottom": "1.5cm", "left": "1cm", "right": "1cm"},
            printBackground=True
            )
        await browser.close()
    return

# Main function
def main():
    template, md_file, output_dir = parse_options()
    print(template, md_file, output_dir)
    html_file, html_file_style_dir = md2html(md_file, output_dir, template)
    asyncio.run(html2pdf(html_file, output_dir))
    os.remove(html_file)
    rmtree(html_file_style_dir)

if __name__ == "__main__":
    main()
        
