# Markdown file coverted to html and pdf file with python-markdown2 and wkhtmltopdf
# Author: Hdaojin
# Date: 2021-12-05
# Update: 2021-12-05
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

Version = 1.0

template_dir = 'template'
template_file_name = 'template.html'
template_file_css = 'template.css'
mdcss_dir = 'mdcss'
config_file = 'config.ini'


def get_sections():
    cfg = ConfigParser()
    cfg.read(config_file)
    sections = cfg.sections()
    return sections


def get_config(section):
    cfg = ConfigParser()
    cfg.read(config_file)
    template = cfg.get(section, 'Template')
    markdown_css = cfg.get(section, 'Markdown_CSS')
    custom_css = cfg.get(section, 'Custom_CSS')
    Generate_HTML = cfg.getboolean(section, 'Generate_HTML')
    Generate_PDF = cfg.getboolean(section, 'Generate_PDF')
    return template, markdown_css, custom_css, Generate_HTML, Generate_PDF


def md2html(md_file, template, markdown_css, custom_css):
    extensions = ['metadata', 'tables', 'code-friendly', 'fenced-code-blocks', 'break-on-newline']
    markdown_css_path = os.path.join(mdcss_dir, markdown_css)
    custom_css_path = os.path.join(mdcss_dir, custom_css)
    template_css_path = os.path.join(template_dir, template, template_file_css)
    template_path = os.path.join(template_dir, template, template_file_name)
    md_file_dir = md_file.parent
    html_file_name = md_file.stem + '.html'

    css_dir = os.path.join(md_file_dir, 'css')
    if not os.path.exists(css_dir):
        os.mkdir(css_dir)
    for css in markdown_css_path, custom_css_path, template_css_path:
        copy(css, css_dir)
    markdown_css = os.path.join('css', markdown_css)
    custom_css = os.path.join('css', custom_css)
    template_css = os.path.join('css', template_file_css)
    
    with open(md_file, 'r', encoding="utf-8") as mf:
        html = markdown2.markdown(mf.read(), extras=extensions)
        title = html.metadata['Title']
        author = html.metadata['Author']
        date = html.metadata['Date']
        task = html.metadata['Task']
    with open(template_path, 'r', encoding="utf-8") as tf:
        template_html = Template(tf.read())
        full_html = template_html.safe_substitute(markdown_css=markdown_css, custom_css=custom_css, template_css=template_css, title=title, author=author, date=date, task=task, content=html)
    html_file = os.path.join(md_file_dir, html_file_name)
    with open(html_file, 'w', encoding="utf-8") as hf:
        hf.write(full_html)
    return html_file, css_dir


def html2pdf(html_file, pdf_file):
    options = {
        'encoding': "UTF-8",
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'page-size': 'A4',
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ],
        'no-outline': None,
        'enable-local-file-access': None
    }
    pdfkit.from_file(html_file, pdf_file, options=options)
    return


def get_args():
    parser = argparse.ArgumentParser(
        description="Markdown file coverted to html and pdf file with python-markdown2 and wkhtmltopdf", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {}'.format(str(Version)))
    parser.add_argument('-t', '--template', required=False, nargs='?', default='DEFAULT',
                        help='select a HTML template: {}\n(default: %(default)s)'.format(get_sections()))
    parser.add_argument('-i', required=True,
                        metavar='markdown_file', help='input a markdown file')
    parser.add_argument('-o', metavar='directory',
                        default='.', help='output directory\n(default: current directory)')
    args = parser.parse_args()

    md_file = Path(args.i)
    output_dir = Path(args.o)
    template = args.template

    if not md_file.is_file():
        print('Error: {} not found'.format(md_file))
        sys.exit(1)
    if not output_dir.is_dir():
        output_dir.mkdir()
    if template not in get_sections():
        print('Warnning: template \'{}\' not found, use \'DEFAULT\''.format(template))
        template = 'DEFAULT'
    return md_file, output_dir, template

if __name__ == '__main__':
    md_file, output_dir, template = get_args()
    template, markdown_css, custom_css, Generate_HTML, Generate_PDF = get_config(template)
    html_file, css_dir = md2html(md_file, template, markdown_css, custom_css)

    if Generate_PDF == True:
        pdf_file_name = md_file.name.replace('.md', '.pdf')
        pdf_file = os.path.join(output_dir, pdf_file_name)
        html2pdf(html_file=html_file, pdf_file=pdf_file)

    if Generate_HTML == False:
        print(html_file)
        print(css_dir)
        os.remove(html_file)
        rmtree(css_dir)
