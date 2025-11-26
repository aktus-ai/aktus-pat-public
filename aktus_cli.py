#!/usr/bin/env python3
"""Aktus Data Pipeline CLI"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import requests


class AktusClient:
    def __init__(self, base_url: str = "https://pat.aktus.ai"):
        self.base_url = base_url.rstrip('/')
        self.session_file = Path.home() / ".aktus_session"
        self.session = requests.Session()
        self._load_session()
    
    def _load_session(self) -> None:
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    self.session.cookies.update(json.load(f))
            except:
                pass
    
    def _save_session(self) -> None:
        try:
            with open(self.session_file, 'w') as f:
                json.dump(dict(self.session.cookies), f)
        except:
            pass
    
    def _clear_session(self) -> None:
        if self.session_file.exists():
            self.session_file.unlink()
    
    def _handle_response(self, response: requests.Response) -> dict:
        try:
            data = response.json()
        except:
            print("Error: Invalid JSON response", file=sys.stderr)
            sys.exit(1)
        
        if response.status_code >= 400:
            error = data.get('detail', data.get('message', 'Unknown error'))
            print(f"Error [{response.status_code}]: {error}", file=sys.stderr)
            sys.exit(1)
        
        return data
    
    def login(self, api_key: str) -> dict:
        response = self.session.post(f"{self.base_url}/api/v1/auth/login", json={"api_key": api_key})
        data = self._handle_response(response)
        self._save_session()
        return data
    
    def logout(self) -> dict:
        response = self.session.post(f"{self.base_url}/api/v1/auth/logout")
        data = self._handle_response(response)
        self._clear_session()
        return data
    
    def upload_document(self, file_path: str, provider_name: Optional[str] = None) -> dict:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        if not file_path_obj.suffix.lower() == '.pdf':
            print("Error: File must be PDF", file=sys.stderr)
            sys.exit(1)
        
        with open(file_path_obj, 'rb') as f:
            files = {'file': (file_path_obj.name, f, 'application/pdf')}
            data = {'provider_name': provider_name} if provider_name else {}
            response = self.session.post(f"{self.base_url}/api/v1/documents", files=files, data=data)
        
        return self._handle_response(response)
    
    def list_documents(self, skip: int = 0, limit: int = 100) -> dict:
        response = self.session.get(f"{self.base_url}/api/v1/documents", params={'skip': skip, 'limit': limit})
        return self._handle_response(response)
    
    def find_portfolios(self, filename: str) -> dict:
        response = self.session.get(f"{self.base_url}/api/v1/documents/by-filename/{filename}/portfolios")
        return self._handle_response(response)


def format_output(data: dict, compact: bool = False) -> None:
    print(json.dumps(data, indent=None if compact else 2))


def cmd_login(client: AktusClient, args: argparse.Namespace) -> None:
    result = client.login(args.api_key)
    print("Authentication successful")
    if not args.quiet:
        format_output(result, args.compact)


def cmd_logout(client: AktusClient, args: argparse.Namespace) -> None:
    result = client.logout()
    print("Session terminated")
    if not args.quiet:
        format_output(result, args.compact)


def cmd_upload(client: AktusClient, args: argparse.Namespace) -> None:
    result = client.upload_document(args.file, args.provider)
    print(f"Document uploaded: {args.file}")
    if not args.quiet:
        format_output(result, args.compact)


def cmd_list(client: AktusClient, args: argparse.Namespace) -> None:
    result = client.list_documents(args.skip, args.limit)
    
    if args.quiet:
        for doc in result.get('documents', []):
            print(doc.get('filename', 'Unknown'))
    else:
        print(f"Retrieved {result.get('count', 0)} document(s)")
        format_output(result, args.compact)


def cmd_portfolios(client: AktusClient, args: argparse.Namespace) -> None:
    result = client.find_portfolios(args.filename)
    
    if args.quiet:
        for portfolio in result.get('portfolios', []):
            print(portfolio.get('name', 'Unknown'))
    else:
        print(f"Found {result.get('count', 0)} portfolio(s): {args.filename}")
        format_output(result, args.compact)


def main() -> None:
    parser = argparse.ArgumentParser(prog='aktus', description='Aktus Data Pipeline CLI')
    parser.add_argument('--base-url', default='https://pat.aktus.ai', help='API server URL')
    parser.add_argument('--compact', action='store_true', help='Compact JSON output')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    login_parser = subparsers.add_parser('login', help='Authenticate')
    login_parser.add_argument('api_key', help='API key')
    
    subparsers.add_parser('logout', help='Terminate session')
    
    upload_parser = subparsers.add_parser('upload', help='Upload PDF')
    upload_parser.add_argument('file', help='PDF file path')
    upload_parser.add_argument('--provider', help='Provider name')
    
    list_parser = subparsers.add_parser('list', help='List documents')
    list_parser.add_argument('--skip', type=int, default=0, help='Skip documents')
    list_parser.add_argument('--limit', type=int, default=100, help='Limit results')
    
    portfolios_parser = subparsers.add_parser('portfolios', help='Find portfolios')
    portfolios_parser.add_argument('filename', help='Document filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    client = AktusClient(base_url=args.base_url)
    
    commands = {
        'login': cmd_login,
        'logout': cmd_logout,
        'upload': cmd_upload,
        'list': cmd_list,
        'portfolios': cmd_portfolios
    }
    
    if args.command in commands:
        commands[args.command](client, args)
    else:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
