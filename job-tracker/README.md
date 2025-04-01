# Application Tracker

A command-line tool to analyze job application emails and display application status in a structured table. This tool works seamlessly with the output from MailHarvest to help you track and manage your job search progress.

## Features

- Analyzes job application emails to determine application status
- Categorizes applications as Interview, Rejected, or Pending
- Combines duplicate applications for the same company and role
- Displays a color-coded table of all job applications
- Provides statistical summary of application status
- Automatically extracts company names and job positions from emails
- Works directly with MailHarvest's JSON output
- Exports results to CSV for further analysis

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/application-tracker.git
   cd application-tracker
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
   pip install pandas tabulate colorama
   ```

## Usage

### Command Line Interface

The Application Tracker provides a flexible command-line interface:

```bash
python application_tracker.py [options]
```

#### Available Options

- `--input`, `-i`: Specify the input JSON file (default: output.json)
- `--export`, `-e`: Export results to a CSV file
- `--no-color`, `-n`: Disable color formatting in output
- `--mock`, `-m`: Use built-in mock data for demonstration

#### Examples

Basic usage with default input file:
```bash
python application_tracker.py
```

Use a specific input file:
```bash
python application_tracker.py --input my_emails.json
```

Export the results to CSV:
```bash
python application_tracker.py --export results.csv
```

Use mock data for testing:
```bash
python application_tracker.py --mock
```

Disable color formatting (useful for redirecting output):
```bash
python application_tracker.py --no-color
```

Combine multiple options:
```bash
python application_tracker.py --input emails.json --export report.csv --no-color
```

## Integration with MailHarvest

This tool is designed to work seamlessly with [MailHarvest](https://github.com/yourusername/mailharvest). The workflow is:

1. Use MailHarvest to export your emails to a JSON file:
   ```bash
   python mailharvest.py export -o output.json
   ```

2. Run Application Tracker to analyze the exported emails:
   ```bash
   python application_tracker.py
   ```

The output JSON from MailHarvest serves as the input for the Application Tracker, creating a complete pipeline for job application tracking.

## Understanding the Output

The Application Tracker generates a table with the following columns:

- **Company**: The company name (extracted from email domain)
- **Position**: The job title/position applied for
- **Status**: Current application status (Interview, Rejected, or Pending)
- **Email IDs**: References to the original emails
- **Count**: Number of emails related to this application

The summary statistics provide:

- Total unique company-position combinations
- Number of companies that have invited you for interviews
- Total interview opportunities (unique positions)
- Number of rejections
- Number of pending applications

## Status Determination

The tool uses keyword analysis to determine the status of each application:

- **Interview**: Emails containing phrases indicating an interview invitation
- **Rejected**: Emails containing phrases indicating rejection
- **Pending**: Emails that don't fall into either of the above categories

## Customization

You can customize the keywords used for status determination by editing the `determine_status` function in the script. This allows you to adapt the tool to different languages or specific phrasing used by recruiters in your industry.

## Limitations

- Status detection relies on keyword matching and may not be 100% accurate
- Company name extraction from email domains may not always yield the correct name
- Position detection is based on common job titles and may require manual correction

## Contributing

Contributions are welcome! Feel free to submit pull requests for improvements such as:

- Enhanced keyword detection for better status determination
- Improved company name and position extraction
- Additional export formats
- UI improvements

## License

MIT