#!/usr/bin/env python3
"""
Générateur HTML optimisé pour PDF depuis Markdown.
Crée un HTML avec pagination et formatage professionnel.
"""

import re
from pathlib import Path

def enhance_html_for_pdf(html_content: str, title: str = "Documentation Technique") -> str:
    """Créer un HTML optimisé pour PDF avec formatage professionnel."""
    
    css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.65;
            color: #2c3e50;
            background: #fff;
        }
        
        .page {
            page-break-after: always;
            padding: 20mm;
            min-height: 100%;
        }
        
        .cover-page {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60mm 20mm;
        }
        
        .cover-page h1 {
            font-size: 3.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .cover-page .subtitle {
            font-size: 1.5em;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        
        .cover-page .meta {
            font-size: 1.1em;
            margin-top: 80px;
            opacity: 0.8;
        }
        
        .toc-page {
            padding: 20mm;
        }
        
        .content-page {
            padding: 20mm;
            page-break-inside: avoid;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.2em;
            margin: 30px 0 20px 0;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            page-break-after: avoid;
        }
        
        h2 {
            color: #34495e;
            font-size: 1.8em;
            margin: 25px 0 15px 0;
            border-left: 6px solid #3498db;
            padding-left: 15px;
            page-break-after: avoid;
        }
        
        h3 {
            color: #34495e;
            font-size: 1.4em;
            margin: 20px 0 12px 0;
            page-break-after: avoid;
        }
        
        h4, h5, h6 {
            color: #555;
            margin: 15px 0 10px 0;
            page-break-after: avoid;
        }
        
        p {
            margin: 12px 0;
            text-align: justify;
            hyphens: auto;
        }
        
        ul, ol {
            margin: 15px 0 15px 30px;
        }
        
        li {
            margin: 8px 0;
            line-height: 1.8;
        }
        
        code {
            background-color: #f5f5f5;
            color: #d63384;
            padding: 3px 8px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }
        
        pre {
            background-color: #f8f8f8;
            border-left: 5px solid #3498db;
            border-radius: 4px;
            padding: 15px;
            margin: 15px 0;
            overflow-x: auto;
            page-break-inside: avoid;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        pre code {
            background-color: transparent;
            color: #2c3e50;
            padding: 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
            font-size: 0.95em;
        }
        
        th, td {
            border: 1px solid #bdc3c7;
            padding: 10px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #ecf0f1;
        }
        
        tr:hover {
            background-color: #d5dbdb;
        }
        
        blockquote {
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            background-color: #f0f8ff;
            color: #2c3e50;
            font-style: italic;
            page-break-inside: avoid;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:visited {
            color: #8e44ad;
        }
        
        hr {
            border: none;
            border-top: 2px solid #3498db;
            margin: 40px 0;
            page-break-after: avoid;
        }
        
        .toc {
            background-color: #ecf0f1;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .toc h2 {
            border: none;
            padding: 0;
            margin-top: 0;
        }
        
        .toc ul {
            list-style-type: none;
            margin-left: 0;
        }
        
        .toc li {
            margin: 8px 0;
            line-height: 1.6;
        }
        
        .toc li ul {
            margin-left: 20px;
        }
        
        .toc a {
            color: #2980b9;
        }
        
        .metadata {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
            font-size: 0.95em;
        }
        
        .metadata p {
            margin: 5px 0;
        }
        
        .section-break {
            page-break-before: always;
            margin-bottom: 30px;
        }
        
        .highlight {
            background-color: #ffeaa7;
            padding: 3px 6px;
            border-radius: 2px;
        }
        
        .box {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            background-color: #f9f9f9;
            page-break-inside: avoid;
        }
        
        .box-title {
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }
        
        footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
            font-size: 0.85em;
            color: #7f8c8d;
            page-break-inside: avoid;
        }
        
        @page {
            size: A4;
            margin: 20mm 15mm;
            
            @bottom-center {
                content: "Page " counter(page) " de " counter(pages);
                font-size: 0.85em;
                color: #999;
            }
            
            @top-right {
                content: "Documentation Technique - RAG Application";
                font-size: 0.85em;
                color: #999;
            }
        }
        
        @page :first {
            @bottom-center { content: ""; }
            @top-right { content: ""; }
        }
        
        @media print {
            a { color: #3498db; }
            * { box-shadow: none !important; }
        }
    """
    
    full_html = f"""<!DOCTYPE html>
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
    <!-- Cover Page -->
    <div class="page cover-page">
        <h1>📚 Documentation Technique</h1>
        <p class="subtitle">Application RAG Multi-Agent</p>
        <div class="meta">
            <p><strong>Analyse de Projet</strong></p>
            <p>Documents Départementaux sur les Risques Majeurs</p>
            <p style="margin-top: 30px; font-size: 0.9em;">
                <strong>Date:</strong> 21 Janvier 2026<br>
                <strong>Version:</strong> 1.0
            </p>
        </div>
    </div>
    
    <!-- Table of Contents Page -->
    <div class="page toc-page">
        <h1>Table des matières</h1>
        <div class="toc">
            <ul>
                <li><a href="#vue-densemble">Vue d'ensemble</a></li>
                <li><a href="#architecture-système">Architecture Système</a></li>
                <li><a href="#analyse-détaillée-des-composants">Analyse Détaillée des Composants</a></li>
                <li><a href="#flux-de-traitement">Flux de Traitement</a></li>
                <li><a href="#dépendances-et-intégrations">Dépendances et Intégrations</a></li>
                <li><a href="#résultats-attendus">Résultats Attendus</a></li>
                <li><a href="#configuration-et-déploiement">Configuration et Déploiement</a></li>
                <li><a href="#guide-de-maintenance">Guide de Maintenance</a></li>
            </ul>
        </div>
        <div class="metadata" style="margin-top: 50px;">
            <p><strong>À propos de ce document</strong></p>
            <p>Cette documentation technique est un guide complet pour comprendre, maintenir et évoluer l'application RAG Multi-Agent.</p>
            <p>Elle couvre l'architecture globale, l'analyse détaillée de chaque composant, les flux de traitement, et les guide de maintenance.</p>
        </div>
    </div>
    
    <!-- Content Pages -->
    <div class="page content-page">
        {html_content}
    </div>
    
    <!-- Footer -->
    <footer>
        <p><strong>Documentation Technique - Application RAG Multi-Agent</strong></p>
        <p>Version 1.0 | 21 Janvier 2026 | Analyse Automatisée</p>
    </footer>
</body>
</html>"""
    
    return full_html

def main():
    project_dir = Path(__file__).parent
    html_file = project_dir / "DOCUMENTATION_TECHNIQUE.html"
    md_file = project_dir / "DOCUMENTATION_TECHNIQUE.md"
    pdf_file = project_dir / "DOCUMENTATION_TECHNIQUE.pdf"
    
    if not html_file.exists():
        print(f"❌ Fichier HTML non trouvé: {html_file}")
        return 1
    
    # Lire le HTML existant
    html_content = html_file.read_text(encoding='utf-8')
    
    # Extraire le body content
    body_match = re.search(r'<body>(.*?)</body>', html_content, re.DOTALL)
    if body_match:
        body_content = body_match.group(1).strip()
    else:
        # Si pas de body, utiliser tout
        body_content = html_content
    
    # Créer HTML optimisé pour PDF
    enhanced_html = enhance_html_for_pdf(body_content)
    
    # Sauvegarder
    enhanced_html_file = project_dir / "DOCUMENTATION_TECHNIQUE_OPTIMIZED.html"
    enhanced_html_file.write_text(enhanced_html, encoding='utf-8')
    
    print("✅ HTML optimisé généré")
    print(f"   {enhanced_html_file}")
    
    # Convertir en PDF
    import subprocess
    print("\n🔄 Conversion en PDF avec Chrome...")
    result = subprocess.run([
        '/usr/bin/google-chrome',
        '--headless',
        '--disable-gpu',
        f'--print-to-pdf={str(pdf_file)}',
        str(enhanced_html_file)
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        pdf_size_mb = pdf_file.stat().st_size / (1024 * 1024)
        import subprocess
        pdf_info = subprocess.run(['file', str(pdf_file)], capture_output=True, text=True)
        pages_info = pdf_info.stdout
        
        print("✅ PDF généré avec succès!")
        print(f"   Chemin: {pdf_file}")
        print(f"   Taille: {pdf_size_mb:.2f} MB")
        print(f"   Info: {pages_info.strip()}")
        return 0
    else:
        print(f"❌ Erreur: {result.stderr}")
        return 1

if __name__ == "__main__":
    exit(main())
