import asyncio
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

            all_ad_blocks = await page.query_selector_all(".xh8yej3") 

            for ad_block in all_ad_blocks:
                ad_elements_infos = await ad_block.query_selector_all(".x8t9es0.xw23nyj.xo1l8bm.x63nzvj.x108nfp6.xq9mrsl.x1h4wwuj.xeuugli") 
                for ad in ad_elements_infos:
                    ad_info = await ad.inner_text()
                    print("Ad Title (CSS):", ad_info)
                
                # Use query_selector instead of locator
                element = await ad_block.query_selector("text='See ad details'")  # Corrected here
                
                if element:  # Check if the element exists
                    print(f"Found element with the text 'See ad details'.")
                    await element.click()
                    await page.wait_for_timeout(2000)  # Wait for the modal to open

                    # Wait for the modal to be visible using its class
                    modal = await page.wait_for_selector(".x1qjc9v5.x9f619.x78zum5.xdt5ytf.x1nhvcw1.xg6iff7.xurb0ha.x1sxyh0.x1l90r2v")

                    # Close the modal
                    await page.click("text='Close'")  # Use the text selector for the close button
                    await page.wait_for_timeout(1000)  # Wait for the modal to close

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
