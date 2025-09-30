#!/usr/bin/env python3
"""
Button Spacing Validator for Guide Templates

This script checks all guide templates for proper button spacing patterns.
Run this before committing changes to ensure consistency.
"""

import os
import re
from pathlib import Path

def check_button_spacing():
    """Check all guide templates for proper button spacing."""
    guides_dir = Path("templates/guides")
    issues = []
    
    # Pattern to find multiple buttons without proper spacing
    # Look for containers with multiple buttons that don't use d-flex gap-3
    button_pattern = r'<div[^>]*class="[^"]*mt-3[^"]*"[^>]*>.*?<a[^>]*class="[^"]*btn[^"]*".*?<a[^>]*class="[^"]*btn[^"]*"'
    proper_spacing_pattern = r'<div[^>]*class="[^"]*mt-3[^"]*d-flex[^"]*flex-wrap[^"]*gap-3[^"]*"'
    
    for guide_file in guides_dir.glob("*.html"):
        if guide_file.name == "guide_base.html":
            continue
            
        try:
            content = guide_file.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = guide_file.read_text(encoding='utf-8', errors='ignore')
        
        # Remove whitespace/newlines to make pattern matching easier
        content_single_line = re.sub(r'\s+', ' ', content)
        
        # Find multiple buttons in the same container
        multiple_buttons = re.findall(button_pattern, content_single_line, re.DOTALL | re.IGNORECASE)
        
        if multiple_buttons:
            # Check if proper spacing is used
            if not re.search(proper_spacing_pattern, content_single_line, re.IGNORECASE):
                issues.append({
                    'file': guide_file.name,
                    'issue': 'Multiple buttons found without proper d-flex gap-3 spacing',
                    'matches': len(multiple_buttons)
                })
    
    return issues

def main():
    """Main function to run the validation."""
    print("🔍 Checking button spacing in guide templates...")
    
    issues = check_button_spacing()
    
    if not issues:
        print("✅ All guide templates have proper button spacing!")
        return 0
    
    print(f"❌ Found {len(issues)} files with button spacing issues:")
    print()
    
    for issue in issues:
        print(f"📁 {issue['file']}")
        print(f"   {issue['issue']}")
        print(f"   Found {issue['matches']} instance(s)")
        print()
    
    print("💡 Fix by adding 'd-flex flex-wrap gap-3' to button containers:")
    print('   <div class="mt-3 d-flex flex-wrap gap-3">')
    print()
    
    return 1

if __name__ == "__main__":
    exit(main())