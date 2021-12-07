# Markdown file coverted to html and pdf file with python-markdown2 and wkhtmltopdf
# Author: Hdaojin
# Date: 2021-12-05
# Version: 1.0
# Update: 2021-12-05

import sys
import os
from getopt import getopt
from configparser import ConfigParser
import markdown2
# import pdfkit

template_dir = 'template'
template_file_name = 'template.html'
mdcss_dir = 'mdcss'
config_file = 'config.ini'



def get_default_config(config_file):
    cfg = ConfigParser()
    cfg.read(config_file)
    template = cfg.get('Default', 'Template')
    template_path = os.path.join(template_dir, template, template_file_name)
    markdown_css = cfg.get('Default', 'Markdown_CSS')
    makrdown_css_path = os.path.join(mdcss_dir, markdown_css)
    custom_css = cfg.get('Default', 'Custom_CSS')
    custom_css_path = os.path.join(mdcss_dir, custom_css)
    Generate_HTML = cfg.get('Default', 'Generate_HTML')
    return template_path, makrdown_css_path, custom_css_path, Generate_HTML

def get_config(sections):
    cfg = ConfigParser()
    cfg.read(config_file)
    template = cfg.get(sections, 'Template')
    template_path = os.path.join(template_dir, template, template_file_name)
    markdown_css = cfg.get(sections, 'Markdown_CSS')
    makrdown_css_path = os.path.join(mdcss_dir, markdown_css)
    custom_css = cfg.get(sections, 'Custom_CSS')
    custom_css_path = os.path.join(mdcss_dir, custom_css)
    Generate_HTML = cfg.get(sections, 'Generate_HTML')
    return template_path, makrdown_css_path, custom_css_path, Generate_HTML

def md2html(md_file):
    extensions = ['metadata']
    template = 'template.html'
    with open(md_file, 'r',encoding="utf-8") as f:
        html = markdown2.markdown(f.read(), extras=extensions)
        title = html.metadata['Title']
        author = html.metadata['Author']
        date = html.metadata['Date']
        task = html.metadata['Task']
        with open('template', 'w',encoding="utf-8") as f:
            f.write(html)


        return html, html.metadata

def html2pdf(html_file):
    pdfkit.from_file(html_file, 'test.pdf')

def main(argv):
    try:
        opts, args = getopt(argv, 'ht:', ['help', 'template='])
    except getopt.GetoptError:
        print('trainning_log2.py -t <template>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('trainning_log2.py -t <template>')
            sys.exit()
        elif opt in ('-t', '--template'):
            sections = arg
    template_path, makrdown_css_path, custom_css_path, Generate_HTML = get_default_config(config_file)
    if Generate_HTML == 'True':
        html2pdf(template_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 trainning_log2.py trainning_log.md')
        sys.exit(1)
    html, metadata = md2html(sys.argv[1])
    print(metadata)
