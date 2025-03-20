#!/usr/bin/env python3
"""
Application Tracker - Analyzes job application emails and displays application status
Prevents counting duplicate interviews from the same company
"""

import json
import re
import pandas as pd
import argparse
import sys
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def load_data(filename=None, mock_data=None):
    """Load job application data from a JSON file or use mock data"""
    if mock_data:
        return mock_data
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} is not a valid JSON file")
        return []

def extract_date(email_data):
    """Extract the date from an email"""
    date_str = email_data.get('date', '')
    try:
        # Parse date from email
        date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        return date_obj
    except ValueError:
        # If date parsing fails, return current date
        return datetime.now()

def is_job_application_email(email_data):
    """Determine if an email is related to a job application"""
    subject = email_data.get('subject', '').lower()
    content = email_data.get('content', '').lower()
    
    application_keywords = [
        'application', 'job', 'position', 'career', 'vacancy', 'applied', 
        'opportunity', 'employment', 'recruiting', 'talent', 'candidate',
        'resume', 'cv', 'cover letter', 'hiring', 'developer', 'engineer'
    ]
    
    # Check if the email is likely to be application-related
    for keyword in application_keywords:
        if keyword in subject or keyword in content:
            return True
            
    return False

def extract_company_name(email_data):
    """Try to extract the company name from the email data"""
    sender = email_data.get('from', '')
    
    # Try to extract from sender domain
    if '@' in sender:
        domain = sender.split('@')[1].split('.')[0]
        if domain not in ['gmail', 'hotmail', 'outlook', 'yahoo', 'aol', 'mail']:
            return domain.title()
    
    return "Unknown Company"

def extract_position(email_data):
    """Try to extract the job position from the email data"""
    subject = email_data.get('subject', '').lower()
    content = email_data.get('content', '').lower()
    
    # Common job titles in tech
    job_titles = [
        'software developer', 'software engineer', 'web developer', 
        'full stack developer', 'backend developer', 'frontend developer',
        'data engineer', 'data scientist', 'machine learning engineer',
        'devops engineer', 'cloud engineer', 'mobile developer',
        'ios developer', 'android developer', 'security engineer',
        'game developer', 'qa engineer', 'product manager'
    ]
    
    # Check for job titles in subject and content
    text = subject + ' ' + content
    for title in job_titles:
        if title in text:
            return title.title()
    
    return "Software Developer"  # Default if no match found

def determine_status(email_data):
    """Determine the status of a job application based on email content"""
    subject = email_data.get('subject', '').lower()
    content = email_data.get('content', '').lower()
    
    combined_text = subject + ' ' + content
    
    # Keywords indicating rejection
    rejection_keywords = [
        'regret', 'unfortunately', 'not moving forward', 'not selected',
        'unable to proceed', 'not a match', 'not the right fit',
        'other candidates', 'no longer', 'will not', 'cannot'
    ]
    
    # Keywords indicating interview
    interview_keywords = [
        'progress your application', "video interview", "happy to invite",
        "excited to move forward", "I'm excited"
    ]
    
    # Check for rejection keywords
    for keyword in rejection_keywords:
        if keyword in combined_text:
            return "Rejected"
    
    # Check for interview keywords
    for keyword in interview_keywords:
        if keyword in combined_text:
            return "Interview"
    
    # If neither rejection nor interview is detected
    return "Pending"

def analyze_emails(data):
    """Analyze the emails and extract job application information"""
    applications = []
    
    for email in data:
        # Skip emails not related to job applications
        if not is_job_application_email(email):
            continue
        
        company = extract_company_name(email)
        position = extract_position(email)
        status = determine_status(email)
        date = extract_date(email)
        email_id = email.get('id', 'Unknown')
        
        applications.append({
            'email_id': email_id,
            'company': company,
            'position': position,
            'status': status,
            'date': date
        })
    
    return applications

