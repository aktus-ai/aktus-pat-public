#!/usr/bin/env python3
"""Batch upload for Aktus Data Pipeline"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


class BatchUploader:
    def __init__(self, api_key, base_url="https://pat.aktus.ai", max_workers=5):
        self.base_url = base_url.rstrip('/')
        self.max_workers = max_workers
        self.session = requests.Session()
        
        response = self.session.post(f"{self.base_url}/api/v1/auth/login", json={"api_key": api_key})
        
        if response.status_code != 200:
            print("Error: Authentication failed")
            sys.exit(1)
        
        print("✓ Authenticated\n")
    
    def upload_file(self, pdf_path, provider_name=None):
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': (pdf_path.name, f, 'application/pdf')}
                data = {'provider_name': provider_name} if provider_name else {}
                
                response = self.session.post(f"{self.base_url}/api/v1/documents", files=files, data=data)
                
                if response.status_code == 200:
                    return True, None
                else:
                    error = response.json().get('detail', 'Unknown error')
                    return False, error
        except Exception as e:
            return False, str(e)
    
    def upload_folder(self, folder_path, provider_name=None):
        folder = Path(folder_path)
        
        if not folder.is_dir():
            print(f"Error: Invalid folder: {folder_path}")
            sys.exit(1)
        
        # Find PDFs with both lowercase and uppercase extensions
        pdf_files = sorted(list(folder.glob("*.pdf")) + list(folder.glob("*.PDF")))
        
        if not pdf_files:
            print(f"No PDFs found in: {folder_path}")
            return
        
        print(f"Found {len(pdf_files)} PDF(s)\n")
        print(f"Uploading with {self.max_workers} workers...\n")
        
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {
                executor.submit(self.upload_file, pdf, provider_name): pdf
                for pdf in pdf_files
            }
            
            for future in as_completed(future_to_pdf):
                pdf = future_to_pdf[future]
                success, error = future.result()
                
                if success:
                    print(f"✓ {pdf.name}")
                    successful += 1
                else:
                    print(f"✗ {pdf.name}: {error}")
                    failed += 1
        
        print(f"\nComplete: {successful} succeeded, {failed} failed")
        self.session.post(f"{self.base_url}/api/v1/auth/logout")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch upload PDFs')
    parser.add_argument('folder', help='Folder with PDFs')
    parser.add_argument('api_key', help='API key')
    parser.add_argument('--provider', help='Provider name')
    parser.add_argument('--workers', type=int, default=5, help='Parallel workers')
    parser.add_argument('--base-url', default='https://pat.aktus.ai', help='API URL')
    
    args = parser.parse_args()
    
    uploader = BatchUploader(args.api_key, args.base_url, args.workers)
    uploader.upload_folder(args.folder, args.provider)
