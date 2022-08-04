# App Reviews Scraper
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

url = "https://play.google.com/store/apps/details?id=com.android.chrome&hl=en&showAllReviews=true"

# make request
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)
SCROLL_PAUSE_TIME = 5

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
time.sleep(SCROLL_PAUSE_TIME)

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break
    last_height = new_height

# Get everything inside <html> tag including javscript
html = driver.execute_script(
    "return document.getElementsByTagName('html')[0].innerHTML"
)
soup = BeautifulSoup(html, "html.parser")

reviewer = []
date = []

# review text
for span in soup.find_all("span", class_="X43Kjb"):
    reviewer.append(span.text)

# review date
for span in soup.find_all("span", class_="p2TkOb"):
    date.append(span.text)

print(len(reviewer))
print(len(date))
