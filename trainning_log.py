# markdown to pdf

import sys
from string import Template
import markdown
import pdfkit

html_template = 'template-coach.html'
extensions = ['toc', 'tables', 'fenced_code', 'codehilite', 'footnotes', 'meta', 'nl2br']

if sys.argv[1:]:
    md_file = sys.argv[1]
else:
    print("Please input markdown file")
    exit()

html_file = md_file.replace(".md", ".html")

with open(md_file, 'r', encoding="utf-8") as input_file:
    md_content = input_file.read()
#    html = markdown.markdown(md, output_format='html5', extensions=extensions)
    md = markdown.Markdown(output_format='html5', extensions=extensions)
    html = md.convert(md_content)
    title = md.Meta['title'][0]
    author = md.Meta['author'][0]
    date = md.Meta['date'][0]
    task = md.Meta['task'][0]

with open(html_template, 'r', encoding="utf-8") as template_file:
    template_html = Template(template_file.read())
    full_html = template_html.safe_substitute(title=title, author=author, date=date, task=task, content=html)

with open(html_file, 'w', encoding="utf-8") as output_file:
   output_file.write(full_html) 

pdf_file = html_file.replace(".html", ".pdf")

options = {
    'encoding': 'utf-8',
    'margin-top': '0px',
    'margin-right': '0px',
    'margin-bottom': '0px',
    'margin-left': '0px',
    'no-outline': None,
    'enable-local-file-access': None
}

pdfkit.from_file(html_file, pdf_file, options=options)