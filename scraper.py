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

       # Find all rows in the table body
       rows = table.find_all('tr')

       data = []
       headers = []

       # Get the table headers
       header_row = rows[0]
       headers = [th.text.strip() for th in header_row.find_all('th') if th.text.strip()]

       # Iterate over the rows and extract data
       for row in rows[1:]:
              cells = row.find_all('td')
              row_data = []

              # Extract each cell's text, cleaning any unwanted characters
              for cell in cells:
                     text = cell.text.strip().replace('–', 'N/A').replace('\xa0', ' ')
                     row_data.append(text)

              # Append the row to the data list if it's not empty
              if row_data:
                     data.append(row_data)

       # Create a Pandas DataFrame for easy manipulation
       df = pd.DataFrame(data, columns=headers[:len(data[0])])

       return df


for url in urls:
       html = fetch_html(url)
       # Call the function and print the DataFrame
       df = extract_table_data(html)
       print(df)

       # Optionally, save to CSV
       df.to_csv('table_data.csv', index=False)
       break
