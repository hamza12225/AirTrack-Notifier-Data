from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import csv
import logging

def scrape_kayak_flights(destinations, start_date, end_date):
    load_dotenv()
    URL = os.getenv('KAYAK_URL')    
    webdriver_path = r'C:\Users\Hamza Elhaiki\Desktop\driver\geckodriver.exe'
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    
    aed_to_mad_rate = 2.76  
    flight_info_dict = {}

    for destination in destinations:
        url = f'https://www.kayak.ae/flights/CMN-{destination}/{start_date}/{end_date}'
        service = Service(executable_path=webdriver_path)
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url)
        wait = WebDriverWait(driver, 10)  # Wait for a maximum of 10 seconds
        try:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'nrc6-inner')))
            flight_results = driver.find_elements(By.CLASS_NAME, 'nrc6-inner')
        except NoSuchElementException as e:
            logging.error(f"Error while loading page for {destination}: {e}")
            driver.quit()
            continue

        flight_info_list = []

        for result in flight_results:
            try:
                flight_info = {}
                
                time_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'vmXl-mod-variant-large')))
                times = time_element.find_elements(By.TAG_NAME, 'span')
                departure_time = times[0].text.strip()
                arrival_time = times[2].text.strip().replace('\n+1', '')

                airport_elements = result.find_elements(By.XPATH, ".//span[@class='EFvI-ap-info']")
                departure_name = airport_elements[0].find_elements(By.TAG_NAME, 'span')[1].text.strip() if len(airport_elements) > 0 else 'N/A'
                arrival_name = airport_elements[1].find_elements(By.TAG_NAME, 'span')[1].text.strip() if len(airport_elements) > 1 else 'N/A'

                airline_element = result.find_element(By.CLASS_NAME, 'J0g6-operator-text')
                airline_name = airline_element.text.strip() if airline_element else 'N/A'

                duration_element = result.find_element(By.CLASS_NAME, 'xdW8-mod-full-airport')
                duration = duration_element.find_element(By.CLASS_NAME, 'vmXl-mod-variant-default').text.strip() if duration_element else 'N/A'

                flight_url = result.find_element(By.CSS_SELECTOR, 'a.Iqt3').get_attribute('href')

                try:
                    price_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'f8F1-price-text-container'))
                    )
                    price_text = price_container.text.strip() if price_container else 'N/A'
                    price_currency_split = price_text.split(' ')
                    price_value = float(price_currency_split[1].replace(',', '')) 
                    currency = price_currency_split[0]

                    if currency == 'AED':
                        price_value = round(float(str(price_value).replace(',', '')) * aed_to_mad_rate, 2)
                        currency = 'MAD'
                except NoSuchElementException:
                    price_value, currency = 'N/A', 'N/A'

                flight_info.update({
                    'Airline': airline_name,
                    'Departure Time': departure_time,
                    'Arrival Time': arrival_time,
                    'Departure Airport': departure_name,
                    'Arrival Airport': arrival_name,
                    'Price': price_value,
                    'Duration': duration,
                    'Flight URL': flight_url
                })
                flight_info_list.append(flight_info)

            except NoSuchElementException as e:
                logging.error(f"Error scraping {destination}: {e}")

        driver.quit()
        flight_info_dict[destination] = flight_info_list

    return flight_info_dict

def save_flight_data_to_csv(flight_data):
    try:
        with open('flight_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'Destination', 'Airline', 'Departure Time', 'Arrival Time',
                'Departure Airport', 'Arrival Airport', 'Price', 'Duration', 'Flight URL'
            ])
            writer.writeheader()
            for destination, flights in flight_data.items():
                for flight in flights:
                    flight['Destination'] = destination  # Add the destination key to each flight dictionary
                    writer.writerow(flight)
        print('Flight data saved to flight_data.csv')
    except IOError as e:
        print(f"Error saving flight data: {e}")

# Your existing code remains the same until the end

# destinations = ['NYC', 'PAR', 'ROM', 'STO','DXB']
# start_date = '2024-01-05'
# end_date = '2024-01-12'
# flight_data = scrape_kayak_flights(destinations, start_date, end_date)

# save_flight_data_to_csv(flight_data)

