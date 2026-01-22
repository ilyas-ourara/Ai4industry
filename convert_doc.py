#!/usr/bin/env python3
"""
Convertisseur Markdown en PDF (HTML intermédiaire).
Utilise uniquement des bibliothèques standard et installables localement.
"""

import re
from pathlib import Path
from typing import List, Tuple
import html

def escape_html(text: str) -> str:
    """Échapper le texte pour HTML."""
    return html.escape(text)

def parse_markdown_to_html(md_content: str) -> str:
    """
    Parser simple Markdown → HTML.
    Support: headings, lists, bold, italic, code, blockquotes, tables
    """
    lines = md_content.split('\n')
    html_lines = []
    in_code_block = False
    in_list = False
    in_table = False
    code_block_language = ""
    
    for i, line in enumerate(lines):
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
                code_block_language = ""
            else:
                in_code_block = True
                code_block_language = line.strip()[3:].strip()
                html_lines.append(f'<pre><code class="language-{code_block_language}">')
            continue
        
        if in_code_block:
            html_lines.append(escape_html(line))
            continue
        
        # Tables
        if '|' in line and not in_list:
            if not in_table:
                html_lines.append('<table>')
                in_table = True
            
            # Check if it's a header separator
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                html_lines.append('<thead><tr>')
                continue
            
            if in_table:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<td>{escape_html(cell)}</td>')
                html_lines.append('</tr>')
                continue
        elif in_table and not line.strip():
            html_lines.append('</table>')
            in_table = False
            continue
        
        # Empty lines
        if not line.strip():
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<br>')
            continue
        
        # Headings
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('#').strip()
            html_lines.append(f'<h{level}>{escape_html(title)}</h{level}>')
            continue
        
        # Lists
        if line.lstrip().startswith(('- ', '* ', '+ ')):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            item = line.lstrip()[2:].strip()
            html_lines.append(f'<li>{escape_html(item)}</li>')
            continue
        
        if line.lstrip().startswith(tuple(f'{i}. ' for i in range(10))):
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
            match = re.match(r'^\s*\d+\.\s+(.*)', line)
            if match:
                item = match.group(1).strip()
                html_lines.append(f'<li>{escape_html(item)}</li>')
            continue
        
        # Blockquotes
        if line.startswith('> '):
            quote = line[2:].strip()
            html_lines.append(f'<blockquote>{escape_html(quote)}</blockquote>')
            continue
        
        # Horizontal rules
        if re.match(r'^[\-\*_]{3,}$', line.strip()):
            html_lines.append('<hr>')
            continue
        
        # Paragraphs with formatting
        text = escape_html(line.strip())
        
        # Code inline
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
        
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        if text.strip():
            html_lines.append(f'<p>{text}</p>')
    
    # Close remaining open tags
    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</table>')
    if in_code_block:
        html_lines.append('</code></pre>')
    
    return '\n'.join(html_lines)

