from urls import urls
import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_html(url: str) -> str:
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

data = None

def get_organization_from_url(s_url):
    base_url = "https://www.wahlrecht.de/umfragen/"
    rest = s_url.replace(base_url, "")
    parts = rest.split('/')
    org_name = parts[0]
    # Remove '.htm' or '.html' extensions if present
    org_name = org_name.replace('.htm', '').replace('.html', '')
    return org_name

for url in urls[:3]:
    org = get_organization_from_url(url)

    html = fetch_html(url)
    # Call the function and print the DataFrame
    df = extract_table_data(html)
    df["org"] = org
    df = df.reset_index(name='datum')
    df = df.set_index(['datum', 'org'])

    print(df)
    if data is not None:
        data= pd.concat([data, df])
    else:
        data = df

print(data)

# Optionally, save to CSV
data.to_pickle('Sonntagsfrage.pkl', index=False)