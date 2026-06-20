import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os

# Target URL
BASE_URL = 'http://books.toscrape.com/catalogue/category/books/science_22/index.html'

def fetch_html(url):
    """Fetches the HTML content of a page with error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as req_err:
        print(f"[-] An error occurred: {req_err}")
        return None

def parse_books(html_content):
    """Parses HTML content and extracts book data."""
    soup = BeautifulSoup(html_content, 'html.parser')
    books_data = []
    
    # CSS Selector to find all book containers
    articles = soup.select('article.product_pod')
    
    for article in articles:
        try:
            # FIX: Check if title_element exists BEFORE accessing its attributes
            title_element = article.select_one('h3 a')
            if title_element and title_element.has_attr('title'):
                title = title_element['title']
            else:
                title = 'Unknown Title'
                
            price_element = article.select_one('div.product_price p.price_color')
            price = price_element.text if price_element else '0'
            
            availability_element = article.select_one('div.product_price p.instock.availability')
            availability = availability_element.text.strip() if availability_element else 'Unknown'
            
            rating_element = article.select_one('p.star-rating')
            rating_class = rating_element['class'][1] if rating_element and len(rating_element['class']) > 1 else 'None'
            
            books_data.append({
                'Title': title,
                'Price': price,
                'Availability': availability,
                'Rating': rating_class
            })
        except Exception as e:
            print(f"[-] Error parsing an article: {e}")
            
    return books_data

def clean_and_save_data(books_data, output_dir):
    """Cleans the data and saves it to CSV and Excel."""
    if not books_data:
        print("[-] No data found to save.")
        return
        
    df = pd.DataFrame(books_data)
    
    # Cleaning Process
    df['Price'] = df['Price'].str.extract(r'(\d+\.\d+)').astype(float)
    
    rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5, 'None': 0}
    df['Rating'] = df['Rating'].map(rating_map)
    
    df['Availability'] = df['Availability'].apply(lambda x: 'In Stock' if 'In stock' in x else 'Out of Stock')
    
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)
    
    # Save Data
    csv_path = os.path.join(output_dir, 'science_books_dataset.csv')
    excel_path = os.path.join(output_dir, 'science_books_dataset.xlsx')
    
    df.to_csv(csv_path, index=False, encoding='utf-8')
    df.to_excel(excel_path, index=False)
    print(f"[+] Files successfully saved to {output_dir}")

def main():
    # Fixed file pathway logic for notebook/script compatibility
    try:
        output_directory = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        output_directory = os.getcwd()
        
    html_content = fetch_html(BASE_URL)
    if html_content:
        books = parse_books(html_content)
        clean_and_save_data(books, output_directory)
        time.sleep(random.uniform(1.5, 3.5))

if __name__ == '__main__':
    main()
