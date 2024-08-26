#novel-list col5 m-col4
from bs4 import BeautifulSoup
import requests
import random
import os

# Define headers to mimic browser requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def main(number_of_novels: int) -> None:
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
            return

        
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        novels_list = soup.find('ul', class_='novel-list col5 m-col4')
        if novels_list is None:
            print("No 'ul' with class 'novel-list col5 m-col4' found.")
            return []

        li_of_novels = novels_list.find_all('li')
        if not li_of_novels:
            print("No 'li' elements found inside the 'ul.novel-list col5 m-col4'.")
            return []

        # Collect all the 'a' tags from the 'li' elements
        links = [li.find('a') for li in li_of_novels if li.find('a') is not None]
        
        if not links:
            print("No 'a' tags found inside 'li' elements.")
            return []
        
        import webscrapers.lightNovelPubDotVip.getPics
        import webscrapers.lightNovelPubDotVip.genChapters
        
        for i in range(number_of_novels):
            # Randomly select a novel link
            random_novel = random.choice(links)
            
            # Print the href attribute which is the URL of the novel
            print("Selected Novel URL:", random_novel['href'])
            
            full_url = f"https://lightnovelpub.vip/{random_novel['href']}"
            
            
            webscrapers.lightNovelPubDotVip.genChapters.yes(base_url=full_url)
            webscrapers.lightNovelPubDotVip.getPics.main(base_url=full_url)
            
            print(f"Scraped {i} novel")
                    

    except requests.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")

def start():
        try:
            num = int(input("(Max 15)\nEnter the number of novels youd like to scrape: "))
            if int(num) > 15:
                os.system('cls')
                print("Please enter a number less than or equal to 15")
                start()
            elif num == int(num):
                os.system('cls')
                main(number_of_novels=int(num))
                print("Scraping completed!")
            else:
                os.system('cls')
                print("Please enter a whole number")
                start()
        except ValueError as e:
            print(e)
            start()

if __name__ == "__main__":
    os.system('cls')
    start()