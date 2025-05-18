#!/usr/bin/env python
"""
Script to automatically ingest all .epub files in the books directory.
"""

import os
import subprocess
from pathlib import Path

def ingest_all_books():
    # Get the books directory
    books_dir = Path("books")
    
    # Get all .epub files
    epub_files = list(books_dir.glob("*.epub"))
    
    if not epub_files:
        print("No .epub files found in the books directory!")
        return
    
    print(f"Found {len(epub_files)} books to ingest:")
    for book in epub_files:
        print(f"- {book.name}")
    
    # Ingest each book
    for book in epub_files:
        print(f"\nIngesting: {book.name}")
        try:
            result = subprocess.run(
                ["python", "main.py", "ingest", str(book)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ Successfully ingested: {book.name}")
            else:
                print(f"❌ Failed to ingest {book.name}:")
                print(result.stderr)
        except Exception as e:
            print(f"❌ Error ingesting {book.name}: {str(e)}")

if __name__ == "__main__":
    ingest_all_books() 