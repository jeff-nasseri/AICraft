#!/usr/bin/env python3
import os
import json
import argparse
import imaplib
import email
import email.header
import base64
from email.parser import BytesParser
from email.policy import default
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import re

# Try different import approaches for dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    try:
        from python_dotenv import load_dotenv
    except ImportError:
        # Fallback implementation if dotenv isn't available
        def load_dotenv():
            """Simple fallback implementation to load .env file"""
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            return True


class EmailConnector(ABC):
    """Abstract base class for email provider connections"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the email provider"""
        pass
        
    @abstractmethod
    def fetch_emails(self, limit: Optional[int] = None, plain_text_only: bool = False, 
                    exclude_senders: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch emails from the provider"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the email provider"""
        pass


class ImapEmailConnector(EmailConnector):
    """Base IMAP email connector implementation"""
    
    def __init__(self, username: str, password: str, imap_server: str, imap_port: int = 993):
        self.username = username
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.imap = None
        
    def connect(self) -> bool:
        """Connect to email provider using IMAP"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.username, self.password)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def fetch_emails(self, limit: Optional[int] = None, plain_text_only: bool = False, 
                    exclude_senders: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch emails from email provider inbox
        
        Args:
            limit: Maximum number of emails to fetch
            plain_text_only: Whether to extract only plain text content
            exclude_senders: List of sender email addresses to exclude
            
        Returns:
            List of email dictionaries
        """
        emails = []
        exclude_senders = exclude_senders or []
        
        # Select the mailbox
        status, messages = self.imap.select('INBOX')
        if status != 'OK':
            print("Error selecting inbox")
            return emails
            
        # Search for all emails
        status, message_ids = self.imap.search(None, 'ALL')
        if status != 'OK':
            print("No messages found")
            return emails
            
        # Convert ids to list
        id_list = message_ids[0].split()
        
        # Apply limit if specified
        if limit and limit > 0:
            id_list = id_list[-limit:]
            
        # Process each message
        for email_id in id_list:
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            if status != 'OK':
                print(f"Error fetching message {email_id}")
                continue
                
            raw_email = msg_data[0][1]
            
            # Parse the raw email
            try:
                # For Python 3.x
                msg = BytesParser(policy=default).parsebytes(raw_email)
            except AttributeError:
                # Alternative approach if parsebytes isn't available
                import io
                msg = BytesParser(policy=default).parse(io.BytesIO(raw_email))
            
            # Extract data
            subject = self._decode_header(msg['Subject'])
            from_address = self._decode_header(msg['From'])
            date = self._parse_date(msg['Date'])
            
            # Skip emails from excluded senders
            should_exclude = False
            for exclude_sender in exclude_senders:
                if exclude_sender.lower() in from_address.lower():
                    should_exclude = True
                    break
                    
            if should_exclude:
                continue
            
            # Get content
            content = self._get_email_content(msg, plain_text_only)
            
            # If content is still empty, try looking deeper in the structure
            if not content:
                try:
                    # Some emails might have content in a deeply nested structure
                    # This is a fallback method to try to extract any text
                    all_parts = []
                    for part in msg.walk():
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                if isinstance(payload, bytes):
                                    decoded = payload.decode('utf-8', errors='replace')
                                    all_parts.append(decoded)
                        except:
                            pass
                    
                    if all_parts:
                        # Join all found parts and try to extract text
                        combined = ' '.join(all_parts)
                        if '<' in combined and '>' in combined:
                            # Extract text from HTML
                            content = self._html_to_text(combined)
                        else:
                            content = combined
                except Exception as e:
                    print(f"Error in fallback content extraction: {e}")
            
            # Create email dict
            email_data = {
                'id': email_id.decode(),
                'subject': subject,
                'from': from_address,
                'date': date,
                'content': content
            }
            
            emails.append(email_data)
            
        return emails
        
    def disconnect(self) -> None:
        """Disconnect from email provider"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ''
            
        decoded_header = email.header.decode_header(header)
        header_parts = []
        
        for content, encoding in decoded_header:
            if isinstance(content, bytes):
                if encoding:
                    header_parts.append(content.decode(encoding or 'utf-8', errors='replace'))
                else:
                    header_parts.append(content.decode('utf-8', errors='replace'))
            else:
                header_parts.append(str(content))
                
        return ' '.join(header_parts)
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and format email date"""
        if not date_str:
            return ''
            
        try:
            dt = email.utils.parsedate_to_datetime(date_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return date_str
    
    def _get_email_content(self, msg, plain_text_only=False) -> str:
        """
        Extract email content (plain text or HTML)
        
        Args:
            msg: The email message object
            plain_text_only: If True, extract only plain text content and ignore HTML
            
        Returns:
            str: The extracted content
        """
        plain_content = ""
        html_content = ""
        
        # Check if the email is multipart
        if msg.is_multipart():
            # Iterate through parts
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                    
                # Get plain text content
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            plain_part = payload.decode('utf-8', errors='replace')
                            plain_content += plain_part
                    except Exception as e:
                        print(f"Error decoding plain text: {e}")
                
                # Get HTML content
                elif content_type == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_part = payload.decode('utf-8', errors='replace')
                            html_content += html_part
                    except Exception as e:
                        print(f"Error decoding HTML: {e}")
        else:
            # Handle non-multipart email
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    if content_type == "text/plain":
                        plain_content = payload.decode('utf-8', errors='replace')
                    elif content_type == "text/html":
                        html_content = payload.decode('utf-8', errors='replace')
            except Exception as e:
                print(f"Error decoding email content: {e}")
        
        # Choose content based on priority and availability
        content = ""
        if plain_content:
            content = plain_content
        elif html_content:
            # Extract text from HTML for all HTML content
            content = self._html_to_text(html_content)
            
        # Clean up the content (remove excessive whitespace)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
        
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML content to plain text
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Plain text extracted from HTML
        """
        # Remove scripts and style elements first
        html_content = re.sub(r'<script.*?>.*?</script>', ' ', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style.*?>.*?</style>', ' ', html_content, flags=re.DOTALL)
        
        # Replace common block elements with newlines for better readability
        html_content = re.sub(r'<(div|p|h\d|br|li|tr)[^>]*?>', '\n', html_content)
        
        # Replace common HTML entities
        entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'",
            '&cent;': '¢',
            '&pound;': '£',
            '&yen;': '¥',
            '&euro;': '€',
            '&copy;': '©',
            '&reg;': '®',
        }
        
        for entity, replacement in entities.items():
            html_content = html_content.replace(entity, replacement)
        
        # Handle numeric entities
        html_content = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), html_content)
        
        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]*?>', '', html_content)
        
        # Clean up whitespace
        html_content = re.sub(r'\n+', '\n', html_content)
        html_content = re.sub(r'\s+', ' ', html_content)
        
        return html_content.strip()


class GmailConnector(ImapEmailConnector):
    """Gmail specific implementation of EmailConnector"""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, 'imap.gmail.com', 993)


class OutlookConnector(ImapEmailConnector):
    """Outlook/Hotmail/Live specific implementation of EmailConnector"""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, 'outlook.office365.com', 993)


class YahooMailConnector(ImapEmailConnector):
    """Yahoo Mail specific implementation of EmailConnector"""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, 'imap.mail.yahoo.com', 993)


class AOLMailConnector(ImapEmailConnector):
    """AOL Mail specific implementation of EmailConnector"""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, 'imap.aol.com', 993)


class ZohoMailConnector(ImapEmailConnector):
    """Zoho Mail specific implementation of EmailConnector"""
    
    def __init__(self, username: str, password: str):
        super().__init__(username, password, 'imap.zoho.com', 993)


class EmailExporter(ABC):
    """Abstract base class for email exporters"""
    
    @abstractmethod
    def export(self, emails: List[Dict[str, Any]], output_path: str) -> bool:
        """Export emails to a file"""
        pass


class JsonEmailExporter(EmailExporter):
    """JSON implementation of EmailExporter"""
    
    def export(self, emails: List[Dict[str, Any]], output_path: str) -> bool:
        """Export emails to a JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(emails, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False


class EmailExportService:
    """Service to coordinate email export operations"""
    
    def __init__(self, connector: EmailConnector, exporter: EmailExporter):
        self.connector = connector
        self.exporter = exporter
        
    def export_emails(self, output_path: str, limit: Optional[int] = None, 
                      plain_text_only: bool = False, exclude_senders: Optional[List[str]] = None) -> bool:
        """
        Export emails using the connector and exporter
        
        Args:
            output_path: Path to save the exported emails
            limit: Maximum number of emails to export
            plain_text_only: Whether to extract only plain text content
            exclude_senders: List of sender email addresses to exclude
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Connect to email provider
            if not self.connector.connect():
                return False
                
            # Fetch emails
            print("Fetching emails...")
            emails = self.connector.fetch_emails(limit, plain_text_only, exclude_senders)
            print(f"Found {len(emails)} emails")
            
            # Export emails
            print(f"Exporting to {output_path}...")
            result = self.exporter.export(emails, output_path)
            
            # Disconnect
            self.connector.disconnect()
            
            if result:
                print("Export completed successfully")
            
            return result
            
        except Exception as e:
            print(f"Export failed: {e}")
            self.connector.disconnect()
            return False


class EmailConnectorFactory:
    """Factory class to create email connectors based on provider type"""
    
    @staticmethod
    def create_connector(provider: str, username: str, password: str) -> EmailConnector:
        """Create an email connector for the specified provider"""
        provider = provider.lower()
        
        if provider == 'gmail':
            return GmailConnector(username, password)
        elif provider == 'outlook':
            return OutlookConnector(username, password)
        elif provider == 'yahoo':
            return YahooMailConnector(username, password)
        elif provider == 'aol':
            return AOLMailConnector(username, password)
        elif provider == 'zoho':
            return ZohoMailConnector(username, password)
        else:
            raise ValueError(f"Unsupported email provider: {provider}")


def create_email_export_service(provider: str) -> EmailExportService:
    """Factory function to create an email export service"""
    load_dotenv()
    
    # Get provider-specific environment variables
    provider = provider.lower()
    username_var = f"{provider.upper()}_USERNAME"
    password_var = f"{provider.upper()}_APP_PASSWORD"
    
    username = os.getenv(username_var)
    password = os.getenv(password_var)
    
    if not username or not password:
        raise ValueError(f"Email credentials not found in .env file. Please set {username_var} and {password_var}.")
        
    connector = EmailConnectorFactory.create_connector(provider, username, password)
    exporter = JsonEmailExporter()
    
    return EmailExportService(connector, exporter)


def load_exclusion_list(file_path: str) -> List[str]:
    """
    Load a list of email addresses to exclude from a text file
    
    Args:
        file_path: Path to the text file with one email address per line
        
    Returns:
        List of email addresses to exclude
    """
    exclude_list = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Remove whitespace and skip empty lines or comments
                line = line.strip()
                if line and not line.startswith('#'):
                    exclude_list.append(line)
        return exclude_list
    except Exception as e:
        print(f"Error loading exclusion list from {file_path}: {e}")
        return []


def main():
    """Main entry point for the CLI application"""
    parser = argparse.ArgumentParser(description="MailHarvest: Export emails from various providers")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export emails')
    export_parser.add_argument('-o', '--output', required=True, help='Output file path')
    export_parser.add_argument('-l', '--limit', type=int, help='Maximum number of emails to export')
    export_parser.add_argument('-p', '--provider', default='gmail', 
                               choices=['gmail', 'outlook', 'yahoo', 'aol', 'zoho'],
                               help='Email provider (default: gmail)')
    export_parser.add_argument('--plain-text', action='store_true', 
                              help='Extract only plain text content, strip HTML')
    export_parser.add_argument('--exclude-sender', action='append', dest='exclude_senders',
                              help='Exclude emails from specific senders (can be used multiple times)')
    export_parser.add_argument('--exclude-file', 
                              help='Path to a text file containing email addresses to exclude (one per line)')
    
    args = parser.parse_args()
    
    if args.command == 'export':
        try:
            # Initialize exclude senders list
            exclude_senders = args.exclude_senders or []
            
            # Add senders from exclusion file if specified
            if args.exclude_file:
                file_exclusions = load_exclusion_list(args.exclude_file)
                exclude_senders.extend(file_exclusions)
                print(f"Loaded {len(file_exclusions)} exclusions from {args.exclude_file}")
            
            service = create_email_export_service(args.provider)
            service.export_emails(args.output, args.limit, args.plain_text, exclude_senders)
        except ValueError as e:
            print(f"Error: {e}")
    else:
        parser.print_help()


# Main entry point
if __name__ == "__main__":
    main()