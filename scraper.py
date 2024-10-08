import os
import pickle
from urls import urls, urls_current
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def fetch_html(url: str) -> str:
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
            duplicates = df.index.intersection(data.index)
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

    data_cleaned.to_pickle("Sonntagsfrage_cleaned.pkl")


def clean_data(df):
    df.reset_index(inplace=True)
    df['s_datum'] = df['datum']
    df.loc[:, 'datum'] = pd.to_datetime(df['s_datum'], format='%d.%m.%Y', errors='coerce')
    df_cleaned = df.dropna(subset=['datum'])
    df_cleaned.loc[:, 'month'] = df_cleaned['datum'].dt.month
    df_cleaned.loc[:, 'year'] = df_cleaned['datum'].dt.year
    df_cleaned.loc[:, 'week_of_year'] = df_cleaned['datum'].dt.isocalendar().week
    cols = ['datum', 'year', 'month', 'week_of_year', 'org', 'CDU/CSU', 'SPD', 'GRÜNE', 'FDP', 'LINKE', 'AfD', 'FW', 'BSW', 'PDS', 'Rechte', 'PIRATEN', 'Linke.PDS',
            'REP/DVU', 'REP']
    data_cleaned = df[cols]
    return data_cleaned


if __name__ == "__main__":
    
    if not os.path.exists("Sonntagsfrage.pkl"):
        build_archive()


#    data = pd.read_pickle("cache/Sonntagsfrage.pkl")
#    for url in urls_current:
#        org = get_organization_from_url(url)
#        html = fetch_html(url)
#        # Call the function and print the DataFrame
#        df = extract_table_data(html)
#
#        keys_to_drop = df.index.isin(data.index)
#        df = df[~keys_to_drop]
#        df = clean_data(df)
#        # drop all rows in df where the multiindex key (datum, org) already is in data
#        data = pd.concat([data, df])
#
#        data.to_pickle('cache/Sonntagsfrage.pkl')
#        print(f"Added {len(df)} new rows for {org}")