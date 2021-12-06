import sys
import os
# To run from the terminal
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


import time


AMAZON_URL = "https://www.amazon.com"
PRODUCT = "iphone X"
WEBDRIVER_IMPLICIT_WAIT_TIME = 10


def setup():
	driver = webdriver.Firefox()
	driver.implicitly_wait(WEBDRIVER_IMPLICIT_WAIT_TIME)
	driver.maximize_window()
	return driver

def teardown(driver):
	driver.quit()


def logger():
	pass


def get_element(driver, css_selector):
	delay = 5
	try:
	    elem = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
	    return elem
	except TimeoutException:
	    print("Loading is taking too long!")
	except NoSuchFrameException:
		print("NoSuchFrameException")
	except NoSuchElementException:
		print("NoSuchElementException")

	teardown(driver)
	return None


def amazon_search(product):
	textbox_css       = '#twotabsearchtextbox'
	search_button_css = '#nav-search-submit-button'
	ios_filter_css    = '#p_n_feature_twenty_browse-bin\\/17881878011 > span > a > div > label > i'
	sort_dropdown_css = '#a-autoid-0-announce'
	high_to_low_css   = '#s-result-sort-select_2'

	# Setup driver
	driver = setup()

   	# Go to the desired url
	driver.get(AMAZON_URL)

	# Find the textbox, clear it, enter the product name
	textbox = get_element(driver, textbox_css)
	if textbox is None:
		print("Couldn't find textbox")
		return

	textbox.clear()
	textbox.send_keys(product)

	# Find and click the search button
	search_button = get_element(driver, search_button_css)
	if search_button is None:
		print("Couldn't find search_button")
		return
	search_button.click()

    # Apply operating system filter: iOS
	ios_filter = get_element(driver, ios_filter_css)
	if ios_filter is None:
		print("Couldn't find ios_filter")
		return
	ios_filter.click()

	# Sort the search results from High to Low price
	sort_dropdown = get_element(driver, sort_dropdown_css)
	if sort_dropdown is None:
		print("Couldn't find sort_dropdown")
		return

	sort_dropdown.click()

	high_to_low = get_element(driver, high_to_low_css)
	if high_to_low is None:
		print("Couldn't find high_to_low entry")
		return

	high_to_low.click()

	# TODO: call the logger here
	print("The logger needs to be called now")

	# Cleanup
	teardown(driver)


if __name__ == "__main__":
	amazon_search(PRODUCT)


