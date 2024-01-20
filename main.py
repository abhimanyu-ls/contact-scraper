import time
from playwright.sync_api import sync_playwright


def main():
    links = []

    with sync_playwright() as p:
        page_url = "https://www.tripadvisor.in/Hotels-g297584-Port_Blair_South_Andaman_Island_Andaman_and_Nicobar_Islands-Hotels.html"
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(page_url, timeout=120000)
        # page.set_default_timeout(timeout=120000)

        hotel_listings = page.locator(
            '//div[@data-automation="hotel-card-title"]'
        ).all()
        print(len(hotel_listings))

        for hotel_listing in hotel_listings:
            hotel_page_url = hotel_listing.locator(
                '//a[@target="_blank"]'
            ).get_attribute("href")
            links.append("https://tripadvisor.com" + hotel_page_url)
        browser.close()

    with open("hotel_list.txt", 'w') as f:
        for link in links:
            f.write(f"{link}\n")


if __name__ == "__main__":
    main()
