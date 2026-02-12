import markdown2


class MarkdownToHTMLConverter:
    """
    A class to convert markdown content to HTML using the markdown2 library.
    It supports various extras for markdown2 to enhance the conversion process.
    """
    def __init__(self, md_content: str) -> dict:
        """
        Initialize the converter with markdown content.

        :param md_content: str, the markdown content to be converted.
        """
        self.md_content = md_content

        
    def md2convert(self):
        md2_extras = [
            # "breaks", # Convert '\n' in paragraphs into <br>
        "code-friendly", # Disable _ and __ for em and strong
        "cuddled-lists", # Allow lists to be cuddled to the preceding paragraph
        "fenced-code-blocks", # Allow code blocks to be fenced by ```
        "metadata", # Parse metadata at the beginning of the markdown content
        "footnotes", # Parse footnotes
        "highlightjs-lang", # Highlight code blocks with language
        "numbering", # Create counters to number tables,figures, equations and graphs
        "tables", # Parse tables
        "toc", # Generate a table of contents
        "header-ids", # Adds "id" attribute to headers
        "task_list", # Parse task lists
        ]
        # Convert markdown to html using markdown2
        html_content = markdown2.markdown(self.md_content, extras=md2_extras)
        # Parse the metadata from the markdown content and lowercase the keys
        html_metadata = html_content.metadata
        html_metadata = {k.lower(): v for k, v in html_metadata.items()} if html_metadata else {}
        
        # Parse the table of contents from the markdown content
        # html_toc = html_content.toc_html

        # Return the html content and metadata
        return html_content, html_metadata

