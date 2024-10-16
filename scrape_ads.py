import asyncio
from playwright.async_api import async_playwright, ElementHandle
import pandas as pd  # Ensure pandas is installed

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

            await page.screenshot(path="screenshot.png", full_page=True)

            all_ad_blocks = await page.query_selector_all("text='Platforms'")
            ads_data = []

            for a_block in all_ad_blocks:
                ad_info = {}
                ad_block = await get_parent(a_block, 6)
                if ad_block:
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

                            basic_info_parent = await get_parent(library_id_element, 1)
                            basic_info = {}

                            if basic_info_parent:
                                next_sibling_handle = await basic_info_parent.evaluate_handle("el => el.nextElementSibling")

                                if next_sibling_handle:
                                    sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                    basic_info['Size'] = sibling_text.strip()

                                prev_sibling_handle = await basic_info_parent.evaluate_handle("el => el.previousElementSibling")

                                if prev_sibling_handle:
                                    sibling_text = await prev_sibling_handle.evaluate("el => el.innerText")
                                    basic_info['Started'] = sibling_text.strip()

                                    prev_sibling_handle = await prev_sibling_handle.evaluate_handle("el => el.previousElementSibling")

                                    if prev_sibling_handle:
                                        sibling_text = await prev_sibling_handle.evaluate("el => el.innerText")
                                        basic_info['Library'] = sibling_text.strip()

                            sponsored_element = await modal_element.query_selector("text='Sponsored'")
                            caption_element = await get_parent(sponsored_element, 9)

                            if caption_element:
                                next_sibling_handle = await caption_element.evaluate_handle("el => el.nextElementSibling")

                                if next_sibling_handle:
                                    sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                    basic_info['Short Summary'] = sibling_text.strip()

                            ad_info['Basic info'] = basic_info
                            print("Basic info:", ad_info['Basic info'])
                            
                            # Extracting about the advertiser
                            element = await modal_element.query_selector("text='About the advertiser'")
                            about_advertiser = await get_parent(element, 2)
                            about_advertiser_info = {}

                            if about_advertiser:
                                await about_advertiser.click()
                                await page.wait_for_timeout(500)

                                more_info_element = await modal_element.query_selector("text='More info'")

                                if more_info_element:
                                    next_sibling_handle = await more_info_element.evaluate_handle("el => el.nextElementSibling")

                                    if next_sibling_handle:
                                        sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                        about_advertiser_info['More info'] = sibling_text.strip()

                                about_advertiser_block = await get_parent(about_advertiser, 1)
                                social_element = await about_advertiser_block.query_selector("text='Captions: For Talking Videos'")
                                social_element_parent = await get_parent(social_element, 5)

                                if social_element_parent:
                                    caption_text = await social_element_parent.inner_text()
                                    about_advertiser_info['Caption info'] = caption_text.strip()

                                    next_sibling_handle = await social_element_parent.evaluate_handle("el => el.nextElementSibling")

                                    if next_sibling_handle:
                                        sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                        about_advertiser_info['facebook'] = sibling_text.strip()

                                        next_sibling_handle = await next_sibling_handle.evaluate_handle("el => el.nextElementSibling")

                                        if next_sibling_handle:
                                            sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                            about_advertiser_info['instagram'] = sibling_text.strip()

                            ad_info['About the advertiser'] = about_advertiser_info
                            print("About the advertiser:", ad_info['About the advertiser'])
                            
                            # Extracting beneficiary and payer
                            element = await modal_element.query_selector("text='Beneficiary and payer'")
                            beneficiary_and_payer = await get_parent(element, 2)
                            beneficiary_and_payer_info = {}
                            
                            if beneficiary_and_payer:
                                await beneficiary_and_payer.click()
                                await page.wait_for_timeout(500)

                                next_sibling_handle = await beneficiary_and_payer.evaluate_handle("el => el.nextElementSibling")

                                if next_sibling_handle:
                                    sibling_text = await next_sibling_handle.evaluate("el => el.innerText")
                                    beneficiary_and_payer_info['Description'] = sibling_text.strip()

                            ad_info['Beneficiary and payer'] = beneficiary_and_payer_info
                            print("Beneficiary and payer:", ad_info['Beneficiary and payer'])

                            # Extracting European Union transparency
                            element = await modal_element.query_selector("text='European Union transparency'")
                            european_union_transparency = await get_parent(element, 2)
                            european_union_transparency_info = {}

                            if european_union_transparency:
                                await european_union_transparency.click()
                                await page.wait_for_timeout(500)

                                eu_ad_audience = await modal_element.query_selector("text='EU ad audience'")
                                eu_ad_audience_info = {}

                                prev_sibling_handle = await eu_ad_audience.evaluate_handle("el => el.previousElementSibling")

                                if prev_sibling_handle:
                                    prev_sibling_handle = await prev_sibling_handle.evaluate_handle("el => el.previousElementSibling")
                                    if prev_sibling_handle:
                                        sibling_text = await prev_sibling_handle.evaluate("el => el.innerText")
                                        european_union_transparency_info['Description'] = sibling_text.strip()                                     

                                next_sibling_handle = await eu_ad_audience.evaluate_handle("el => el.nextElementSibling")
                                location_info = {}
                                age_info = {}
                                gender_info = {}

                                if next_sibling_handle:
                                    second_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[1]")

                                    if second_child_handle:
                                        info_text = await second_child_handle.evaluate("el => el.innerText")
                                        location_info['Description'] = info_text.strip()
                                    
                                    third_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[2]")

                                    if third_child_handle:
                                        info_text = await third_child_handle.evaluate("el => el.innerText")
                                        location_info['Table'] = info_text.strip()

                                    eu_ad_audience_info['Location'] = location_info

                                    next_sibling_handle = await next_sibling_handle.evaluate_handle("el => el.nextElementSibling")
                                    
                                    if next_sibling_handle:
                                        second_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[1]")

                                        if second_child_handle:
                                            info_text = await second_child_handle.evaluate("el => el.innerText")
                                            age_info['Range'] = info_text.strip()
                                        
                                        third_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[2]")

                                        if third_child_handle:
                                            info_text = await third_child_handle.evaluate("el => el.innerText")
                                            age_info['Description'] = info_text.strip()

                                        eu_ad_audience_info['Age'] = age_info

                                        next_sibling_handle = await next_sibling_handle.evaluate_handle("el => el.nextElementSibling")
                                    
                                        if next_sibling_handle:
                                            second_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[1]")

                                            if second_child_handle:
                                                info_text = await second_child_handle.evaluate("el => el.innerText")
                                                gender_info['Value'] = info_text.strip()
                                            
                                            third_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[2]")

                                            if third_child_handle:
                                                info_text = await third_child_handle.evaluate("el => el.innerText")
                                                gender_info['Description'] = info_text.strip()

                                            eu_ad_audience_info['Gender'] = gender_info

                                    european_union_transparency_info['EU ad audience'] = eu_ad_audience_info
                                eu_ad_delivery = await modal_element.query_selector("text='EU ad delivery'")
                                eu_ad_delivery_info = {}

                                next_sibling_handle = await eu_ad_delivery.evaluate_handle("el => el.nextElementSibling")
                                reach_info = {}
                                reach_table_info = {}
                                if next_sibling_handle:
                                    second_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[1]")

                                    if second_child_handle:
                                        info_text = await second_child_handle.evaluate("el => el.innerText")
                                        reach_info['Value'] = info_text.strip()
                                    
                                    third_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[2]")

                                    if third_child_handle:
                                        info_text = await third_child_handle.evaluate("el => el.innerText")
                                        reach_info['Description'] = info_text.strip()

                                    eu_ad_delivery_info['Reach'] = reach_info

                                    next_sibling_handle = await next_sibling_handle.evaluate_handle("el => el.nextElementSibling")

                                    if next_sibling_handle:
                                        second_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[1]")

                                        if second_child_handle:
                                            info_text = await second_child_handle.evaluate("el => el.innerText")
                                            reach_table_info['Description'] = info_text.strip()
                                        
                                        third_child_handle = await next_sibling_handle.evaluate_handle("el => el.children[2]")

                                        if third_child_handle:
                                            info_text = await third_child_handle.evaluate("el => el.innerText")
                                            reach_table_info['Table'] = info_text.strip()

                                        eu_ad_delivery_info['Reach by location, age and gender'] = reach_table_info

                                    european_union_transparency_info['EU ad delivery'] = eu_ad_delivery_info

                            ad_info['European Union transparency'] = european_union_transparency_info
                            print("European Union transparency", ad_info['European Union transparency'])
                                
                        ads_data.append(ad_info)  # Append ad info to the list
                        await page.click("text='Close'")  # Close the modal after scraping

            # Save the ads data to different file formats
            df = pd.DataFrame(ads_data)

            # Save as JSON
            df.to_json('scraped_ads_data.json', orient='records', lines=True)
            print("Data saved to scraped_ads_data.json")

            # Save as PSV
            df.to_csv('scraped_ads_data.psv', sep='|', index=False)
            print("Data saved to scraped_ads_data.psv")

            # Save as CSV
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
