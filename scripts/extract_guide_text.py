"""
Extract text content from guide pages for AI review.

This script extracts all text content from guide HTML templates,
removing Jinja2 syntax and HTML tags to produce clean text files
that can be sent to an AI writing team for review.

Usage:
    python scripts/extract_guide_text.py [guide_name]
    
    If no guide_name is provided, extracts all guides.
    
Examples:
    python scripts/extract_guide_text.py what-is-a-prop-firm
    python scripts/extract_guide_text.py
"""

import os
import re
from pathlib import Path
from html.parser import HTMLParser
from io import StringIO


class MLStripper(HTMLParser):
    """Strip HTML tags from content."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()
        
    def handle_data(self, data):
        self.text.write(data)
        
    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    """Remove HTML tags from a string."""
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def extract_jinja_block(content, block_name):
    """Extract content from a Jinja2 block."""
    pattern = rf'{{% block {block_name} %}}(.*?){{% endblock %}}'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def clean_text(text):
    """Clean up extracted text."""
    if not text:
        return ""
    
    # Remove Jinja2 variables like {{ meta_desc }}
    text = re.sub(r'\{\{.*?\}\}', '', text)
    
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Strip HTML tags
    text = strip_tags(text)
    
    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Collapse spaces
    text = text.strip()
    
    return text


def extract_guide_text(guide_path):
    """Extract all text content from a guide HTML file."""
    with open(guide_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    guide_name = Path(guide_path).stem
    
    # Extract blocks
    title = extract_jinja_block(content, 'guide_title')
    subtitle = extract_jinja_block(content, 'guide_subtitle')
    trust = extract_jinja_block(content, 'hero_trust')
    main_content = extract_jinja_block(content, 'guide_content')
    faq = extract_jinja_block(content, 'guide_faq')
    
    # Build output
    output = []
    output.append("=" * 80)
    output.append(f"GUIDE: {guide_name}")
    output.append("=" * 80)
    output.append("")
    
    if title:
        output.append("TITLE:")
        output.append(clean_text(title))
        output.append("")
    
    if subtitle:
        output.append("SUBTITLE:")
        output.append(clean_text(subtitle))
        output.append("")
    
    if trust:
        output.append("TRUST BADGE:")
        output.append(clean_text(trust))
        output.append("")
    
    if main_content:
        output.append("MAIN CONTENT:")
        output.append("-" * 80)
        output.append(clean_text(main_content))
        output.append("")
    
    if faq:
        output.append("FAQ SECTION:")
        output.append("-" * 80)
        output.append(clean_text(faq))
        output.append("")
    
    # Extract structured FAQ from JSON-LD block
    faq_items = extract_jinja_block(content, 'faq_items')
    if faq_items:
        output.append("STRUCTURED FAQ (Schema.org):")
        output.append("-" * 80)
        # Parse the JSON-LD FAQ items
        try:
            import json
            # Remove trailing {% endblock %} if present
            faq_items = faq_items.replace('{% endblock %}', '')
            faq_data = json.loads(faq_items)
            for item in faq_data:
                q = item.get('name', '')
                a = item.get('acceptedAnswer', {}).get('text', '')
                output.append(f"Q: {q}")
                output.append(f"A: {a}")
                output.append("")
        except:
            output.append(clean_text(faq_items))
        output.append("")
    
    return "\n".join(output)


def main():
    import sys
    
    guides_dir = Path(__file__).parent.parent / 'templates' / 'guides'
    output_dir = Path(__file__).parent.parent / 'docs' / 'guide_text_extracts'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine which guides to process
    if len(sys.argv) > 1:
        guide_name = sys.argv[1]
        if not guide_name.endswith('.html'):
            guide_name += '.html'
        guide_files = [guides_dir / guide_name]
    else:
        # Get all guide files except index.html and guide_base.html
        guide_files = [
            f for f in guides_dir.glob('*.html')
            if f.name not in ('index.html', 'guide_base.html')
        ]
    
    # Process each guide
    for guide_file in guide_files:
        if not guide_file.exists():
            print(f"❌ Guide not found: {guide_file.name}")
            continue
            
        print(f"📄 Extracting: {guide_file.name}")
        
        try:
            text_content = extract_guide_text(guide_file)
            
            # Write to output file
            output_file = output_dir / f"{guide_file.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            print(f"   ✅ Saved to: {output_file}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✨ Done! Text files saved to: {output_dir}")
    print(f"\nYou can now send these .txt files to your AI writing team for review.")


if __name__ == '__main__':
    main()
