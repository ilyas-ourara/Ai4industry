#!/usr/bin/env python3
"""
Script de conversion Markdown → PDF pour documentation technique.
Génère un PDF professionnel avec table des matières et formatage.
"""

import markdown2
from weasyprint import HTML, CSS
from pathlib import Path
import re
from datetime import datetime

def markdown_to_html(md_content: str) -> str:
    """Convertir Markdown en HTML avec extras."""
    # Extras pour meilleur rendu
    extras = [
        'fenced-code-blocks',
        'tables',
        'toc',
        'codehilite',
        'break-on-newline'
    ]
    
    html_content = markdown2.markdown(md_content, extras=extras)
    return html_content

def create_styled_html(html_content: str, title: str = "Documentation Technique") -> str:
    """Créer HTML stylisé avec CSS pour PDF."""
    
    css_styles = """
    <style>
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
            padding: 40px;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin: 40px 0 20px 0;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
        }
        
        h2 {
            color: #34495e;
            font-size: 2em;
            margin: 30px 0 15px 0;
            border-left: 5px solid #3498db;
            padding-left: 15px;
            page-break-after: avoid;
        }
        
        h3 {
            color: #34495e;
            font-size: 1.5em;
            margin: 25px 0 12px 0;
            page-break-after: avoid;
        }
        
        h4, h5, h6 {
            color: #555;
            margin: 15px 0 10px 0;
            page-break-after: avoid;
        }
        
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        ul, ol {
            margin-left: 30px;
            margin-bottom: 12px;
        }
        
        li {
            margin-bottom: 8px;
            line-height: 1.8;
        }
        
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
            page-break-inside: avoid;
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
            page-break-inside: avoid;
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
        
        tr:hover {
            background-color: #f0f0f0;
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
        
        .toc {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .toc ul {
            list-style-type: none;
            margin-left: 0;
        }
        
        .toc li {
            margin-bottom: 6px;
        }
        
        .toc a {
            color: #3498db;
        }
        
        .title-page {
            text-align: center;
            padding: 100px 20px;
            margin-bottom: 50px;
            border-bottom: 2px solid #3498db;
            page-break-after: always;
        }
        
        .title-page h1 {
            font-size: 3em;
            color: #2c3e50;
            margin: 20px 0;
            border: none;
        }
        
        .title-page p {
            font-size: 1.1em;
            color: #666;
            margin: 10px 0;
        }
        
        .metadata {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .metadata p {
            margin: 5px 0;
            font-size: 0.95em;
        }
        
        .section {
            page-break-inside: avoid;
            margin-bottom: 30px;
        }
        
        .row {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        
        .col {
            flex: 1;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }
        
        @page {
            size: A4;
            margin: 20mm;
            
            @bottom-center {
                content: "Page " counter(page) " de " counter(pages);
                font-size: 0.9em;
                color: #999;
            }
        }
        
        @media print {
            body {
                padding: 0;
            }
        }
        
        hr {
            border: none;
            border-top: 2px solid #3498db;
            margin: 40px 0;
            page-break-after: avoid;
        }
    </style>
    """
    
    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css_styles}
</head>
<body>
    {html_content}
</body>
</html>"""
    
    return full_html

def markdown_file_to_pdf(md_file: Path, output_file: Path) -> bool:
    """
    Convertir fichier Markdown en PDF.
    
    Args:
        md_file: Chemin fichier Markdown source
        output_file: Chemin fichier PDF destination
        
    Returns:
        True si succès
    """
    try:
        # Lire le fichier Markdown
        md_content = md_file.read_text(encoding='utf-8')
        
        print(f"📖 Lecture du fichier: {md_file.name}")
        print(f"   Taille: {len(md_content) / 1024:.1f} KB")
        
        # Convertir Markdown → HTML
        print("🔄 Conversion Markdown → HTML...")
        html_content = markdown_to_html(md_content)
        
        # Créer HTML stylisé
        print("🎨 Application des styles...")
        full_html = create_styled_html(html_content, md_file.stem)
        
        # Convertir HTML → PDF avec WeasyPrint
        print("📄 Génération du PDF...")
        HTML(string=full_html).write_pdf(
            str(output_file),
            optimize_images=True
        )
        
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"✅ PDF généré avec succès!")
        print(f"   Chemin: {output_file}")
        print(f"   Taille: {file_size_mb:.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Point d'entrée principal."""
    
    # Chemins
    project_dir = Path(__file__).parent
    md_file = project_dir / "DOCUMENTATION_TECHNIQUE.md"
    pdf_file = project_dir / "DOCUMENTATION_TECHNIQUE.pdf"
    
    print("=" * 70)
    print("📚 CONVERSION MARKDOWN → PDF")
    print("=" * 70)
    print()
    
    # Vérifier fichier Markdown existe
    if not md_file.exists():
        print(f"❌ Fichier non trouvé: {md_file}")
        return 1
    
    # Convertir
    success = markdown_file_to_pdf(md_file, pdf_file)
    
    print()
    print("=" * 70)
    if success:
        print("✅ CONVERSION COMPLÉTÉE AVEC SUCCÈS")
        print(f"📄 Fichier PDF: {pdf_file.absolute()}")
    else:
        print("❌ CONVERSION ÉCHOUÉE")
        return 1
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    exit(main())
