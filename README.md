# STS Congenital Heart Surgery Dashboard

This project creates an improved interface for analyzing STS (Society of Thoracic Surgeons) Congenital Heart Surgery data. It scrapes public reporting data from participating hospitals and presents it in a user-friendly, comparative format.

## Features

- Automated data collection from STS public reporting pages
- Comparative analysis of hospital outcomes
- Interactive data visualization
- Custom filtering and sorting capabilities
- Hospital performance metrics comparison

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper:
```bash
python -m scraper.scraper
```

4. Start the web application:
```bash
python -m webapp.app
```

## Project Structure

- `scraper/`: Web scraping and data collection components
- `database/`: Database models and management
- `webapp/`: Flask web application and UI components

## Data Sources

Data is collected from the STS Public Reporting website (https://publicreporting.sts.org/congenital/)
