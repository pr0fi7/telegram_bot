from docx import Document
from io import BytesIO

def create_docx_from_markdown_simple(markdown_text, output_path):
    """
    Create a DOCX file from Markdown text with basic support for headings and paragraphs.
    
    This simple parser only handles:
      - Headings (#, ##, ###)
      - Paragraphs (other lines)
      
    For full Markdown support, consider using pypandoc.
    """
    document = Document()
    
    # Split the markdown text into lines.
    for line in markdown_text.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue  # Skip empty lines
        
        # Check for headings
        if stripped_line.startswith('### '):
            document.add_heading(stripped_line[4:].strip(), level=3)
        elif stripped_line.startswith('## '):
            document.add_heading(stripped_line[3:].strip(), level=2)
        elif stripped_line.startswith('# '):
            document.add_heading(stripped_line[2:].strip(), level=1)
        else:
            document.add_paragraph(stripped_line)
    
    # Write the document to a BytesIO object instead of a local file
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer