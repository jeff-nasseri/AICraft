# AICraft - AI-Powered Job Application Management Suite

A collection of AI-powered tools designed to streamline and enhance your job search process. This suite includes tools for email harvesting and job application tracking, all developed with modern AI assistance.

## Projects

### 1. MailHarvest
A powerful email harvesting tool that exports emails from various email providers into JSON format for analysis. Perfect for collecting and organizing your job-related communications.

**Key Features:**
- Multi-provider support (Gmail, Outlook, Yahoo, AOL, Zoho)
- Secure authentication using App Passwords
- Configurable email limits and exclusions
- JSON export format for easy analysis
- Built with SOLID principles

[View MailHarvest Documentation](email/README.md)

### 2. Application Tracker
An intelligent job application tracking system that analyzes your job-related emails and provides insights into your application status.

**Key Features:**
- Automatic status detection (Interview, Rejected, Pending)
- Company and position extraction
- Color-coded status visualization
- Statistical analysis of application progress
- CSV export capability

[View Application Tracker Documentation](job-tracker/README.md)

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aicraft.git
   cd aicraft
   ```

2. Each project has its own virtual environment and dependencies. Please refer to the individual project READMEs for specific setup instructions.

## Project Structure

```
aicraft/
├── email/              # MailHarvest project
│   ├── MailHarvest.py  # Main email harvesting script
│   └── README.md       # Project documentation
│
└── job-tracker/        # Application Tracker project
    ├── application_tracker.py  # Main tracking script
    └── README.md       # Project documentation
```

## Integration

These tools work together seamlessly:
1. Use MailHarvest to export your job-related emails
2. Feed the exported JSON into the Application Tracker
3. Get comprehensive insights into your job search progress

## Development

All projects in this suite were developed with AI assistance, leveraging modern AI tools to create efficient, maintainable, and user-friendly solutions. The code follows best practices and is designed to be easily extensible.

## Contributing

Contributions are welcome! Please feel free to submit pull requests for any of the projects in this suite.

## License

BSD Zero-Clause License

```
Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
```

## Acknowledgments

- All projects in this suite were developed with AI assistance
- Built with modern Python best practices
- Designed for extensibility and maintainability 