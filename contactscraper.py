import re
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


def scrape_contact_info(urls):
    all_data = []

    for url in urls:
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            wait = WebDriverWait(driver, 10)
            driver.get(url)
            get_url = driver.current_url
            wait.until(EC.url_to_be(url))

            if get_url != url:
                continue
            page_source = driver.page_source

            soup = BeautifulSoup(page_source, "html.parser")

            phone_numbers = set()
            emails = set()

            # Find phone numbers using a regular expression
            for text in soup.stripped_strings:
                matches = re.findall(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text)
                phone_numbers.update(matches)

                # Find emails using a regular expression
                email_matches = re.findall(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
                )
                emails.update(email_matches)

            print(f"Found phone numbers on {url}: {phone_numbers}")
            print(f"Found emails on {url}: {emails}")

            # Store data in a list of dictionaries
            site_data = {
                "URL": url,
                "Phone Numbers": ", ".join(phone_numbers),
                "Emails": ", ".join(emails),
            }
            all_data.append(site_data)

            # Find the link to the next page
            next_page_link = soup.find(
                "a", text=re.compile(r"Next|>>|»", re.IGNORECASE)
            )

            if next_page_link:
                next_page_url = next_page_link.get("href")
                phone_numbers_next, emails_next = scrape_contact_info([next_page_url])
                phone_numbers.update(phone_numbers_next)
                emails.update(emails_next)

                # Introduce a delay between requests
                time.sleep(1)

            driver.close()

        except Exception as e:
            print(f"Error: {e}")

    return all_data


def main():
    # Example usage with multiple URLs:
    # sites = [
    #     "https://www.numtracker.com/city/pune",
    #     "https://fastag.bank.sbi/PgTickerTermscond"
    # ]

    with open("hotel_list.txt") as f:
        sites = f.readlines()

    data = scrape_contact_info(sites)

    # Write the data to a CSV file
    csv_filename = "scraped_data.csv"
    fields = ["URL", "Phone Numbers", "Emails"]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fields)

        # Write the header
        csv_writer.writeheader()

        # Write the data
        csv_writer.writerows(data)

    print(f"\nScraped data has been stored in {csv_filename}")


if __name__ == "__main__":
    main()
