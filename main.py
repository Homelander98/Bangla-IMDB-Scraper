from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_imdb_bangla_movies():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=Options())

    movies = []
    for page in range(1, 201, 50):  # Loop through pages
        url = f"https://www.imdb.com/search/title/?languages=bn&title_type=movie,tvSeries&count=50&start={page}"
        print(f"Scraping {url}...")
        driver.get(url)

        try:
            WebDriverWait(driver, 40).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ipc-title__text"))
            )
        except TimeoutException:
            print(f"Timeout while waiting for elements on page {page}. Check the page structure.")
            continue  # Skip to the next page

        # Scroll down to trigger dynamic content loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load

        # Parse the page source
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", class_="sc-300a8231-0 gTnHyA")

        if not results:
            print(f"No results found on page {page}. Check HTML structure.")
        else:
            for result in results:
                # Extract title
                title = result.find("h3", class_="ipc-title__text").text.strip() if result.find("h3",
                                                                                                class_="ipc-title__text") else "N/A"

                # Extract year
                year = result.find("span", class_="sc-300a8231-7").text.strip() if result.find("span",
                                                                                               class_="sc-300a8231-7") else "N/A"

                # Extract rating
                rating = result.find("span", class_="ipc-rating-star--rating")
                rating = rating.text.strip() if rating else "N/A"

                # Extract type (Movie/TV Series)
                movie_type = result.find("span", class_="dli-title-type-data").text.strip() if result.find("span",
                                                                                                           class_="dli-title-type-data") else "N/A"

                # Append the extracted data
                movies.append({"Title": title, "Year": year, "Rating": rating, "Type": movie_type})

    driver.quit()

    if movies:
        df = pd.DataFrame(movies)
        df.to_csv("bangla_movies_and_webseries.csv", index=False)
        print("Data saved to bangla_movies_and_webseries.csv")
    else:
        print("No movies scraped. Check page structure or scraper logic.")


scrape_imdb_bangla_movies()
