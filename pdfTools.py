#!/usr/bin/env python3
import argparse
import os
from typing import List, Tuple
import fitz  # PyMuPDF

def parse_ranges(ranges_str: str) -> List[Tuple[str, List[int]]]:
    """Parse ranges string into list of tuples (name, page_range)"""
    ranges = []
    for part in ranges_str.split(';'):
        parts = part.strip().split(',')
        name = parts[-1]
        pages = [int(p.strip()) for p in parts[:-1]]
        ranges.append((name, pages))
    return ranges

def pdf_to_png(pdf_path: str, dpi: int, output_folder: str):
    """Convert PDF to sequence of PNG files"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0  # Convert DPI to zoom factor
    matrix = fitz.Matrix(zoom, zoom)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=matrix)
        output_path = os.path.join(output_folder, f"page-{page_num}.png")
        pix.save(output_path)
    
    doc.close()

def split_pdf(pdf_path: str, ranges_str: str):
    """Split PDF according to specified page ranges"""
    doc = fitz.open(pdf_path)
    ranges = parse_ranges(ranges_str)
    
    for name, pages in ranges:
        output_path = f"{name}.pdf"
        new_doc = fitz.open()
        
        # Sort pages to handle ranges like [5,1] correctly
        sorted_pages = sorted(pages)
        
        # Add all pages in the range
        for page_num in range(sorted_pages[0]-1, sorted_pages[-1]):  # -1 for 0-based indexing
            if 0 <= page_num < len(doc):
                page = doc[page_num]
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(page.rect, doc, page.number)
        
        new_doc.save(output_path)
        new_doc.close()
    
    doc.close()

def main():
    parser = argparse.ArgumentParser(description="PDF manipulation tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parser for pdf-to-png conversion
    png_parser = subparsers.add_parser(
        "convert",
        help="Convert PDF to sequence of PNG files"
    )
    png_parser.add_argument("input", help="Input PDF file path")
    png_parser.add_argument("--dpi", type=int, default=300, help="Resolution in DPI")
    png_parser.add_argument("--output", required=True, help="Destination folder")

    # Parser for PDF splitting
    split_parser = subparsers.add_parser(
        "split",
        help="Split PDF into multiple files based on page ranges"
    )
    split_parser.add_argument("input", help="Input PDF file path")
    split_parser.add_argument(
        "--ranges",
        required=True,
        help="Page ranges in format: '1,5,name1; 7,9,name2'"
    )

    args = parser.parse_args()

    if args.command == "convert":
        pdf_to_png(args.input, args.dpi, args.output)
    elif args.command == "split":
        split_pdf(args.input, args.ranges)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()