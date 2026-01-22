"""
PDF Extraction Agent (Agent 1)
Responsible for extracting content from PDF files and converting to raw Markdown.

IMPORTANT: This agent uses ONLY Docling for extraction.
No other extraction method (PyMuPDF, pdfplumber, OCR, etc.) is allowed.

Role: PDF → Raw Markdown (no structuring, no chunking, no semantic analysis)
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from loguru import logger

from core.base_agent import BaseAgent

# Docling imports
try:
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
except ImportError:
    raise ImportError(
        "Docling is required for PDF extraction. "
        "Install with: pip install docling"
    )


@dataclass
class ExtractionResult:
    """Result of PDF extraction."""
    source_file: str
    markdown_content: str
    extraction_time: float
    success: bool
    error: Optional[str] = None


class PDFExtractionAgent(BaseAgent):
    """
    Agent 1: PDF Extraction (Docling Only)
    
    Responsibilities:
    - Extract content from PDF files using Docling
    - Convert to raw Markdown format
    - Preserve original content and order
    
    Constraints:
    - Uses ONLY Docling for extraction
    - No structuring, chunking, or semantic analysis
    - Output is raw Markdown preserving document content
    
    Role: PDF → Raw Markdown
    """

    # Placeholders for page breaks and images
    PAGE_BREAK_PLACEHOLDER = "\n\n--- Page Break ---\n\n"
    IMAGE_PLACEHOLDER = "<!__image__>"

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the PDF Extraction Agent.
        
        Args:
            output_dir: Directory to save extracted Markdown files
        """
        super().__init__(
            name="PDFExtractionAgent",
            description="Extracts PDF content to raw Markdown using Docling"
        )
        
        # Configure output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.settings.get_absolute_path(
                self.settings.output_dir / "markdown"
            )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"PDFExtractionAgent initialized (output: {self.output_dir})")

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input PDF path(s).
        
        Args:
            input_data: Single path or list of paths to PDF files
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If input is invalid
        """
        if isinstance(input_data, (str, Path)):
            paths = [Path(input_data)]
        elif isinstance(input_data, list):
            paths = [Path(p) for p in input_data]
        else:
            raise ValueError(f"Invalid input type: {type(input_data)}")
        
        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"PDF file not found: {path}")
            if not path.suffix.lower() == ".pdf":
                raise ValueError(f"Not a PDF file: {path}")
        
        return True

    def process(
        self, 
        input_data: Union[str, Path, List[Union[str, Path]]]
    ) -> List[ExtractionResult]:
        """
        Process PDF file(s) and extract to raw Markdown.
        
        Args:
            input_data: Path to PDF file or list of paths
            
        Returns:
            List of ExtractionResult objects
        """
        self.logger.info("Starting PDF extraction process (Docling)")
        
        # Normalize input to list
        if isinstance(input_data, (str, Path)):
            pdf_paths = [Path(input_data)]
        else:
            pdf_paths = [Path(p) for p in input_data]
        
        # Validate
        self.validate_input(pdf_paths)
        
        # Process each PDF
        results = []
        for pdf_path in pdf_paths:
            result = self._extract_single_pdf(pdf_path)
            results.append(result)
            
            if result.success:
                self.logger.info(f"✓ Extracted: {pdf_path.name} ({result.extraction_time:.2f}s)")
            else:
                self.logger.error(f"✗ Failed: {pdf_path.name} - {result.error}")
        
        # Update agent state
        self.update_state("extraction_results", results)
        self.update_state("markdown_files", [
            str(self.output_dir / f"{r.source_file.replace('.pdf', '.md')}")
            for r in results if r.success
        ])
        
        return results

    def _extract_single_pdf(self, pdf_path: Path) -> ExtractionResult:
        """
        Extract content from a single PDF using Docling.
        
        This method follows STRICTLY the provided extract_text() function.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult with markdown content
        """
        self.logger.info(f"Extracting PDF: {pdf_path}")
        print(f"----Démarrage du traitement du PDF: {pdf_path.name}----")
        
        start_time = time.time()
        
        try:
            # Validate file exists
            if not pdf_path.exists():
                raise FileNotFoundError(
                    f"Le fichier PDF spécifié n'existe pas : {pdf_path}"
                )
            
            # Configure Docling pipeline options (EXACTLY as provided)
            pipeline_options = PdfPipelineOptions(
                generate_page_images=False,
                do_ocr=False,
                do_picture_classification=False,
                image_scale=0.3
            )
            
            # Create converter with PDF format options
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pipeline_options
                    )
                }
            )
            
            # Convert PDF to Docling document
            result = converter.convert(pdf_path)
            doc = result.document
            
            # Export to Markdown with placeholders
            markdown_text = doc.export_to_markdown(
                page_break_placeholder=self.PAGE_BREAK_PLACEHOLDER,
                image_placeholder=self.IMAGE_PLACEHOLDER
            )
            
            elapsed = time.time() - start_time
            print(f"----Extraction terminée en {elapsed:.2f}s----")
            
            # Save Markdown file
            md_filename = pdf_path.stem + ".md"
            md_path = self.output_dir / md_filename
            self._save_markdown(markdown_text, md_path)
            
            return ExtractionResult(
                source_file=pdf_path.name,
                markdown_content=markdown_text,
                extraction_time=elapsed,
                success=True
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Extraction failed for {pdf_path}: {e}")
            
            return ExtractionResult(
                source_file=pdf_path.name,
                markdown_content="",
                extraction_time=elapsed,
                success=False,
                error=str(e)
            )

    def _save_markdown(self, markdown_content: str, output_path: Path) -> Path:
        """
        Save Markdown content to file.
        
        Args:
            markdown_content: Raw Markdown content
            output_path: Path to save the file
            
        Returns:
            Path to saved file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        self.logger.info(f"Saved Markdown: {output_path}")
        return output_path

    def extract_single(self, pdf_path: Union[str, Path]) -> ExtractionResult:
        """
        Convenience method to extract a single PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ExtractionResult
        """
        results = self.process(pdf_path)
        return results[0]

    def get_markdown_content(self, pdf_path: Union[str, Path]) -> str:
        """
        Extract and return only the Markdown content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Raw Markdown string
        """
        result = self.extract_single(pdf_path)
        
        if not result.success:
            raise RuntimeError(f"Extraction failed: {result.error}")
        
        return result.markdown_content

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about extractions performed."""
        results = self.get_state("extraction_results", [])
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        return {
            "total_processed": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "total_time": sum(r.extraction_time for r in results),
            "average_time": sum(r.extraction_time for r in results) / len(results) if results else 0,
            "output_directory": str(self.output_dir),
        }
