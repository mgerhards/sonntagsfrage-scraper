import os
import pickle
from urls import urls, urls_current
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def fetch_html(url: str) -> str:
    """
    Fetches the HTML content from the given URL.
    Args:
        url (str): The URL to fetch the HTML content from.
    Returns:
        str: The HTML content of the response if the request is successful.
    Raises:
        ValueError: If the URL is null or empty.
        None: If there is an error during the request, None is returned and an error message is printed.
    """
    if not url:
        raise ValueError("The URL must not be null or empty")

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to extract table data
def extract_table_data(html_content: str) -> pd.DataFrame:
        """
        Extracts data from an HTML table and returns it as a Pandas DataFrame.
        Args:
            html_content (str): The HTML content containing the table.
        Returns:
            pd.DataFrame: A DataFrame containing the extracted table data.
        The function performs the following steps:
        1. Parses the HTML content using BeautifulSoup.
        2. Finds the table with the class 'wilko'.
        3. Extracts the table headers from the <thead> section.
        4. Handles empty headers by assigning them a default name.
        5. Extracts the table rows from the <tbody> section.
        6. Cleans and processes the cell data, removing unwanted characters.
        7. Creates a Pandas DataFrame using the extracted data and headers.
        Note:
            - The function assumes that the table has a <thead> and <tbody> section.
            - The function handles empty headers by naming them 'Unnamed_i' where 'i' is the column index.
            - The function removes certain characters (e.g., '–', '\xa0', '%', ',') from the cell data.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='wilko')

        table_header = table.find("thead")
        headers = [th.text.strip() for th in table_header.find_all(['th', 'td'])]
        # handle empty headers
        headers = [f"Unnamed_{i}" if not col else col for i, col in enumerate(headers)]
        table_body = table.find("tbody")
        rows = table_body.find_all('tr')
        data = []

        for row in rows[1:]:
            cells = row.find_all('td')
            row_data = []

            for cell in cells:
                text = cell.text.strip().replace('–', ' ').replace('\xa0', ' ').replace('%','').replace(',','.')
                row_data.append(text)

            if row_data:
                data.append(row_data)
        
        max_data_cols = max(len(row) for row in data)
        
        # Create a Pandas DataFrame for easy manipulation
        df = pd.DataFrame(data, columns=headers[:max_data_cols])

        return df

def get_organization_from_url(s_url: str) -> str:
    base_url = "https://www.wahlrecht.de/umfragen/"
    rest = s_url.replace(base_url, "")
    parts = rest.split('/')
    org_name = parts[0]
    # Remove '.htm' or '.html' extensions if present
    org_name = org_name.replace('.htm', '').replace('.html', '')
    return org_name

def load_urls_completed(file_path: str) -> list:
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            try:
                urls_completed = pickle.load(file)
                if not isinstance(urls_completed, list):
                    raise ValueError("The data in the pickle file is not a list")
                return urls_completed
            except (pickle.UnpicklingError, EOFError) as e:
                print(f"Error loading pickle file: {e}")
                return []
    else:
        return []
    
def load_cached_data(file_path: str) -> pd.DataFrame:
    if not file_path or not os.path.exists(file_path):
        print("File path is invalid or file does not exist.")
        return None

    try:
        df = pd.read_pickle(file_path)
        return df
    except Exception as e:
        print(f"Error loading data frame from file: {e}")
        return None
    
def pickle_urls_completed(file_path: str, urls: list):
    with open(file_path, 'wb') as file:
        pickle.dump(urls, file)

    
def build_archive():
    """
    Builds an archive of data by parsing URLs, extracting table data, and saving the results.
    This function performs the following steps:
    1. Loads the list of completed URLs from a cache file.
    2. Loads cached data from a file.
    3. Iterates over a set of URLs that have not been completed yet.
    4. For each URL:
        a. Prints the URL being parsed.
        b. Extracts the organization name from the URL.
        c. Fetches the HTML content of the URL.
        d. Extracts table data from the HTML content into a DataFrame.
        e. Adds the organization name to the DataFrame.
        f. Renames the first column to 'datum'.
        g. Resets the DataFrame index and sets a new multi-index with 'datum' and 'org'.
        h. Replaces empty strings with NaN values.
        i. Concatenates the new DataFrame with existing data if available.
        j. Saves the updated data to a cache file.
        k. Appends the URL to the list of completed URLs and updates the cache file.
    5. Prints the final DataFrame.
    6. Optionally, saves the final DataFrame to a CSV file.
    7. Cleans the data and saves the cleaned DataFrame to a file.
    Note:
        - The function assumes the existence of helper functions: `load_urls_completed`, `load_cached_data`, 
          `get_organization_from_url`, `fetch_html`, `extract_table_data`, `pickle_urls_completed`, and `clean_data`.
        - The function uses the `pandas` library for DataFrame operations and `numpy` for handling NaN values.
    """
    urls_completed_cache_filename = 'cache/urls_completed.pkl'
    urls_completed = load_urls_completed(urls_completed_cache_filename)

    data_cache_filename = 'cache/Sonntagsfrage_wip.pkl'
    data = load_cached_data(data_cache_filename)
    
    for url in list(set(urls) - set(urls_completed)):
        print("Parsing URL:", url)
        org = get_organization_from_url(url)

        html = fetch_html(url)
        # Call the function and print the DataFrame
        df = extract_table_data(html)
        df["org"] = org
        #df.drop(df.columns[1], axis=1,inplace=True)
        df.rename(columns={df.columns[0]: 'datum'}, inplace=True)
        df = df.reset_index()
        df = df.set_index(['datum', 'org'])
        # %%
        df = df.replace(r'^\s*$', np.nan, regex=True)
        if data is not None:
            data= pd.concat([data, df])
        else:
            data = df

        
        data.to_pickle(data_cache_filename)    
        urls_completed.append(url)
        pickle_urls_completed(urls_completed_cache_filename, urls_completed)

    print(data)

    # Optionally, save to CSV
    data.to_pickle('cache/Sonntagsfrage.pkl')
    data_cleaned = clean_data(data)
    data_cleaned.to_pickle("cache/Sonntagsfrage_cleaned.pkl")
    


def clean_data(df):
    df = df.reset_index()
    df['s_datum'] = df['datum']
    df.loc[:, 'datum'] = pd.to_datetime(df['s_datum'], format='%d.%m.%Y', errors='coerce') 
    df_cleaned = df.dropna(subset=['datum'])
    df_cleaned['datum'] = pd.to_datetime(df_cleaned['datum'])
    df_cleaned.loc[:, 'month'] = df_cleaned['datum'].dt.month
    df_cleaned.loc[:, 'year'] = df_cleaned['datum'].dt.year
    df_cleaned.loc[:, 'week_of_year'] = df_cleaned['datum'].dt.isocalendar().week
    relevant_cols = ['datum', 'year', 'month', 'week_of_year', 'org', 'CDU/CSU', 'SPD', 'GRÜNE', 'FDP', 'LINKE', 'AfD', 'FW', 'BSW', 'PDS', 'Rechte', 'PIRATEN', 'Linke.PDS',
            'REP/DVU', 'REP']
    # keep only relevant columns if they exist
    cols = [col for col in relevant_cols if col in df_cleaned.columns]
    data_cleaned = df_cleaned[cols]
    return data_cleaned


if __name__ == "__main__":
    
    if not os.path.exists("cache/Sonntagsfrage_cleaned.pkl"):
        build_archive()
        
    data = pd.read_pickle("cache/Sonntagsfrage_cleaned.pkl")
    for url in urls_current:
        print("Parsing URL:", url)
        org = get_organization_from_url(url)

        html = fetch_html(url)
        df = extract_table_data(html)
        df["org"] = org
        df.rename(columns={df.columns[0]: 'datum'}, inplace=True)
        df = df.reset_index()
        df = df.set_index(['datum', 'org'])
        df = df.replace(r'^\s*$', np.nan, regex=True)
        
        # we add all rows from df to data if data does not contain a row with datum) "date" and org=org
        if data is not None:
           unique_indices = df.index.difference(data.index) 
           df_unique = df.loc[unique_indices]
           df_unique_cleaned = clean_data(df_unique)           
           data = pd.concat([data, df_unique_cleaned])
        else:
            data = df
    
    data.to_pickle('cache/Sonntagsfrage_cleaned.pkl')