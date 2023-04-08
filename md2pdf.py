"""
Markdown file coverted to html and pdf file with python-markdown and wkhtmltopdf
Author: hdaojin
Version: 2.0.0
Date: 2021-12-05
Update: 2023-04-05
"""

from configparser import ConfigParser
from pathlib import Path
from shutil import copy, rmtree
from string import Template
import sys
import os

import pdfkit
import markdown
import click

# from pygments import highlight
# from pygments.lexers import PythonLexer
# from pygments.formatters import HtmlFormatter

# Get the directory of the current file
DIRECTORY = Path(__file__).parent

# template directory
TEMPLATE_DIR = DIRECTORY / 'templates'

# styles directory
STYLES_DIR = DIRECTORY / 'styles'

# Template file name
TEMPLATE_FILE_NAME = 'template.html'

# Template css file name
TEMPLATE_FILE_CSS = 'template.css'

# Config file
CONFIG_FILE = DIRECTORY / 'config.ini'


# Get sections from config file, return a list, porvid the user to choose.
def get_sections():
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    sections = cfg.sections()
    return sections

# Get config in the section which user choose. It have decided the style of the html and pdf file.


def get_config(section):
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    config = dict(cfg.items(section))
    return config

# Convert markdown file to html file.


def md2html(md_file, output_dir, config):
    markdown_css_path = STYLES_DIR / config['markdown_css']
    markdown_custom_css_path = STYLES_DIR / config['markdown_custom_css']
    template_path = TEMPLATE_DIR / config['template_name'] / TEMPLATE_FILE_NAME
    template_css_path = TEMPLATE_DIR / config['template_name'] / TEMPLATE_FILE_CSS

    md_file_dir = md_file.parent

    styles_dir = md_file_dir / 'styles'
    # html_file = output_dir / (md_file.stem + '.html')
    html_file = os.path.join(md_file_dir, md_file.stem + '.html')

    if not Path.exists(styles_dir):
        Path.mkdir(styles_dir)

    for style_file in markdown_css_path, markdown_custom_css_path, template_css_path:
        copy(style_file, styles_dir)

    extensions = ['extra', 'meta', 'nl2br',
                  'sane_lists', 'smarty', 'toc', 'wikilinks']

    with open(md_file, 'r', encoding="utf-8") as mf:
        md = markdown.Markdown(output_format='html5', extensions=extensions)
        html = md.convert(mf.read())
        meta_data = md.Meta
        meta_data = {k: ' '.join(v) for k, v in meta_data.items()}

    with open(template_path, 'r', encoding="utf-8") as tf:
        template_html = Template(tf.read())
        d = {**config, **meta_data}
        full_html = template_html.safe_substitute(d, content=html)

    with open(html_file, 'w', encoding="utf-8") as hf:
        hf.write(full_html)

    return html_file, styles_dir, meta_data

# Convert html file to pdf file.

def html2pdf(html_file, pdf_file):
    options = {
        'encoding': "UTF-8",
        'margin-top': '15mm',
        'margin-right': '15mm',
        'margin-bottom': '15mm',
        'margin-left': '15mm',
        'page-size': 'A4',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'cookie': [
            ('cookie-empty-value', '""'),
            ('cookie-name1', 'cookie-value1'),
            ('cookie-name2', 'cookie-value2'),
        ],
        'footer-font-size': '6',
        'footer-font-name': 'Times-Roman',
        'footer-center': '[page]/[topage]',
        'footer-spacing': '5',
        'enable-local-file-access': None
    }
    pdfkit.from_file(html_file, pdf_file, options=options)
    return

# Get parameters from the command line using click

sections = get_sections()

@click.command()
@click.option('-t', '--template', default='DEFAULT', show_default='True', help=f'select a HTML template: {sections}')
@click.argument('md_file', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), required=True, nargs=1)
@click.argument('output_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True), required=False, nargs=1)
def main(template, md_file, output_dir):
    md_file = Path(md_file).resolve()
    if not output_dir:
        output_dir = md_file.parent
    else:
        output_dir = Path(output_dir).resolve()
    if template not in sections and template != 'DEFAULT':
        print(f'Error: template {template} is not exist.')
        sys.exit()
    
    config = get_config(template)
    html_file, styles_dir, meta_data = md2html(md_file, output_dir, config)
    # pdf_file = output_dir / (md_file.stem + '.pdf')
    name_parts = [meta_data['role'], meta_data['document'], meta_data['date'], meta_data['author'], meta_data['subject']]
    # pdf_file = output_dir / ('-'.join(name_parts) + '.pdf')
    pdf_file = os.path.join(output_dir, '-'.join(name_parts) + '.pdf')

    if config['generate_pdf']:
        html2pdf(html_file, pdf_file)

    if config['generate_html'] == 'False':
        print(f'Delete {html_file}')
        os.remove(html_file)
        print(f'Delete {styles_dir}')
        rmtree(styles_dir)

if __name__ == '__main__':
    main()