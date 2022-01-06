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

URL = r"https://www.google.com/search?q=barbershop%20aachen&rlz=1C1CHBF_deDE814DE814&oq=barber&aqs=chrome.0.69i59j69i57j0i20i263i512l2j0i457i512j0i512j69i60l2.1299j0j7&sourceid=chrome&ie=UTF-8&tbs=lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!1m4!1u16!2m2!16m1!1e1!1m4!1u16!2m2!16m1!1e2!2m1!1e2!2m1!1e16!2m1!1e3!3sIAE,lf:1,lf_ui:14&tbm=lcl&sxsrf=AOaemvKaylUIois018_x7ELTUQscLTsPjw:1641473374348&rflfq=1&num=10&rldimm=17192299855451658527&rllas=1&ved=2ahUKEwi79IrrlJ31AhVvQ_EDHZ3PC_gQ764BegQICxA8&rlst=f#lrd=0x47c09956dd743b5b:0xc49f3b87fa37dead,1,,,&rlfi=hd:;si:14168108407935458989,l,ChFiYXJiZXJzaG9wIGFhY2hlbkiA2dCUm6uAgAhaJRAAEAEYABgBIhFiYXJiZXJzaG9wIGFhY2hlbioECAMQADICZGWSAQtiYXJiZXJfc2hvcJoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VSUmJrMHliMFpCRUFFqgESEAEqDiIKYmFyYmVyc2hvcCgF;mv:[[50.79779,6.169645099999999],[50.7465738,6.068955]]"
scraped_reviews = []


def extract_review_data(review_obj):

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
                user_num_photos = attribute.split(" ")[0]
            elif "Local Guide" in attribute:
                user_is_local_guide = True
            elif "review" in attribute:
                user_num_reviews = attribute.split(" ")[0]

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

    print(f"Review Scraped by : {user_name}")

    return {
        "user_name": user_name,
        "user_num_reviews": user_num_reviews,
        "user_num_photos": user_num_photos,
        "user_is_local_guide": user_is_local_guide,
        "user_rating": user_rating,
        "user_review_date": user_review_date,
        "user_review_description": user_review_description,
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

data.to_csv("Freigeist_Friseure.csv", index=False, encoding="utf-8-sig")
