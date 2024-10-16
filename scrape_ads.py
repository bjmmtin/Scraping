import asyncio
from playwright.async_api import async_playwright, ElementHandle
import pandas as pd  # type: ignore

async def get_parent(element: ElementHandle, nth: int):
    if element:
        current_element = element
        for i in range(nth):
            current_element = await current_element.evaluate_handle("el => el.parentElement")
            if current_element is None:
                print(f"{nth}th Element not found at level {i + 1}")
                return None
        return current_element
    else:
        print("Provided element is None.")
        return None

async def scrape_ads_library(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.route("**/ads/library/**", lambda route: route.continue_())

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(5000)

            all_ad_blocks = await page.query_selector_all(".xh8yej3")
            ads_data = []

            for ad_block in all_ad_blocks:
                ad_info = {}
                see_detail_element = await ad_block.query_selector("text='See ad details'")  
                
                if see_detail_element:
                    print("Found element with the text 'See ad details'.")
                    await see_detail_element.click()
                    await page.wait_for_timeout(5000)

                    element = await page.query_selector("text='Ad Details'")
                    modal_element = await get_parent(element, 9)

                    if modal_element:
                        # Extracting basic info
                        library_id_element = await modal_element.query_selector("text='Platforms'")
                        basic_info_parent = await get_parent(library_id_element, 2)
                        if basic_info_parent:
                            basic_info = await basic_info_parent.inner_text()
                            ad_info['basic_info'] = basic_info.strip()
                            print("Basic info:", ad_info['basic_info'])
                        
                        # Extracting about the advertiser
                        element = await modal_element.query_selector("text='About the advertiser'")
                        about_advertiser = await get_parent(element, 2)
                        if about_advertiser:
                            await about_advertiser.click()
                            await page.wait_for_timeout(500)
                            element = await modal_element.query_selector("text='More info'")
                            more_info = await get_parent(element, 2)
                            if more_info:
                                info_text = await more_info.inner_text()
                                ad_info['about_advertiser'] = info_text.strip()
                                print("About the advertiser:", ad_info['about_advertiser'])

                        # Extracting beneficiary and payer
                        element = await modal_element.query_selector("text='Beneficiary and payer'")
                        beneficiary_and_payer = await get_parent(element, 2)
                        if beneficiary_and_payer:
                            await beneficiary_and_payer.click()
                            await page.wait_for_timeout(500)
                            next_sibling_handle = await beneficiary_and_payer.evaluate_handle("el => el.nextElementSibling")

                            if next_sibling_handle:
                                sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                ad_info['beneficiary_and_payer'] = sibling_text.strip()
                                print("Beneficiary and payer:", ad_info['beneficiary_and_payer'])

                        # Extracting European Union transparency
                        element = await modal_element.query_selector("text='European Union transparency'")
                        european_union_transparency = await get_parent(element, 2)
                        if european_union_transparency:
                            await european_union_transparency.click()
                            await page.wait_for_timeout(500)
                            next_sibling_handle = await european_union_transparency.evaluate_handle("el => el.nextElementSibling")

                            if next_sibling_handle:
                                sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                ad_info['european_union_transparency'] = sibling_text.strip()
                                print("European Union Transparency:", ad_info['european_union_transparency'])

                    ads_data.append(ad_info)  # Append ad info to the list
                    await page.click("text='Close'")  # Close the modal after scraping

            # Save the ads data to a CSV file
            df = pd.DataFrame(ads_data)
            df.to_csv('scraped_ads_data.csv', index=False)
            print("Data saved to scraped_ads_data.csv")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

# Get URL input from the user
url = input("Please enter the URL to scrape: ")

# Run the scraping function
asyncio.run(scrape_ads_library(url))
