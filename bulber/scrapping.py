import requests
from bs4 import BeautifulSoup
import chromedriver_binary
from selenium import webdriver
import csv
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

# Step 1: Extract url for each species
#      1.1 open full page and extract species info and urls

def scroll_through(page="https://identify.plantnet.org/explo/weurope/"):
    SCROLL_PAUSE_TIME = 0.5

    browser = webdriver.Chrome()
    browser.get(page)

    for n in range(5):

        # Get scroll height
        ### This is the difference. Moving this *inside* the loop
        ### means that it checks if scrollTo is still scrolling
        last_height = browser.execute_script("return document.body.scrollHeight")

        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:

            # try again (can be removed)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")

            # check if the page height has remained the same
            if new_height == last_height:
                # if so, you are done
                break
            # if not, move on to the next loop
            else:
                last_height = new_height
                continue


    # Extract all urls and associated info for each species
    rows = browser.find_elements_by_xpath("//div[@class='row']")

    plants = []

    for row in rows:
        plant = {}
        heading1 = browser.find_element_by_tag_name('h6')
        heading2 = browser.find_element_by_xpath("//h6[@class='colored ng-binding']")
        heading3 = browser.find_element_by_xpath("//em[@class='family-name ng-binding']")
        a = heading1.find_element_by_tag_name('a')
        plant['url'] = a.get_attribute('href')
        plant['species_name'] = heading1.text
        plant['common_name'] = heading2.text
        plant['family'] = heading3.text
        plants.append(plant)

    return plants


#      1.1 Open images to get HQ image link

# images = browser.find_elements_by_xpath('//a[@ng-click="openLightboxModal($index)"]')

# wait = WebDriverWait(browser, 15)

# links = []
# for image in images[:4]:
#     time.sleep(2)
#     image.click()
#     wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@class='lightbox-image-container']")))
#     lightbox = browser.find_element_by_class_name('lightbox-image-container')
#     image_link = lightbox.find_element_by_tag_name('img').get_attribute('src')
#     links.append(image_link)
#     webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
#     time.sleep(2)


# Step 2: Extract smaller format images for selected species
def extract_images(selected_species):

    for selected in selected_species:

        # open the page
        browser = webdriver.Chrome()
        browser.get(selected)

        # wait for element to appear
        wait = WebDriverWait(browser, 60)
        wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "table-condensed")))

        # find the section with the plant info
        plant_info_node = browser.find_element_by_class_name("table-condensed")
        a = plant_info_node.find_element_by_tag_name('td a')
        b = a.find_elements_by_xpath('//i[@class="ng-binding"]')

        image_angle = ['flower', 'habit', 'leaf', 'other']

        for angle in image_angle:
            # select the angel of image
            wait.until(ec.visibility_of_element_located((By.XPATH, f'//img[@ng-src="app/webimgs/tags/{angle}.png"]')))
            icone = browser.find_element_by_xpath(f'//img[@ng-src="app/webimgs/tags/{angle}.png"]')
            icone.click()
            # select the images in the gallery
            gallery = browser.find_element_by_class_name('gallery')
            small_images = gallery.find_elements_by_tag_name('img')
            image_count = 1
            # loop over images to extract all plant info and url with 'src'
            for small_image in small_images:
                plant = {}
                plant['family'] = b[0].text
                plant['genus'] = b[1].text
                plant['species'] = b[2].text
                plant['angle'] = angle
                plant['image_url'] = small_image.get_attribute('src')
                plant['image_title'] = f'{b[2].text}_{angle}_img_{image_count}'
                full_image_list_2.append(plant)
                image_count += 1
        browser.quit()
        print(page)
        page += 1

    return full_image_list_2