def create_table(applications, no_color=False, export_file=None):
    """Create and display a tabulated table with the applications"""
    if not applications:
        print("No job applications found in the data.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(applications)
    
    # Group by company and position to combine duplicates
    # For each group, we'll pick the most positive status (Interview > Pending > Rejected)
    # and combine the email IDs
    
    # Create a function to get status priority (higher is better)
    def status_priority(status):
        if status == 'Interview':
            return 3
        elif status == 'Pending':
            return 2
        else:  # Rejected
            return 1
    
    # Create a dictionary to hold the aggregated data
    aggregated_data = []
    
    # Group by company and position
    grouped = df.groupby(['company', 'position'])
    
    for (company, position), group in grouped:
        # Get all email IDs
        email_ids = group['email_id'].tolist()
        combined_email_id = ', '.join(map(str, email_ids))
        
        # Get the best status
        statuses = group['status'].tolist()
        best_status = max(statuses, key=status_priority)
        
        # Add to aggregated data
        aggregated_data.append({
            'company': company,
            'position': position,
            'status': best_status,
            'email_id': combined_email_id,
            'email_count': len(email_ids)
        })
    
    # Create new DataFrame from aggregated data
    df = pd.DataFrame(aggregated_data)
    
    # Sort by company name alphabetically
    df = df.sort_values(by='company', ascending=True)
    
    # Reset index for display
    df = df.reset_index(drop=True)
    
    # Define colors
    if no_color:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ""
    else:
        GREEN = Fore.GREEN
        RED = Fore.RED
        YELLOW = Fore.YELLOW
        BLUE = Fore.BLUE
        CYAN = Fore.CYAN
        RESET = Style.RESET_ALL
        BOLD = Style.BRIGHT
    
    # Create a copy of the dataframe for display
    display_df = df.copy()
    
    # Color-code the status column
    display_df['status'] = df['status'].apply(
        lambda x: f"{GREEN}{x}{RESET}" if x == 'Interview' else 
                (f"{RED}{x}{RESET}" if x == 'Rejected' else 
                 f"{YELLOW}{x}{RESET}")
    )
    
    # Color-code the company column
    display_df['company'] = df['company'].apply(
        lambda x: f"{BLUE}{x}{RESET}"
    )
    
    # Add count indicator for combined rows
    display_df['email_count'] = df['email_count'].apply(
        lambda x: f"({x} emails)" if x > 1 else ""
    )
    
    # Display the table
    print(f"\n{BOLD}===== JOB APPLICATION TRACKER ====={RESET}\n")
    
    # Convert DataFrame to tabulate format
    # Reorder columns for better readability
    display_cols = ['company', 'position', 'status', 'email_id', 'email_count']
    table = tabulate(
        display_df[display_cols], 
        headers=['Company', 'Position', 'Status', 'Email IDs', 'Count'],
        tablefmt='grid',
        showindex=True
    )
    
    print(table)
    
    # Calculate summary statistics using the aggregated data
    total_unique_company_positions = len(df)
    rejected = len(df[df['status'] == 'Rejected'])
    interviews = len(df[df['status'] == 'Interview'])
    pending = len(df[df['status'] == 'Pending'])
    
    # Get unique companies with interview status
    interview_companies = set(df[df['status'] == 'Interview']['company'])
    unique_interview_companies = len(interview_companies)
    
    # Print formatted summary statistics
    print(f"\n{BOLD}Summary:{RESET}")
    print(f"Total Unique Company-Position Combinations: {total_unique_company_positions}")
    print(f"{GREEN}Companies with Interviews:{RESET} {unique_interview_companies} ({unique_interview_companies/total_unique_company_positions*100:.1f}%)")
    print(f"Total Interview Opportunities: {interviews} ({interviews/total_unique_company_positions*100:.1f}%)")
    print(f"{RED}Rejections:{RESET} {rejected} ({rejected/total_unique_company_positions*100:.1f}%)")
    print(f"{YELLOW}Pending:{RESET} {pending} ({pending/total_unique_company_positions*100:.1f}%)")
    
    # List unique companies that invited for interviews
    if unique_interview_companies > 0:
        print(f"\n{BOLD}Companies that invited you for interviews:{RESET}")
        for company in sorted(interview_companies):
            print(f"- {BLUE}{company}{RESET}")

    # Export to CSV if requested
    if export_file:
        try:
            # Export the non-colored data
            export_df = df.copy()
            export_df.to_csv(export_file, index=False)
            print(f"\nData exported successfully to {export_file}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Application Tracker - Analyze job application emails and display status"
    )
    parser.add_argument(
        "--input", "-i", 
        default="output.json",
        help="Path to the input JSON file (default: output.json)"
    )
    parser.add_argument(
        "--export", "-e",
        help="Export results to CSV file"
    )
    parser.add_argument(
        "--no-color", "-n",
        action="store_true",
        help="Disable color formatting in output"
    )
    parser.add_argument(
        "--mock", "-m",
        action="store_true",
        help="Use mock data for demonstration"
    )
    return parser.parse_args()

def main():
    """Main function to run the application tracker"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Mock data for testing
    mock_data = [
      {
        "id": "email1",
        "from": "recruiter@techcorp.com",
        "subject": "Interview Invitation for Software Developer Position",
        "date": "Mon, 10 Mar 2025 09:30:45 +0000",
        "content": "We would like to invite you for an interview for the Software Developer position at TechCorp."
      },
      {
        "id": "email2",
        "from": "careers@datasoft.com",
        "subject": "Your application for Data Engineer",
        "date": "Fri, 7 Mar 2025 14:22:18 +0000",
        "content": "Thank you for applying. Unfortunately, we regret to inform you that we are not moving forward with your application."
      },
      {
        "id": "email3",
        "from": "hr@webdev.io",
        "subject": "Application Received - Full Stack Developer",
        "date": "Wed, 5 Mar 2025 11:15:30 +0000",
        "content": "We have received your application for the Full Stack Developer position. We will review your qualifications and get back to you."
      },
      {
        "id": "email4",
        "from": "talent@innovate.com",
        "subject": "Next steps for your Software Developer application",
        "date": "Tue, 4 Mar 2025 16:45:22 +0000",
        "content": "We'd like to schedule a time to discuss your application and experience further. Please let us know your availability."
      },
      {
        "id": "email5",
        "from": "no-reply@cloudtech.com",
        "subject": "Cloud Engineer Application Status",
        "date": "Mon, 3 Mar 2025 10:20:15 +0000",
        "content": "After careful consideration, we have determined that your qualifications are not the right fit for this role."
      },
      {
        "id": "email6",
        "from": "careers@mobileapp.com",
        "subject": "Interview Invitation - Mobile Developer",
        "date": "Fri, 28 Feb 2025 15:10:05 +0000",
        "content": "We were impressed with your application and would like to invite you for an interview to discuss the Mobile Developer position."
      },
      {
        "id": "email7",
        "from": "recruitment@ailab.org",
        "subject": "Application for Machine Learning Engineer",
        "date": "Wed, 26 Feb 2025 09:05:45 +0000",
        "content": "Your application is being reviewed by our team. We appreciate your patience during this process."
      },
      {
        "id": "email8",
        "from": "hr@securitysys.net",
        "subject": "Interview Request - Security Developer",
        "date": "Mon, 24 Feb 2025 14:30:12 +0000",
        "content": "We would like to meet with you to discuss your application for the Security Developer position. Please confirm your availability."
      },
      {
        "id": "email9",
        "from": "jobs@gaming.dev",
        "subject": "Your Game Developer Application",
        "date": "Fri, 21 Feb 2025 11:45:33 +0000",
        "content": "Unfortunately, we are unable to proceed with your application at this time. We will keep your resume on file for future opportunities."
      },
      {
        "id": "email10",
        "from": "noreply@newsletter.com",
        "subject": "Weekly Tech Newsletter",
        "date": "Thu, 20 Feb 2025 08:00:00 +0000",
        "content": "Here's your weekly roundup of tech news and job opportunities."
      },
      # Added duplicate interview from same company to test de-duplication
      {
        "id": "email11",
        "from": "recruiter@techcorp.com",
        "subject": "Follow-up Interview Details",
        "date": "Tue, 11 Mar 2025 14:22:10 +0000",
        "content": "We're excited to move forward with your application. Here are the details for your upcoming interview."
      }
    ]
    
    print("Loading job application data...")
    
    # Determine data source based on arguments
    if args.mock:
        print("Using mock data for demonstration...")
        data = mock_data
    else:
        data = load_data(filename=args.input)
        if not data:
            print("No data found. Use --mock for demonstration data.")
            sys.exit(1)
    
    # Analyze emails and extract job application information
    applications = analyze_emails(data)
    
    # Create and display the table
    create_table(applications, no_color=args.no_color, export_file=args.export)

if __name__ == "__main__":
    main()