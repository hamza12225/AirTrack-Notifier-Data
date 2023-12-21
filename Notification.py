import requests
import csv
from dotenv import load_dotenv
import os

def send_flights_notification(flight_data):
    load_dotenv()
    keyAPI = os.getenv('MAILGUN_API_KEY')
    try:
        # Create a CSV file with flight data
        output_file = 'flight_data.csv'
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Destination', 'Airline', 'Departure Time', 'Arrival Time',
                'Departure Airport', 'Arrival Airport', 'Price', 'Duration','Flight url'
            ])
            for destination, flights in flight_data.items():
                for flight in flights:
                    writer.writerow([
                        destination,
                        flight['Airline'],
                        flight['Departure Time'],
                        flight['Arrival Time'],
                        flight['Departure Airport'],
                        flight['Arrival Airport'],
                        flight['Price'],
                        flight['Duration'],
                        flight['Flight URL']
                    ])

        # Send email with the CSV file attached
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxb9a70a2f408443a7ba683f03c0f176e5.mailgun.org/messages",
            auth=("api", f"{keyAPI}"),
            files=[("attachment", open(output_file, "rb"))],
            data={"from": "Excited User <haikihamza456@gmail.com>",
                  "to": ["hamzahaiki501@gmail.com"],
                  "subject": "Flight Data",
                  "text": "Please find the attached flight data."})

        # Check the response status
        if response.status_code == 200:
            print('Email sent successfully!')
        else:
            print('Failed to send email. Status code:', response.status_code)
            print('Error message:', response.text)
    except requests.RequestException as e:
        print('Failed to send email:', e)
