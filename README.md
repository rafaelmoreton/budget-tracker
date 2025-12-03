# Budget Tracker

This is an app to assist with tracking the expenditure and income of my family. Each different bank and credit card report comes in a different format, with different information, different categories. Having to manually get all this data, from all my family's credit cards and bank accounts, every month, was making me avoid this task and give up on tracking our finances. Hence, the budget tracker.

It works together with Google Sheets, which acts as both a database and a visualization tool. What the budget tracker actually does (not yet) is taking in the diverse financial reports, parsing and normalizing them, and use the manually attributed categories of transactions as reference for automatically categorizing future transactions.

## Features
- Parse bank and credit card reports from multiple sources
- Normalize data into a consistent structure
- Integrate with Google Sheets for visualization
- Auto‑categorize transactions based on past manual categorization

## Installation
This project needs [Poetry](https://python-poetry.org/docs/) to be installed.
```
git clone https://github.com/rafaelmoreton/budget-tracker.git
cd budget-tracker
poetry install
```
### Configuration
You will need to create a project on [Google Cloud](https://cloud.google.com/), then, in API and Services:
- Activate the Google Sheets API
- Create a service account for the project and download its credentials (store them securely)
- Go to your spreadsheet and share it with the email associated with the service account you created

Place sensitive information inside the .env file at the project root:
```
SPREADSHEET_ID=<your-spreadsheet-id>
GSPREAD_CREDENTIALS=<path-to-your-credentials>
```
*The spreadsheet id is in the spreadsheet's URL, it's the part between d/ and /edit*

## Usage
After installation, the app can be run with `budget-tracker <command>`.

## License
This project is licensed under the GNU General Public License v3.0 – see the [LICENSE](LICENSE) file for details.