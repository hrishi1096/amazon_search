import sys
import os
# To run from the terminal
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup
from threading import Thread



AMAZON_URL = "https://www.amazon.com"
PRODUCT = "iphone X"
WEBDRIVER_IMPLICIT_WAIT_TIME = 10
USERNAME = os.environ['BROWSERSTACK_USERNAME']
ACCESSKEY = os.environ['BROWSERSTACK_ACCESS_KEY']


capabilities = [{
      'os_version': '11',
      'os': 'Windows',
      'browser': 'chrome',
      'browser_version': '96.0',
      'name': 'Chrome Test',
      'build': 'Amazon_product_search_build'
      },
      {
      'os_version': '10',
      'os': 'Windows',
      'browser': 'firefox',
      'browser_version': '94.0',
      'name': 'Firefox test',
      'build': 'Amazon_product_search_build'
      },
      {
      'os_version': 'Monterey',
      'os': 'OS X',
      'browser': 'safari',
      'browser_version': '15.0',
      'name': 'Safari',
      'build': 'Amazon_product_search_build'
}]



def setup(desired_cap):
	driver = webdriver.Remote(
		command_executor='https://' + USERNAME + ':' + ACCESSKEY + '@hub-cloud.browserstack.com/wd/hub',
		desired_capabilities=desired_cap)
	driver.implicitly_wait(WEBDRIVER_IMPLICIT_WAIT_TIME)
	driver.maximize_window()
	return driver


def teardown(driver):
	driver.quit()


def logger(driver):
	index = 0
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	all_results = soup.find_all('div', {'data-component-type': 's-search-result'})

	for result in all_results:
		index += 1
		atag = result.h2.a
		name = atag.text.strip()
		link = AMAZON_URL + atag.get('href')
		price = result.find('span', 'a-price')
		price_text = "Not available"
		if price is not None:
			price_text = price.find('span', 'a-offscreen').text

		print(
			  "\n--------{}--------"
			  "\nProduct name: {}"
			  "\nPrice: {} "
			  "\nLink to product details:\n{}".format(index, name, price_text, link)
			  )


def get_element(driver, css_selector):
	delay = 10
	try:
	    elem = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
	    return elem
	except TimeoutException:
	    print("{}: Loading is taking too long!\n".format(css_selector))
	except NoSuchFrameException:
		print("{}: NoSuchFrameException\n".format(css_selector))
	except NoSuchElementException:
		print("{}: NoSuchElementException\n".format(css_selector))

	return None


def get_search_result_url(search_str):
	template = AMAZON_URL + "/s?k={}&ref=nb_sb_noss_2"
	search_str = search_str.replace(' ', '+')
	return template.format(search_str)


def amazon_search(driver, product):
	ios_filter_css    = '#p_n_feature_twenty_browse-bin\\/17881878011 > span > a > div > label > i'
	sort_dropdown_css = '#a-autoid-0-announce'
	high_to_low_css   = '#s-result-sort-select_2'

	search_result_url = get_search_result_url(product)

   	# Go directly to the search results page
	driver.get(search_result_url)

	# Apply operating system filter: iOS
	ios_filter = get_element(driver, ios_filter_css)
	if (ios_filter is None):
		return 0
	ios_filter.click()

	# Sort the search results from High to Low price
	sort_dropdown = get_element(driver, sort_dropdown_css)
	if (sort_dropdown is None):
		return 0
	sort_dropdown.click()

	high_to_low = get_element(driver, high_to_low_css)
	if (high_to_low is None):
		return 0
	high_to_low.click()

	logger(driver)

	return 1


def run_product_search(desired_cap):
	# Setup
	driver = setup(desired_cap)

	if (amazon_search(driver, PRODUCT)):
		driver.execute_script(
			'browserstack_executor: {"action": "setSessionStatus", "arguments": \
			{"status":"passed", "reason": "Amazon product search successful!"}}')
	else:
		driver.execute_script(
			'browserstack_executor: {"action": "setSessionStatus", "arguments": \
			{"status":"failed", "reason": "Amazon product search unsuccessful"}}')

	# Cleanup
	teardown(driver)


if __name__ == "__main__":
    for cap in capabilities:
        Thread(target=run_product_search, args=(cap,)).start()


