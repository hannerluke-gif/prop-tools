"""
Update guide HTML templates from edited text files.

After getting text reviewed by AI writing team, save the edited content
back to the .txt files, then run this script to update the HTML templates.

Usage:
    python scripts/update_guide_from_text.py [guide_name]
    
    If no guide_name is provided, updates all guides.
    
Examples:
    python scripts/update_guide_from_text.py what-is-a-prop-firm
    python scripts/update_guide_from_text.py
    
Workflow:
    1. Extract text: python scripts/extract_guide_text.py
    2. Send .txt files to AI writing team
    3. Receive edited .txt files
    4. Save edited files to docs/guide_text_extracts/
    5. Run this script: python scripts/update_guide_from_text.py
"""

import os
import re
from pathlib import Path


def parse_text_file(text_path):
    """Parse an extracted text file into structured sections."""
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = {}
    
    # Extract title
    title_match = re.search(r'TITLE:\s*\n(.+?)(?=\n\n|\nSUBTITLE:|\Z)', content, re.DOTALL)
    if title_match:
        sections['title'] = title_match.group(1).strip()
    
    # Extract subtitle
    subtitle_match = re.search(r'SUBTITLE:\s*\n(.+?)(?=\n\n|\nTRUST BADGE:|\nMAIN CONTENT:|\Z)', content, re.DOTALL)
    if subtitle_match:
        sections['subtitle'] = subtitle_match.group(1).strip()
    
    # Extract main content sections
    main_content_match = re.search(r'MAIN CONTENT:\s*\n-+\s*\n(.+?)(?=\n\nFAQ SECTION:|\n\nSTRUCTURED FAQ|\Z)', content, re.DOTALL)
    if main_content_match:
        sections['main_content'] = main_content_match.group(1).strip()
    
    # Extract FAQ section
    faq_match = re.search(r'FAQ SECTION:\s*\n-+\s*\n(.+?)(?=\n\nSTRUCTURED FAQ|\Z)', content, re.DOTALL)
    if faq_match:
        sections['faq'] = faq_match.group(1).strip()
    
    # Extract structured FAQ (Schema.org)
    structured_faq_match = re.search(r'STRUCTURED FAQ \(Schema\.org\):\s*\n-+\s*\n(.+)', content, re.DOTALL)
    if structured_faq_match:
        # Parse Q&A pairs
        faq_text = structured_faq_match.group(1).strip()
        sections['structured_faq'] = []
        
        # Split by Q: markers
        qa_pairs = re.split(r'\n\n(?=Q: )', faq_text)
        for qa in qa_pairs:
            q_match = re.search(r'Q: (.+?)\nA: (.+)', qa, re.DOTALL)
            if q_match:
                sections['structured_faq'].append({
                    'question': q_match.group(1).strip(),
                    'answer': q_match.group(2).strip()
                })
    
    return sections


def parse_faq_content(faq_text):
    """Parse FAQ section text into structured Q&A pairs."""
    faq_items = []
    lines = faq_text.split('\n')
    
    # Skip the "Common questions" heading
    lines = [line for line in lines if line.strip() and line.strip().lower() != 'common questions']
    
    current_q = None
    current_a = []
    
    for line in lines:
        line = line.strip()
        if not line:
            # Empty line might separate Q&A pairs
            if current_q and current_a:
                faq_items.append({
                    'question': current_q,
                    'answer': ' '.join(current_a)
                })
                current_q = None
                current_a = []
            continue
        
        # Check if this looks like a question (ends with ?)
        if line.endswith('?'):
            # Save previous Q&A if exists
            if current_q and current_a:
                faq_items.append({
                    'question': current_q,
                    'answer': ' '.join(current_a)
                })
            current_q = line
            current_a = []
        else:
            # This is part of the answer
            current_a.append(line)
    
    # Don't forget the last Q&A pair
    if current_q and current_a:
        faq_items.append({
            'question': current_q,
            'answer': ' '.join(current_a)
        })
    
    return faq_items


