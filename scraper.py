from urls import urls
import requests
from bs4 import BeautifulSoup
import pandas as pd

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
def extract_table_data(html_content: str):
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', class_='wilko')

        table_header = table.find("thead")
        headers = [th.text.strip() for th in table_header.find_all('th')]
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

        # Create a Pandas DataFrame for easy manipulation
        df = pd.DataFrame(data, columns=headers[:len(data[0])])

        return df

def get_organization_from_url(s_url):
    base_url = "https://www.wahlrecht.de/umfragen/"
    rest = s_url.replace(base_url, "")
    parts = rest.split('/')
    org_name = parts[0]
    # Remove '.htm' or '.html' extensions if present
    org_name = org_name.replace('.htm', '').replace('.html', '')
    return org_name

data = None

for url in urls:
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


    if data is not None:
        duplicates = df.index.intersection(data.index)
        data= pd.concat([data, df])
    else:
        data = df

print(data)

# Optionally, save to CSV
data.to_pickle('Sonntagsfrage.pkl', index=False)