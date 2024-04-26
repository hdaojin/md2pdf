from weasyprint import HTML

from pathlib import Path

base_dir = Path(__file__).resolve().parent

html_file = base_dir / 'test' / 'Linux-Apache-Base.html'
output_file = base_dir / 'test' / 'Linux-Apache-Base.pdf'

HTML(html_file).write_pdf(output_file)