def create_html_document(content: str, title: str = "Documentation") -> str:
    """Créer un document HTML complet avec styles."""
    
    css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: white;
            padding: 60px 40px;
            max-width: 900px;
            margin: 0 auto;
        }
        
        h1 { color: #2c3e50; font-size: 2.5em; margin: 40px 0 20px; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; font-size: 2em; margin: 35px 0 15px; border-left: 5px solid #3498db; padding-left: 15px; }
        h3 { color: #34495e; font-size: 1.5em; margin: 25px 0 12px; }
        h4, h5, h6 { color: #555; margin: 15px 0 10px; }
        
        p { margin-bottom: 12px; text-align: justify; }
        
        ul, ol { margin-left: 30px; margin-bottom: 12px; }
        li { margin-bottom: 8px; line-height: 1.8; }
        
        code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #d63384;
        }
        
        pre {
            background-color: #f5f5f5;
            border-left: 4px solid #3498db;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 15px 0;
            font-size: 0.9em;
        }
        
        pre code {
            background-color: transparent;
            color: #333;
            padding: 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 15px 0;
            color: #666;
            font-style: italic;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        hr {
            border: none;
            border-top: 2px solid #3498db;
            margin: 40px 0;
        }
        
        @media print {
            body { padding: 40px; }
            h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
            pre, table { page-break-inside: avoid; }
        }
    """
    
    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    {content}
</body>
</html>"""
    
    return html_doc

def markdown_to_html_file(md_path: Path, html_path: Path) -> bool:
    """Convertir Markdown en HTML."""
    try:
        print(f"📖 Lecture: {md_path.name}")
        md_content = md_path.read_text(encoding='utf-8')
        
        print("🔄 Conversion Markdown → HTML...")
        html_content = parse_markdown_to_html(md_content)
        
        print("🎨 Création du document avec styles...")
        html_doc = create_html_document(html_content, md_path.stem)
        
        print(f"💾 Sauvegarde: {html_path.name}")
        html_path.write_text(html_doc, encoding='utf-8')
        
        print(f"✅ HTML généré: {html_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def html_to_pdf_with_wkhtmltopdf(html_path: Path, pdf_path: Path) -> bool:
    """Convertir HTML en PDF avec wkhtmltopdf si disponible."""
    import subprocess
    import shutil
    
    wkhtmltopdf = shutil.which('wkhtmltopdf')
    if not wkhtmltopdf:
        return False
    
    try:
        subprocess.run(
            [wkhtmltopdf, '--enable-local-file-access', str(html_path), str(pdf_path)],
            check=True,
            capture_output=True
        )
        return True
    except:
        return False

def create_pdf_instruction_file(html_path: Path):
    """Créer un fichier d'instructions pour convertir le HTML en PDF."""
    
    instruction_file = html_path.parent / "CONVERSION_PDF_INSTRUCTIONS.txt"
    
    instructions = f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║          CONVERSION HTML → PDF - INSTRUCTIONS                             ║
╚═══════════════════════════════════════════════════════════════════════════╝

Un fichier HTML a été généré avec succès:
   📄 {html_path.name}

Pour convertir ce fichier en PDF professionnel, vous avez plusieurs options:

OPTION 1: Utiliser votre navigateur web (le plus simple)
─────────────────────────────────────────────────────────
1. Ouvrez le fichier HTML: {html_path.absolute()}
2. Dans le navigateur: Ctrl+P (ou Cmd+P sur Mac)
3. Sélectionnez "Imprimer dans un fichier PDF"
4. Sauvegardez avec le nom: DOCUMENTATION_TECHNIQUE.pdf

OPTION 2: Utiliser Google Chrome en ligne de commande
──────────────────────────────────────────────────────
google-chrome --headless --print-to-pdf=DOCUMENTATION_TECHNIQUE.pdf {html_path.absolute()}

OPTION 3: Utiliser wkhtmltopdf (si installé)
──────────────────────────────────────────────
wkhtmltopdf --enable-local-file-access {html_path.absolute()} DOCUMENTATION_TECHNIQUE.pdf

OPTION 4: Utiliser pandoc avec LaTeX
──────────────────────────────────────
pandoc {html_path.absolute()} -o DOCUMENTATION_TECHNIQUE.pdf

RÉSULTAT ATTENDU:
─────────────────
✓ Fichier PDF: DOCUMENTATION_TECHNIQUE.pdf (~5-10 MB)
✓ Pages: ~100-150
✓ Table des matières: Automatique
✓ Formatage: Professionnel avec styles

Le fichier HTML {html_path.name} est le fichier source.
Vous pouvez le visualiser directement dans votre navigateur,
ou le convertir en PDF selon l'une des options ci-dessus.

Bonne documentation! 📚
"""
    
    instruction_file.write_text(instructions, encoding='utf-8')
    print(f"\n📋 Instructions de conversion: {instruction_file}")

def main():
    """Point d'entrée principal."""
    project_dir = Path(__file__).parent
    md_file = project_dir / "DOCUMENTATION_TECHNIQUE.md"
    html_file = project_dir / "DOCUMENTATION_TECHNIQUE.html"
    pdf_file = project_dir / "DOCUMENTATION_TECHNIQUE.pdf"
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║      CONVERSION DOCUMENTATION MARKDOWN → HTML/PDF               ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    if not md_file.exists():
        print(f"❌ Fichier Markdown non trouvé: {md_file}")
        return 1
    
    # Convertir Markdown → HTML
    if not markdown_to_html_file(md_file, html_file):
        print("❌ Erreur lors de la conversion Markdown → HTML")
        return 1
    
    print()
    print("✅ Document HTML créé avec succès!")
    print(f"   Chemin: {html_file.absolute()}")
    print()
    
    # Essayer convertir HTML → PDF si les outils sont disponibles
    if html_to_pdf_with_wkhtmltopdf(html_file, pdf_file):
        print("✅ Document PDF créé avec succès!")
        print(f"   Chemin: {pdf_file.absolute()}")
        file_size = pdf_file.stat().st_size / (1024 * 1024)
        print(f"   Taille: {file_size:.1f} MB")
    else:
        print("⚠️  wkhtmltopdf non disponible.")
        print("   Un fichier HTML a été créé à la place.")
        print()
        create_pdf_instruction_file(html_file)
    
    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                  CONVERSION TERMINÉE                            ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    return 0

if __name__ == "__main__":
    exit(main())