def parse_main_content(text):
    """Parse main content text into HTML structure."""
    # Split by section headers (lines that look like headings)
    sections = []
    current_section = None
    
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check if this looks like a heading (not starting with special chars)
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
        
        # If line doesn't start with bullet/number and next line is empty or starts with bullet/number
        # or if it's a short line followed by content, it's likely a heading
        if line and not re.match(r'^[•\-\*\d]', line):
            # Start new section
            if current_section:
                sections.append(current_section)
            
            current_section = {
                'title': line,
                'content': [],
                'type': None  # Will be 'list' or 'steps'
            }
            i += 1
            continue
        
        # Add content to current section
        if current_section:
            # Detect list items
            if re.match(r'^[\d]+\.', line):
                if current_section['type'] != 'steps':
                    current_section['type'] = 'steps'
                # Remove number prefix
                item = re.sub(r'^[\d]+\.\s*', '', line)
                current_section['content'].append(item)
            elif re.match(r'^[•\-\*]', line):
                if current_section['type'] != 'list':
                    current_section['type'] = 'list'
                # Remove bullet
                item = re.sub(r'^[•\-\*]\s*', '', line)
                current_section['content'].append(item)
            elif line:
                # Regular paragraph text
                current_section['content'].append(line)
        
        i += 1
    
    # Add last section
    if current_section:
        sections.append(current_section)
    
    return sections


def generate_main_content_html(sections):
    """Generate HTML for main content sections."""
    html_parts = []
    
    for section in sections:
        html_parts.append('  <div class="guide__section animation-ready fade-in">')
        html_parts.append('    <div class="guide__card">')
        html_parts.append(f'      <h2 class="guide__section-title">{section["title"]}</h2>')
        
        if section['type'] == 'steps':
            html_parts.append('      <ol class="guide__steps">')
            for item in section['content']:
                html_parts.append(f'        <li>{item}</li>')
            html_parts.append('      </ol>')
        elif section['type'] == 'list':
            html_parts.append('      <ul class="guide__bullets">')
            for item in section['content']:
                # Check if item has bold text (word: definition pattern)
                if ':' in item and item.index(':') < 30:
                    parts = item.split(':', 1)
                    html_parts.append(f'        <li><strong>{parts[0]}:</strong>{parts[1]}</li>')
                else:
                    html_parts.append(f'        <li>{item}</li>')
            html_parts.append('      </ul>')
        else:
            # Paragraph content
            for para in section['content']:
                html_parts.append(f'      <p>{para}</p>')
        
        html_parts.append('    </div>')
        html_parts.append('  </div>')
    
    return '\n'.join(html_parts)


def generate_faq_html(faq_items):
    """Generate HTML for FAQ section."""
    html_parts = []
    html_parts.append('<div class="guide__faq-section guide__faq-section--spacious">')
    html_parts.append('  <h2 class="guide__section-title">Common questions</h2>')
    
    for item in faq_items:
        html_parts.append('  <details class="guide__faq" role="group">')
        html_parts.append('    <summary class="guide__faq__summary">')
        html_parts.append(f'      <span class="h6 mb-0 d-inline-block">{item["question"]}</span>')
        html_parts.append('    </summary>')
        html_parts.append('    <div class="guide__faq__content">')
        html_parts.append(f'      {item["answer"]}')
        html_parts.append('    </div>')
        html_parts.append('  </details>')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)


