# Guide Content Update Workflow

This guide shows how to extract guide text for AI review and update the HTML templates with edited content.

## 📤 Export for Review

### Extract all guides:
```bash
python scripts/extract_guide_text.py
```

### Extract a specific guide:
```bash
python scripts/extract_guide_text.py what-is-a-prop-firm
```

**Output:** Clean `.txt` files in `docs/guide_text_extracts/`

---

## ✏️ Get Content Reviewed

1. Send the `.txt` files to your AI writing team
2. Have them review for:
   - Landing page optimization
   - Clarity and engagement
   - Tone and voice consistency
   - SEO and conversion best practices
   - Grammar and readability

3. Receive edited `.txt` files back

---

## 📥 Update HTML Templates

### Method 1: Automated Script (Recommended)

Save the edited `.txt` files back to `docs/guide_text_extracts/` with the same filenames, then run:

```bash
# Update all guides
python scripts/update_guide_from_text.py

# Update specific guide
python scripts/update_guide_from_text.py what-is-a-prop-firm
```

The script will:
- ✅ Parse the edited text
- ✅ Update titles, subtitles, and content
- ✅ Preserve HTML structure and Jinja2 blocks
- ✅ Update FAQ schema.org data

### Method 2: Manual Chat (For single guides)

Just paste the edited text in chat:

> "Here's the reviewed text for the 'what-is-a-prop-firm' guide: [paste text]"

GitHub Copilot will update the HTML template for you.

---

## 🧪 Testing After Updates

1. **Check the Flask dev server** to see your changes live
2. **Review the rendered page** for formatting issues
3. **Validate the content** matches the edited text
4. **Test all internal links** still work
5. **Check FAQ accordion** functionality

---

## 📝 Text File Format

The extracted text follows this structure:

```
================================================================================
GUIDE: guide-name
================================================================================

TITLE:
Main Title Here

SUBTITLE:
Subtitle description here

MAIN CONTENT:
--------------------------------------------------------------------------------
Section Heading
- Bullet point 1
- Bullet point 2

Another Section
1. Numbered item 1
2. Numbered item 2

FAQ SECTION:
--------------------------------------------------------------------------------
Common questions

Question 1?
Answer to question 1

Question 2?
Answer to question 2

STRUCTURED FAQ (Schema.org):
--------------------------------------------------------------------------------
Q: Schema FAQ question 1?
A: Schema FAQ answer 1

Q: Schema FAQ question 2?
A: Schema FAQ answer 2
```

### Editing Tips

- Keep section headings on their own lines
- Use `-` or `•` for bullet lists
- Use `1.` `2.` etc for numbered lists  
- For definition lists, use `Term: definition` format (gets bolded automatically)
- Blank lines separate sections
- Keep FAQ format as `Q:` and `A:` for structured FAQs

---

## 🔄 Full Workflow Example

```bash
# 1. Extract text from all guides
python scripts/extract_guide_text.py

# 2. Send files in docs/guide_text_extracts/ to writing team
# ... (external review process) ...

# 3. Save edited files back to docs/guide_text_extracts/

# 4. Update HTML templates
python scripts/update_guide_from_text.py

# 5. Review changes in browser
# Navigate to http://localhost:5000/guides/[guide-name]

# 6. Commit and deploy if satisfied
```

---

## ⚠️ Important Notes

- **Backup first:** The update script modifies HTML files directly. Commit your changes to git before running it.
- **Review changes:** Always review the updated HTML in your browser before deploying.
- **Preserve structure:** Don't change the section markers (`TITLE:`, `MAIN CONTENT:`, etc.) in the text files.
- **Test locally:** Make sure your Flask dev server is running to preview changes.

---

## 🆘 Troubleshooting

**Script errors:** Make sure you're in the project root directory and the virtual environment is activated.

**Content not updating:** Check that the text file names match the guide HTML file names exactly.

**Formatting issues:** The script expects the same structure as the extracted files. Don't change section headers.

**Manual fix needed:** For complex changes (like adding new sections or restructuring), use the manual chat method or edit HTML directly.
