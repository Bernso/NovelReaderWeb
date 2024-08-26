#novel-list col5 m-col4
from bs4 import BeautifulSoup
import requests
# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def main(number_of_novels):
    try:
        print("Options:\n1. New Novel\n2. Recently Updated Novel\n3. Popular Novel")
        user_choice = int(input("Enter a number: "))
        if user_choice == 1:
            base_url = "https://lightnovelpub.vip/browse/genre-all-25060123/order-new/status-all"
        elif user_choice == 2:
            base_url = "https://lightnovelpub.vip/browse/genre-all-25060123/order-updated/status-all"
        elif user_choice == 3:
            base_url = "https://lightnovelpub.vip/browse/genre-all-25060123/order-popular/status-all"
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")
            main(number_of_novels=number_of_novels)    
        
    
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        categories_div = soup.find('div', class_='categories')
        if categories_div is None:
            print("No 'div' with class 'categories' found.")
            return []

        ul = categories_div.find('ul')
        if ul is None:
            print("No 'ul' found inside the 'div.categories'.")
            return []

        list_items = ul.find_all('li')
        categories = [item.get_text(strip=True) for item in list_items]

        return categories

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"Error scraping categories: {e}")
        return []