def update_guide_html(guide_path, sections):
    """Update guide HTML template with new content from sections."""
    with open(guide_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update title
    if 'title' in sections:
        html_content = re.sub(
            r'{% block guide_title %}.*?{% endblock %}',
            f'{{% block guide_title %}}{sections["title"]}{{% endblock %}}',
            html_content,
            flags=re.DOTALL
        )
    
    # Update subtitle
    if 'subtitle' in sections:
        html_content = re.sub(
            r'{% block guide_subtitle %}.*?{% endblock %}',
            f'{{% block guide_subtitle %}}\n{sections["subtitle"]}\n{{% endblock %}}',
            html_content,
            flags=re.DOTALL
        )
    
    # Update main content
    if 'main_content' in sections:
        parsed_sections = parse_main_content(sections['main_content'])
        new_html = generate_main_content_html(parsed_sections)
        html_content = re.sub(
            r'{% block guide_content %}.*?{% endblock %}',
            f'{{% block guide_content %}}\n{new_html}\n{{% endblock %}}',
            html_content,
            flags=re.DOTALL
        )
    
    # Update FAQ content (visual FAQ section)
    if 'faq' in sections:
        faq_items = parse_faq_content(sections['faq'])
        if faq_items:
            new_faq_html = generate_faq_html(faq_items)
            
            # Check if guide_faq block exists
            if re.search(r'{% block guide_faq %}', html_content):
                # Update existing block
                html_content = re.sub(
                    r'{% block guide_faq %}.*?{% endblock %}',
                    lambda m: f'{{% block guide_faq %}}\n{new_faq_html}\n{{% endblock %}}',
                    html_content,
                    flags=re.DOTALL
                )
            else:
                # Insert new block before next_links or at the end of the file
                # Find a good insertion point - after guide_content and before next_links
                insert_pattern = r'({% endblock %}\s*)({% block next_links %})'
                if re.search(insert_pattern, html_content):
                    html_content = re.sub(
                        insert_pattern,
                        rf'\1\n{{% block guide_faq %}}\n{new_faq_html}\n{{% endblock %}}\n\n\2',
                        html_content
                    )
                else:
                    # Try before the final endblock or end of file
                    # Insert before {% block next_links %}
                    next_links_match = re.search(r'{% block next_links %}', html_content)
                    if next_links_match:
                        pos = next_links_match.start()
                        html_content = (
                            html_content[:pos] +
                            f'{{% block guide_faq %}}\n{new_faq_html}\n{{% endblock %}}\n\n' +
                            html_content[pos:]
                        )
    
    # Update structured FAQ (Schema.org)
    if 'structured_faq' in sections and sections['structured_faq']:
        import json
        faq_items = []
        for qa in sections['structured_faq']:
            faq_items.append({
                "@type": "Question",
                "name": qa['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa['answer']
                }
            })
        
        faq_json = json.dumps(faq_items, indent=0).replace('\n', '')
        # Format it nicely
        faq_json = json.dumps(faq_items, indent=2)
        # Remove outer array brackets for the template format
        faq_json = faq_json[1:-1]  # Remove [ and ]
        
        # Use a lambda to avoid regex interpretation of backslashes in the replacement
        html_content = re.sub(
            r'{% block faq_items %}\[.*?\]{% endblock %}',
            lambda m: f'{{% block faq_items %}}[{faq_json}]{{% endblock %}}',
            html_content,
            flags=re.DOTALL
        )
    
    # Write updated content
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    import sys
    
    guides_dir = Path(__file__).parent.parent / 'templates' / 'guides'
    text_dir = Path(__file__).parent.parent / 'docs' / 'guide_text_extracts'
    
    # Determine which guides to process
    if len(sys.argv) > 1:
        guide_name = sys.argv[1]
        if not guide_name.endswith('.txt'):
            guide_name += '.txt'
        text_files = [text_dir / guide_name]
    else:
        # Get all text files
        text_files = list(text_dir.glob('*.txt'))
    
    if not text_files:
        print("❌ No text files found in docs/guide_text_extracts/")
        return
    
    print("🔄 Updating guide HTML templates from edited text files...\n")
    
    # Process each text file
    for text_file in text_files:
        if not text_file.exists():
            print(f"❌ Text file not found: {text_file.name}")
            continue
        
        guide_name = text_file.stem
        guide_html = guides_dir / f"{guide_name}.html"
        
        if not guide_html.exists():
            print(f"❌ Guide HTML not found: {guide_html.name}")
            continue
        
        print(f"📝 Updating: {guide_name}")
        
        try:
            # Parse text file
            sections = parse_text_file(text_file)
            
            # Update HTML
            update_guide_html(guide_html, sections)
            
            print(f"   ✅ Updated: {guide_html.name}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✨ Done! Guide templates have been updated.")
    print(f"\n💡 Review the changes and test the pages before deploying.")


if __name__ == '__main__':
    main()
