from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import requests
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time

chrome = webdriver.Chrome("C:\chromedriver\chromedriver.exe")
webdriver = chrome

URL = r"https://www.google.com/search?q=aachen%20friseur&rlz=1C1CHBF_deDE814DE814&oq=aachen+f&aqs=chrome.0.69i59j69i57j0i512j46i175i199i512l2j69i60l3.1100j0j7&sourceid=chrome&ie=UTF-8&tbs=lf:1,lf_ui:14&tbm=lcl&sxsrf=AOaemvJlq7Ff6K0HHKYUghGqUQkD_8su_Q:1641467197818&rflfq=1&num=10&rldimm=15521606472338731331&lqi=Cg5hYWNoZW4gZnJpc2V1ckjf2NXw5YCAgAhaHBAAEAEYABgBIg5hYWNoZW4gZnJpc2V1cjICZGWSAQpoYWlyX3NhbG9uqgEPEAEqCyIHZnJpc2V1cigF&ved=2ahUKEwi5t_Hp_Zz1AhUCSPEDHWX1BKsQvS56BAgLEGw&rlst=f#lrd=0x47c0997e8732aec1:0xd767d2d97f277143,1,,,&rlfi=hd:;si:15521606472338731331,l,Cg5hYWNoZW4gZnJpc2V1ckjf2NXw5YCAgAhaHBAAEAEYABgBIg5hYWNoZW4gZnJpc2V1cjICZGWSAQpoYWlyX3NhbG9uqgEPEAEqCyIHZnJpc2V1cigF;mv:[[50.82298355098014,6.172987092208717],[50.73810512176909,5.91549502677903]]"

Reviewer = []
ReviewDate = []
ReviewRating = []
ReviewDescription = []
TotalReviewsByUser = []
last_len = 0


def extract_review_data(review_obj):
    # Finding the Name
    username = review_obj.find_element_by_class_name("TSUbDb").text

    # extracting the total number of reviews by user
    try:
        num_reviews_by_user = review_obj.find_element_by_class_name("A503be").text
    except NoSuchElementException:
        num_reviews_by_user = ""

    # extracting the rating
    rating_by_user = review_obj.find_element_by_class_name("EBe2gf").get_attribute(
        "aria-label"
    )

    # extracting the date
    review_date = review_obj.find_element_by_class_name("dehysf").text

    # extracting the description
    Body = review_obj.find_element_by_class_name("Jtu6Td")
    try:
        review_obj.find_element_by_class_name("review-more-link").click()
        review_text = review_obj.find_element_by_class_name("review-full-text").text
        print(review_text)
    except NoSuchElementException:
        review_text = Body.text
        print(review_text)

    print(f"Review Scraped by : {username}")

    return {
        "username": username,
        "num_reviews_by_user": num_reviews_by_user,
        "rating_by_user": rating_by_user,
        "review_date": review_date,
        "review_text": review_text,
    }


def get_reviews(review_list):
    global last_len
    print("Scrolling Complete, Continuing...")

    # data from a single review
    for review_obj in review_list.find_elements_by_class_name(
        "gws-localreviews__google-review"
    ):

        # Finding the Name
        Name = review_obj.find_element_by_class_name("TSUbDb")
        Reviewer.append(Name.text)

        # extracting the total number of reviews by user
        try:
            ReviewByuser = review_obj.find_element_by_class_name("A503be")
            TotalReviewsByUser.append(ReviewByuser.text)
        except NoSuchElementException:
            TotalReviewsByUser.append("")

        # extracting the rating
        star = review_obj.find_element_by_class_name("EBe2gf")
        ReviewStar = star.get_attribute("aria-label")
        ReviewRating.append(ReviewStar)

        # extracting the date
        Date = review_obj.find_element_by_class_name("dehysf")
        ReviewDate.append(Date.text)

        # extracting the description
        Body = review_obj.find_element_by_class_name("Jtu6Td")
        try:
            review_obj.find_element_by_class_name("review-more-link").click()
            s_32B = review_obj.find_element_by_class_name("review-full-text")
            ReviewDescription.append(s_32B.text)
            print(s_32B.text)
        except NoSuchElementException:
            ReviewDescription.append(Body.text)

        print(f"Review Scraped by : {Name.text}")

        # scrolling the next like into view to load the next review
        element = review_obj.find_element_by_class_name("hTt9T")
        webdriver.execute_script("arguments[0].scrollIntoView();", element)

    print(f"Current Length: {len(Reviewer)}")
    time.sleep(3)
    reviews = webdriver.find_elements_by_class_name(
        "gws-localreviews__general-reviews-block"
    )
    r_len = len(reviews)
    if r_len > last_len:
        last_len = r_len
        get_reviews(reviews[r_len - 1])


# google consenting
webdriver.get("https://www.google.de/")
time.sleep(3)
webdriver.find_element(by="id", value="L2AGLb").click()
time.sleep(3)

# going to the reviev page
webdriver.get(URL)
time.sleep(3)

# getting the reviews
reviews = webdriver.find_elements_by_class_name(
    "gws-localreviews__general-reviews-block"
)
# extracting current length of reviews
last_len = len(reviews)

# starting the loop
get_reviews(reviews[last_len - 1])

data = pd.DataFrame(
    {
        "Reviewer": Reviewer,
        "TotalReviewsByUser": TotalReviewsByUser,
        "ReviewRating": ReviewRating,
        "ReviewDate": ReviewDate,
        "ReviewDescription": ReviewDescription,
    }
)

data.to_csv("Freigeist_Friseure.csv", index=False, encoding="utf-8-sig")
