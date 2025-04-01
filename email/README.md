# MailHarvest

A command-line tool to export emails from various email providers into JSON format for analysis.

## Features

- Exports email subjects, senders, dates, and content
- Supports multiple email providers:
  - Gmail (fully implemented)
  - Outlook (coming soon)
  - Yahoo Mail (coming soon)
  - AOL Mail (coming soon)
  - Zoho Mail (coming soon)
- Saves data in JSON format for easy analysis
- Uses App Passwords for secure authentication
- Configurable email limit
- Built with SOLID principles

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/mailharvest.git
   cd mailharvest
   ```

2. Set up a virtual environment:
   ```bash
   # For Python 3 on Linux/macOS
   python3 -m venv venv
   source venv/bin/activate

   # For Python 3 on Windows (Command Prompt)
   python -m venv venv
   venv\Scripts\activate.bat

   # For Python 3 on Windows (PowerShell)
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```
   # Using pip directly
   pip install -r requirements.txt
   
   # Or if using Python 3.13 specifically
   python3.13 -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your email credentials (see below for instructions on getting App Passwords)

## How to Get App Passwords

### Gmail
To use this tool with Gmail, you'll need to create an App Password:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Select "Security" in the left navigation panel
3. Under "Signing in to Google," select "2-Step Verification" (you must have this enabled)
4. Scroll to the bottom and select "App passwords"
5. Click "Select app" dropdown and choose "Mail"
6. Click "Select device" dropdown and choose "Other" (enter "MailHarvest")
7. Click "Generate"
8. Google will display your 16-character app password - copy this
9. Paste this password into your `.env` file as the value for `GMAIL_APP_PASSWORD`

### Other Providers
Similar instructions apply for other email providers, though the exact steps may vary. Check your provider's documentation for details on generating app passwords.

**Important**: Never share your App Password. It provides access to your email account.

## Usage

### Activating the Virtual Environment

Always activate the virtual environment before running the tool:

```bash
# For Linux/macOS
source venv/bin/activate

# For Windows (Command Prompt)
venv\Scripts\activate.bat

# For Windows (PowerShell)
venv\Scripts\Activate.ps1
```

You'll know the virtual environment is active when you see `(venv)` at the beginning of your command prompt.

### Exporting Emails

Export your emails to a JSON file (defaults to Gmail):

```
python mailharvest.py export -o output.json
```

Specify a different email provider:

```
python mailharvest.py export -o output.json -p outlook
```

Supported provider options: `gmail`, `outlook`, `yahoo`, `aol`, `zoho`

Limit the number of emails exported:

```
python mailharvest.py export -o output.json -l 100
```

Extract only plain text content (strip HTML):

```
python mailharvest.py export -o output.json --plain-text
```

Exclude emails from specific senders (individual exclusions):

```
python mailharvest.py export -o output.json --exclude-sender newsletter@example.com --exclude-sender no-reply@company.com
```

Exclude emails using an exclusion list file:

```
python mailharvest.py export -o output.json --exclude-file exclude_list.txt
```

## Exclusion List Format

When using the `--exclude-file` option, create a text file with one email address pattern per line:

```
# Comments start with #
newsletter@company.com
marketing@example.com
@spam-domain.com  # Exclude entire domains
no-reply          # Exclude anything containing "no-reply"
```

- Blank lines are ignored
- Lines starting with # are treated as comments
- Each line is used for partial matching (case-insensitive)
- You can exclude entire domains with @domain.com

A sample exclusion list file is included in the repository as `exclude_list.txt`.

### Output Format

The tool exports emails in the following JSON format:

```json
[
  {
    "id": "12345",
    "subject": "Hello World",
    "from": "John Doe <john.doe@example.com>",
    "date": "2023-01-01 12:34:56",
    "content": "This is the email content..."
  },
  // More emails...
]
```

## Architecture

This tool is built using SOLID principles:

- **Single Responsibility Principle**: Each class has a single responsibility
  - `EmailConnector`: Handles connecting to email providers
  - `EmailExporter`: Handles exporting emails to different formats
  - `EmailExportService`: Coordinates the export process

- **Open/Closed Principle**: Classes are open for extension but closed for modification
  - New email providers can be added by implementing the `EmailConnector` interface
  - New export formats can be added by implementing the `EmailExporter` interface

- **Liskov Substitution Principle**: Child classes can be substituted for their parent classes
  - `ImapEmailConnector` provides a base implementation for all IMAP-based providers
  - Specific provider implementations inherit from this base class

- **Interface Segregation Principle**: Clients are not forced to depend on interfaces they don't use
  - Interfaces are small and focused on specific functionality

- **Dependency Inversion Principle**: High-level modules depend on abstractions, not concrete implementations
  - `EmailExportService` depends on the `EmailConnector` and `EmailExporter` interfaces
  - `EmailConnectorFactory` creates concrete implementations based on provider type

## Current Status

Currently, only Gmail is fully implemented and tested. Support for other providers (Outlook, Yahoo, AOL, Zoho) is in development and will be available soon. The architecture is designed to make adding these providers straightforward.

## Limitations

- Only exports from the inbox folder
- Only exports to JSON format (though the architecture allows for easy extension)
- Does not download attachments

## Why Use a Virtual Environment?

Virtual environments in Python provide several benefits:

1. **Isolation**: Each project has its own dependencies, regardless of what other projects need
2. **Dependency Management**: Avoid conflicts between project requirements
3. **Clean Environment**: Start with a clean environment for each project
4. **Easy Deployment**: Makes it easier to reproduce the environment on another machine

The `venv` module is included with Python 3.3 and later, so no additional installation is needed.

## Troubleshooting

### Virtual Environment Issues

- **Permission Denied**: If you get permission errors when creating a virtual environment, try using `sudo` on Linux/macOS or running as administrator on Windows.
- **Command Not Found**: If `python3` or `python` command is not found, ensure Python is installed and in your PATH.
- **Activation Script Not Found**: Make sure you're in the project root directory when activating the virtual environment.

### Email Connection Issues

- **Connection Errors**: Ensure your credentials are correct and that the email provider allows IMAP access.
- **Authentication Errors**: Make sure 2FA is set up and you're using an App Password, not your regular account password.
- **Too Many Connections**: Some providers limit the number of concurrent IMAP connections. Wait a few minutes and try again.

## Contributing

Contributions are welcome! If you'd like to add support for another email provider, please submit a pull request.

## License

MIT