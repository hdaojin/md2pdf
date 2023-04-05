# Markdown file coverted to html and pdf file with python-markdown2 and wkhtmltopdf
# Author: Hdaojin
# Date: 2021-12-05
# Update: 2021-12-05
__version__ = 1.0
__author__ = 'Hdaojin'
__date__ = '2021-12-05'

import markdown2
from configparser import ConfigParser
import argparse
import os
import sys
from pathlib import Path
from pathlib import PurePath
from shutil import copy, rmtree
from string import Template
import pdfkit
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


TEMPLATE_DIR = Path('template')
TEMPLATE_FILE_NAME = 'template.html'
TEMPLATE_FILE_CSS = 'template.css'
MDCSS_DIR = Path('styles')
CONFIG_FILE = 'config.ini'


def get_sections():
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    sections = cfg.sections()
    return sections


def get_config(section):
    cfg = ConfigParser()
    cfg.read(CONFIG_FILE)
    template = cfg.get(section, 'template_name')
    markdown_css = cfg.get(section, 'markdown_css')
    custom_css = cfg.get(section, 'markdown_custom_css')
    code_highlight_css = cfg.get(section, 'code_highlight_css')
    generate_html = cfg.getboolean(section, 'generate_html')
    generate_pdf = cfg.getboolean(section, 'generate_pdf')
    return template, markdown_css, custom_css, code_highlight_css, generate_html, generate_pdf


def md2html(md_file, template, markdown_css, custom_css, code_highlight_css):
    extensions = ['metadata', 'tables', 'code-friendly',
                  'fenced-code-blocks', 'break-on-newline', 'footnotes']
    markdown_css_path = os.path.join(MDCSS_DIR, markdown_css)
    custom_css_path = os.path.join(MDCSS_DIR, custom_css)
    code_highlight_css_path = os.path.join(MDCSS_DIR, code_highlight_css)
    template_css_path = os.path.join(TEMPLATE_DIR, template, TEMPLATE_FILE_CSS)
    template_path = os.path.join(TEMPLATE_DIR, template, TEMPLATE_FILE_NAME)
    md_file_dir = md_file.parent
    html_file_name = md_file.stem + '.html'

    css_dir = os.path.join(md_file_dir, 'css')
    if not os.path.exists(css_dir):
        os.mkdir(css_dir)
    for css in markdown_css_path, custom_css_path, code_highlight_css_path, template_css_path:
        copy(css, css_dir)
    markdown_css = os.path.join('css', markdown_css)
    custom_css = os.path.join('css', custom_css)
    code_highlight_css = os.path.join('css', code_highlight_css)
    template_css = os.path.join('css', TEMPLATE_FILE_CSS)

    with open(md_file, 'r', encoding="utf-8") as mf:
        html = markdown2.markdown(mf.read(), extras=extensions)
        title = html.metadata['Head']
        author = html.metadata['Author']
        role = html.metadata['Role']
        date = html.metadata['Date']
        subject = html.metadata['Subject']
        task = html.metadata['Task']
    with open(template_path, 'r', encoding="utf-8") as tf:
        template_html = Template(tf.read())
        full_html = template_html.safe_substitute(
            markdown_css=markdown_css,
            custom_css=custom_css,
            code_highlight_css=code_highlight_css,
            template_css=template_css,
            title=title,
            author=author,
            role=role,
            date=date,
            subject=subject,
            task=task,
            content=html)
    html_file = os.path.join(md_file_dir, html_file_name)
    with open(html_file, 'w', encoding="utf-8") as hf:
        hf.write(full_html)
    return title, author, role, date, subject, task, html_file, css_dir


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


def get_args():
    parser = argparse.ArgumentParser(
        description="Markdown file coverted to html and pdf file with python-markdown2 and wkhtmltopdf",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(str(__version__)))
    parser.add_argument('-t', '--template', required=False, nargs='?', const='DEFAULT', default='DEFAULT',
                        help='select a HTML template: {}\n(default: %(default)s)'.format(get_sections()))
    parser.add_argument('-i', required=True,
                        metavar='markdown_file', help='input a markdown file')
    # parser.add_argument('-o', metavar='directory',
    #                    default='.', help='output directory\n(default: The directory where markdown file is located)')
    parser.add_argument('-o', metavar='directory',
                        help='output directory\n(default: The directory where markdown file is located)')
    args = parser.parse_args()

    md_file = Path(args.i)
    if not args.o:
        output_dir = md_file.resolve().parent
    else:
        output_dir = args.o
    output_dir = Path(output_dir)
    template = args.template

    if not md_file.is_file():
        print('Error: {} not found'.format(md_file))
        sys.exit(1)
    if not output_dir.is_dir():
        output_dir.mkdir()
    if template not in get_sections() and template != 'DEFAULT':
        print('Warnning: template \'{}\' not found, use \'DEFAULT\''.format(template))
        template = 'DEFAULT'
    return md_file, output_dir, template


if __name__ == '__main__':
    md_file, output_dir, template = get_args()
    template, markdown_css, custom_css, code_highlight_css, generate_html, generate_pdf = get_config(
        template)
    title, author, role, date, subject, task, html_file, css_dir = md2html(
        md_file, template, markdown_css, custom_css, code_highlight_css)

    if generate_pdf == True:
        # pdf_file_name = md_file.name.replace('.md', '.pdf')
        # pdf_file_name = role + '-' + title + '-' + \
        #     date + '-' + author + '-' + subject + '.pdf'
        pdf_file_name = '-'.join([role, title, date, author, subject]) + '.pdf'
        pdf_file = os.path.join(output_dir, pdf_file_name)
        html2pdf(html_file=html_file, pdf_file=pdf_file)

    if generate_html == False:
        print('Delete ', html_file)
        os.remove(html_file)
        print('Delete ', css_dir)
        rmtree(css_dir)
