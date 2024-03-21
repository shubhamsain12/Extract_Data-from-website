

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import pandas as pd
import time

# Use requests and BeautifulSoup to extract name, price, and location
url = "https://www.tradeindia.com/jaipur/paper-printing-services-city-197559.html"
webpage = requests.get(url)
soup = BeautifulSoup(webpage.content, "html.parser")

name_elems = soup.find_all("h3", class_='sc-99c38e0-14 jABSuU mt-2 Body4R coy-name')
price_elems = soup.find_all("p", class_='sc-99c38e0-14 jARKuT Body3R mb-1')
location_elems = soup.find_all("span", class_='sc-99c38e0-14 fZNuPr mb-1 Body4R')

# Extracting text from elements
names = [name.text.strip() for name in name_elems] if name_elems else []
prices = [price.text.strip() for price in price_elems] if price_elems else []
locations = [loc.text.strip() for loc in location_elems] if location_elems else []

# Fill missing values with a placeholder to ensure all lists have the same length
max_length = max(len(names), len(prices), len(locations))
names += ['Not available'] * (max_length - len(names))
prices += ['Not available'] * (max_length - len(prices))
locations += ['Not available'] * (max_length - len(locations))

# Print the extracted data from BeautifulSoup
print(f"Names: {names}")
print(f"Prices: {prices}")
print(f"Locations: {locations}")

# Initialize the Chrome driver using Selenium
driver = webdriver.Chrome()

try:
    # Open the URL
    driver.get(url)

    # Handle pop-up if present
    close_popup = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/main/div[1]/div[4]/div/div[1]/button')))
    close_popup.click()
    time.sleep(2)  # Add a short delay after closing the popup

    # Find all cards using Selenium
    cards = driver.find_elements(By.XPATH, '//*[@id="__next"]/div/main/div[1]/div[1]/div[1]/div[6]')

    # Store all the numbers in a list
    numbers_list = []

    # Loop through each card
    for card in cards:
        try:
            # Find the "View Number" button within the card and wait for it to be clickable
            view_button = WebDriverWait(card, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/main/div[1]/div[1]/div[1]/div[6]/div[1]/div/div[2]/button[2]/span[2]')))
            view_button.click()
            time.sleep(5)  # Add a delay after clicking the button

            # Extract all numbers displayed after clicking the button
            number_elems = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '//span[@class="d-none d-md-block"]')))
            numbers = [elem.text.strip() for elem in number_elems]
            numbers_list.extend(numbers)

            # Go back to the previous page to click on the next card's "View Number" button
            driver.back()
        except TimeoutException:
            print("Timeout waiting for number elements to be visible.")
        except Exception as e:
            print(f"Error processing card: {e}")
            continue

    # Fill missing values with a placeholder for numbers list
    numbers_list += ['Not available'] * (max_length - len(numbers_list))

    # Print all the numbers extracted using Selenium
    print("All Numbers:")
    for number in numbers_list:
        print(number)

    # Close the browser
    driver.quit()

    # Check if all lists have the same length
    if len(names) == len(prices) == len(locations) == len(numbers_list):
        # Create a DataFrame using pandas
        data = {'Name': names, 'Location': locations, 'Price': prices, 'Phone Number': numbers_list}
        df = pd.DataFrame(data)

        # Save DataFrame to Excel file
        df.to_excel("tradeindia_data.xlsx", index=False)

        print("Data saved to Excel file.")
    else:
        print("Error: Lists do not have the same length. Data not saved.")
except Exception as e:
    print(f"Error: {e}")
    driver.quit()
