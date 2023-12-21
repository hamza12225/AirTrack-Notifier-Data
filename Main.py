from Notification import send_flights_notification
from scraping2 import scrape_kayak_flights

destinations = ['NYC','PAR','ROM','YYZ']
start_date = '2024-01-05'
end_date = '2024-01-12'
flight_data = scrape_kayak_flights(destinations, start_date, end_date)
send_flights_notification(flight_data)



