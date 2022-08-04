import time

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

file_name = "Aachen_Barbershop_Reviews.csv"
URL = r"https://www.google.com/search?q=barbershop%20aachen&rlz=1C1CHBF_deDE814DE814&oq=bar&aqs=chrome.0.69i59j69i57j69i59j69i65l2j69i60l2j69i61.819j0j9&sourceid=chrome&ie=UTF-8&tbs=lf:1,lf_ui:14&tbm=lcl&sxsrf=AOaemvLgCujTpNE2aSVfNPMZWmmg8Jrr7A:1641479505719&rflfq=1&num=10&rldimm=17192299855451658527&lqi=ChFiYXJiZXJzaG9wIGFhY2hlbki0zZSn56qAgAhaJRAAEAEYABgBIhFiYXJiZXJzaG9wIGFhY2hlbioECAMQADICZGWSAQpoYWlyX3NhbG9umgEkQ2hkRFNVaE5NRzluUzBWSlEwRm5TVU5MTFdNM2J5MVJSUkFCqgESEAEqDiIKYmFyYmVyc2hvcCgF&ved=2ahUKEwiVluDWq531AhVOjqQKHeQ4CPEQvS56BAgLEFQ&rlst=f#lrd=0x47c09979e37b42db:0xee9751a13c32191f,1,,,&rlfi=hd:;si:17192299855451658527,l,ChFiYXJiZXJzaG9wIGFhY2hlbki0zZSn56qAgAhaJRAAEAEYABgBIhFiYXJiZXJzaG9wIGFhY2hlbioECAMQADICZGWSAQpoYWlyX3NhbG9umgEkQ2hkRFNVaE5NRzluUzBWSlEwRm5TVU5MTFdNM2J5MVJSUkFCqgESEAEqDiIKYmFyYmVyc2hvcCgF;mv:[[50.79779,6.169645099999999],[50.7465738,6.068955]]"
scraped_reviews = []


def extract_review_data(review_obj):
    # Extract the Positive etc... Data
    # Atrributes : Positive, Service,
    # Extract the Response of the owner

    # Finding the Name
    user_name = review_obj.find_element(By.CLASS_NAME, "TSUbDb").text

    # extracting the subdescription of the user
    # initalize the default value of the subdescription
    user_num_reviews = 1
    user_num_photos = 0
    user_is_local_guide = False
    try:

        # Split the subdescription into a list, the list has review number, photos and if the user is a local guide
        review_subdesc = review_obj.find_element(By.CLASS_NAME, "A503be")
        attribute_array = review_subdesc.text.split("·")

        # extract each attribute
        for attribute in attribute_array:
            attribute = attribute.strip()
            if "photo" in attribute:
                user_num_photos = int(attribute.split(" ")[0])
            elif "Local Guide" in attribute:
                user_is_local_guide = True
            elif "review" in attribute:
                user_num_reviews = int(attribute.split(" ")[0])

    except NoSuchElementException:
        user_num_reviews = 1
        user_num_photos = 0
        user_is_local_guide = False

    # extracting the rating
    rating_text = review_obj.find_element(By.CLASS_NAME, "EBe2gf").get_attribute(
        "aria-label"
    )
    user_rating = int(rating_text.split(" ")[1].split(",")[0])

    # extracting the date
    user_review_date = review_obj.find_element(By.CLASS_NAME, "dehysf").text

    # extracting the description
    description_body = review_obj.find_element(By.CLASS_NAME, "Jtu6Td")
    try:
        # expand the description
        description_body.find_element(By.CLASS_NAME, "review-more-link").click()
        user_review_description = description_body.find_element(
            By.CLASS_NAME, "review-full-text"
        ).text

        print("Successfully scraped review description, Big Description")
    except NoSuchElementException:
        user_review_description = description_body.text
        print("Successfully scraped review description, Small Description")
    except ElementClickInterceptedException:
        print("ElementClickInterceptedException")
        user_review_description = ""

    # process the user description
    user_review_description_original = ""
    user_review_description_translated = ""

    # split the string into Original and Translated
    if user_review_description.startswith("(Translated by Google)"):
        user_review_description = user_review_description.split("(Original)")
        # remove the first 23 characters ("(Translated by Google)")
        user_review_description_translated = user_review_description[0].strip(" \n")[
            23:
        ]
        user_review_description_original = user_review_description[1].strip(" \n")
    else:
        user_review_description_original = user_review_description.strip(" \n")

    print(f"Review Scraped by : {user_name}")

    return {
        "user_name": user_name,
        "user_num_reviews": user_num_reviews,
        "user_num_photos": user_num_photos,
        "user_is_local_guide": user_is_local_guide,
        "user_rating": user_rating,
        "user_review_date": user_review_date,
        "user_review_description_original": user_review_description_original,
        "user_review_description_translated": user_review_description_translated,
    }


def scrape_page(review_page, current_page):

    # extract the reviews
    review_list = review_page.find_elements(
        By.CLASS_NAME, "gws-localreviews__google-review"
    )

    # data from a single review
    for review_obj in review_list:
        # scrolling the like into view to load the review
        like_div = review_obj.find_element(By.CLASS_NAME, "hTt9T")
        driver.execute_script("arguments[0].scrollIntoView();", like_div)

        extracted_review_data = extract_review_data(review_obj)
        scraped_reviews.append(extracted_review_data)

    # Wait to load the next page
    time.sleep(3)

    # get all the current review pages
    review_pages = driver.find_elements(
        By.CLASS_NAME, "gws-localreviews__general-reviews-block"
    )
    num_pages = len(review_pages)
    # if more pages have been loaded continue to scrape
    if num_pages > current_page + 1:
        # get the next page of reviews
        scrape_page(review_pages[current_page + 1], current_page + 1)


# google consenting
driver.get("https://www.google.de/")
time.sleep(3)
driver.find_element(by="id", value="L2AGLb").click()
time.sleep(3)

# going to the review page
driver.get(URL)
time.sleep(3)

# getting the first review page
review_pages = driver.find_elements(
    By.CLASS_NAME, "gws-localreviews__general-reviews-block"
)

# Start scraping the first page
# page 1 are the first 3 revies shown before clicking to load more reviews
# this means we have to start at page 2
if len(review_pages) > 1:
    scrape_page(review_pages[1], current_page=1)

data = pd.DataFrame(scraped_reviews)

data.to_csv(file_name, index=False, encoding="utf-8-sig")
