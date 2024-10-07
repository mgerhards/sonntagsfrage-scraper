# Sonntagsfrage Scraper

This project scrapes data from the **Sonntagsfrage** section of [Wahlrecht.de](https://www.wahlrecht.de/umfragen/), which contains polling data from major research institutes dating back to 1998. The data is then transformed into both a `.pickle` and `.csv` file for easy access and further analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- Scrapes polling data from multiple research institutes (Forsa, Allensbach, Emnid, GMS, INSA, etc.).
- Extracts data from 1998 to the present.
- Saves the data into two formats:
  - **Pickle** file for fast, Python-native access.
  - **CSV** file for external usage or analysis.
- Uses `pip-tools` for dependency management.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/sonntagsfrage-scraper.git
   cd sonntagsfrage-scraper
   ```

2. Install dependencies using `pip-tools`:

   ```bash
   pip install pip-tools
   pip-sync requirements.txt
   ```

   To update dependencies, modify the `requirements.in` file and run:

   ```bash
   pip-compile
   pip-sync
   ```

3. Ensure you have Python 3.12+ installed.

## Usage

Run the scraper to extract and transform the data:

   ```bash
   python scraper.py
   ```

   This will generate two files in the `data/` directory:
   
   - `sonntagsfrage_data.csv`
   - `sonntagsfrage_data.pkl`


## Data Sources

The polling data is scraped from [Wahlrecht.de](https://www.wahlrecht.de/umfragen/), which aggregates polling results from major German research institutes.

## Project Structure

```bash
├── data/
│   ├── sonntagsfrage_data.csv   # Scraped data in CSV format
│   ├── sonntagsfrage_data.pkl   # Scraped data in Pickle format
├── scraper.py                   # Main script for scraping and transforming data
├── requirements.in              # Dependencies for pip-tools
├── requirements.txt             # Compiled dependency file
├── README.md                    # Project documentation
└── urls.py                      # Lists of urls leading to the data
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
