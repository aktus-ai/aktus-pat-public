#!/usr/bin/env python3
"""Aktus Data Pipeline - Interactive UI"""

import os
import sys
from pathlib import Path
import subprocess


class AktusUI:
    def __init__(self):
        self.base_url = "https://pat.aktus.ai"
        self.session_file = Path.home() / ".aktus_session"
    
    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_curl(self, endpoint, method="GET", data=None, files=None, auth_required=True):
        print("\n📋 Swagger API Equivalent:")
        print("-" * 60)
        
        curl = f"curl -X {method} '{self.base_url}{endpoint}'"
        
        if method in ["POST", "PUT"] and not files:
            curl += " \\\n  -H 'Content-Type: application/json'"
        
        if auth_required:
            curl += " \\\n  -H 'X-API-Key: YOUR_API_KEY'"
        
        if data:
            curl += f" \\\n  -d '{data}'"
        
        if files:
            curl += f" \\\n  -F 'file=@{files}'"
        
        print(curl)
        print("-" * 60)
        print()
    
    def header(self):
        print("=" * 60)
        print(" " * 15 + "AKTUS DATA PIPELINE")
        print("=" * 60)
        print()
    
    def menu(self):
        self.clear()
        self.header()
        
        status = "✓ Session Active" if self.session_file.exists() else "⚠ Not Logged In"
        print(f"{status}\n")
        
        print("MAIN MENU")
        print("-" * 60)
        print("1. Login")
        print("2. Upload Document")
        print("3. List Documents")
        print("4. Find Portfolios")
        print("5. Logout")
        print()
        print("6. Upload Folder (Batch)")
        print("7. Settings")
        print("0. Exit")
        print("-" * 60)
        print()
    
    def cli(self, args):
        cmd = ["python", "aktus_cli.py"] + args
        if self.base_url != "https://pat.aktus.ai":
            cmd.extend(["--base-url", self.base_url])
        subprocess.run(cmd)
    
    def batch(self, args):
        cmd = ["python", "batch_upload.py"] + args
        if self.base_url != "https://pat.aktus.ai":
            cmd.extend(["--base-url", self.base_url])
        subprocess.run(cmd)
    
    def login(self):
        self.clear()
        self.header()
        print("LOGIN\n")
        
        self.show_curl('/api/v1/auth/login', 'POST', '{"api_key": "YOUR_API_KEY"}', auth_required=False)
        
        api_key = input("API Key: ").strip()
        if api_key:
            print("\nAuthenticating...")
            self.cli(["login", api_key])
        input("\nPress Enter...")
    
    def upload(self):
        self.clear()
        self.header()
        print("UPLOAD DOCUMENT\n")
        
        self.show_curl('/api/v1/documents', 'POST', files='document.pdf')
        
        if not self.session_file.exists():
            print("⚠ Not logged in. Please provide API key.\n")
            api_key = input("API Key: ").strip()
            if api_key:
                print("\nAuthenticating...")
                self.cli(["login", api_key])
                print()
        
        file_path = input("File path: ").strip()
        if file_path:
            provider = input("Provider (optional): ").strip()
            print("\nUploading...")
            args = ["upload", file_path]
            if provider:
                args.extend(["--provider", provider])
            self.cli(args)
        input("\nPress Enter...")
    
    def batch_upload(self):
        self.clear()
        self.header()
        print("BATCH UPLOAD\n")
        
        print("📋 Swagger API Equivalent:")
        print("-" * 60)
        print("For each PDF file:")
        print(f"curl -X POST '{self.base_url}/api/v1/documents' \\")
        print("  -H 'X-API-Key: YOUR_API_KEY' \\")
        print("  -F 'file=@filename.pdf'")
        print("-" * 60)
        print()
        
        folder = input("Folder: ").strip()
        api_key = input("API Key: ").strip()
        if folder and api_key:
            provider = input("Provider (optional): ").strip()
            workers = input("Workers (default 5): ").strip()
            print("\nUploading...")
            args = [folder, api_key]
            if provider:
                args.extend(["--provider", provider])
            if workers:
                args.extend(["--workers", workers])
            self.batch(args)
        input("\nPress Enter...")
    
    def list_docs(self):
        self.clear()
        self.header()
        print("LIST DOCUMENTS\n")
        
        self.show_curl('/api/v1/documents?limit=100', 'GET')
        
        if not self.session_file.exists():
            print("⚠ Not logged in. Please provide API key.\n")
            api_key = input("API Key: ").strip()
            if api_key:
                print("\nAuthenticating...")
                self.cli(["login", api_key])
                print()
        
        limit = input("Limit (default 100): ").strip()
        print("\nRetrieving...")
        args = ["list"]
        if limit:
            args.extend(["--limit", limit])
        self.cli(args)
        input("\nPress Enter...")
    
    def portfolios(self):
        self.clear()
        self.header()
        print("FIND PORTFOLIOS\n")
        
        self.show_curl('/api/v1/documents/by-filename/{filename}/portfolios', 'GET')
        
        if not self.session_file.exists():
            print("⚠ Not logged in. Please provide API key.\n")
            api_key = input("API Key: ").strip()
            if api_key:
                print("\nAuthenticating...")
                self.cli(["login", api_key])
                print()
        
        filename = input("Filename: ").strip()
        if filename:
            print("\nRetrieving...")
            self.cli(["portfolios", filename])
        input("\nPress Enter...")
    
    def logout(self):
        self.clear()
        self.header()
        print("LOGOUT\n")
        
        self.show_curl('/api/v1/auth/logout', 'POST')
        
        self.cli(["logout"])
        input("\nPress Enter...")
    
    def settings(self):
        self.clear()
        self.header()
        print("SETTINGS\n")
        print(f"API URL: {self.base_url}\n")
        print("1. Change URL")
        print("2. Reset to default")
        print("0. Back")
        print()
        choice = input("Option: ").strip()
        
        if choice == "1":
            url = input("\nNew URL: ").strip()
            if url:
                self.base_url = url
                print(f"✓ Updated to: {self.base_url}")
        elif choice == "2":
            self.base_url = "https://pat.aktus.ai"
            print(f"✓ Reset to: {self.base_url}")
        
        if choice in ["1", "2"]:
            input("\nPress Enter...")
    
    def run(self):
        while True:
            self.menu()
            choice = input("Option: ").strip()
            
            if choice == "1": self.login()
            elif choice == "2": self.upload()
            elif choice == "3": self.list_docs()
            elif choice == "4": self.portfolios()
            elif choice == "5": self.logout()
            elif choice == "6": self.batch_upload()
            elif choice == "7": self.settings()
            elif choice == "0":
                self.clear()
                print("\nGoodbye!\n")
                sys.exit(0)


if __name__ == '__main__':
    try:
        AktusUI().run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!\n")
        sys.exit(0)
