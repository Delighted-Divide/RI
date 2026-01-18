import requests
from bs4 import BeautifulSoup

url = "https://novelfull.com/reverend-insanity/chapter-1.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.find(id='chapter-content')
        if content:
            print("Content found!")
            # Print first 200 chars of text
            print(content.get_text()[:200])
        else:
            print("Content not found.")
        
        next_chap = soup.find(id='next_chap')
        if next_chap:
            print(f"Next Chapter Link: {next_chap.get('href')}")
        else:
            print("Next Chapter Link not found.")
except Exception as e:
    print(f"Error: {e}")
