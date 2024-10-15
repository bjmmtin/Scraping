import asyncio
import re
from playwright.async_api import async_playwright

async def scrape_ads_library():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True for no UI
        page = await browser.new_page()

        # Intercept network requests
        await page.route("**/ads/library/**", lambda route: route.continue_())

        try:
            # Navigate to the Facebook Ads Library
            await page.goto("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&media_type=all&search_type=page&view_all_page_id=106091695497460", timeout=60000)

            # Wait for the page to load
            await page.wait_for_timeout(5000)  # Adjust based on your internet speed

            # Locate all elements containing the text "See summary details"
            elements = page.locator("text='See summary details'")  # Use locator instead of get_by_text

            # Get the count of elements found
            count = await elements.count()
            print(f"Found {count} elements with the text 'See summary details'.")

            # Iterate through the elements
            for i in range(count):
                element_text = await elements.nth(i).inner_text()
                print(f"Element {i + 1}: {element_text}")

            # Locate all elements containing the text "See ad details"
            elements = page.locator("text='See ad details'")  # Use locator instead of get_by_text

            # Get the count of elements found
            count = await elements.count()
            print(f"Found {count} elements with the text 'See ad details'.")

            # Iterate through the elements
            for i in range(count):
                element_text = await elements.nth(i).inner_text()
                print(f"Element {i + 1}: {element_text}")

            # Print the page title
            print("Page Title:", await page.title())

            # Take a screenshot
            await page.screenshot(path="screenshot.png", full_page=True)

            # Capture network responses
            async def handle_response(response):
                if "ads/library" in response.url:
                    try:
                        data = await response.json()
                        print(data)  # Process the data as needed
                    except Exception as e:
                        print("Error processing response:", e)

            page.on("response", handle_response)

            # Optionally, click to load more ads (uncomment and adjust selector if needed)
            # await page.click("selector-for-load-more-button")

            # Wait for some time to gather data
            await page.wait_for_timeout(10000)  # Adjust as needed

        except Exception as e:
            print("An error occurred:", e)

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_ads_library())
