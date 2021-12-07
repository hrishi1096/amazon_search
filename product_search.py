import sys
import os
import time
# To run from the terminal
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import NoSuchElementException

from threading import Thread


AMAZON_URL = "https://www.amazon.co.uk"
CURRENCY = "Pounds"
PRODUCT = "iphone X"
WEBDRIVER_IMPLICIT_WAIT_TIME = 10
DELAY = 5
USERNAME = os.environ['BROWSERSTACK_USERNAME']
ACCESSKEY = os.environ['BROWSERSTACK_ACCESS_KEY']


capabilities = [{
      'os_version': '11',
      'os': 'Windows',
      'browser': 'chrome',
      'browser_version': '96.0',
      'name': 'Chrome Test',
      'build': 'Amazon_product_search_build_1'
      },
      {
      'os_version': '10',
      'os': 'Windows',
      'browser': 'firefox',
      'browser_version': '94.0',
      'name': 'Firefox test',
      'build': 'Amazon_product_search_build_1'
      },
      {
      'os_version': 'Monterey',
      'os': 'OS X',
      'browser': 'safari',
      'browser_version': '15.0',
      'name': 'Safari Test',
      'build': 'Amazon_product_search_build_1'
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
    all_results = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

    for result in all_results:
        index += 1
        name = result.find_element(By.CSS_SELECTOR, 'span.a-size-medium.a-color-base.a-text-normal')
        name = name.text

        try:
            price = result.find_element(By.CSS_SELECTOR, 'span.a-price-whole')
            price = price.text
        except NoSuchElementException:
            price = "Currently not available"

        link = result.find_element(By.CSS_SELECTOR, 'a.a-link-normal.a-text-normal')
        link = link.get_attribute('href')

        print(
              "\n--------{}--------"
              "\nProduct name: {}"
              "\nPrice(in {}): {}"
              "\nLink to product details:\n{}".format(index, name, CURRENCY, price, link)
              )


def get_element(driver, css_selector):
	try:
	    elem = WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
	    return elem
	except TimeoutException:
	    print("{}: Loading is taking too long!\n".format(css_selector))
	except NoSuchFrameException:
		print("{}: NoSuchFrameException\n".format(css_selector))
	except NoSuchElementException:
		print("{}: NoSuchElementException\n".format(css_selector))

	return None


def accept_cookies(driver, css_selector):
    try:
        cookie_accept = WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        cookie_accept.click()
    except NoSuchElementException:
        return


def amazon_search(driver, product):
    cookie_accept_css = "input[name='accept']"
    searchbox_css     = "input[id='twotabsearchtextbox']"
    submit_btn_css    = "input[id='nav-search-submit-button']"
    ios_filter_css    = "li[aria-label='iOS']"
    sort_dropdown_css = 'span[data-action="a-dropdown-button"]'
    high_to_low_css   = '#s-result-sort-select_2'

    # Go to desired url
    driver.get(AMAZON_URL)

    # To handle the cookies banner
    accept_cookies(driver, cookie_accept_css)

    # Search the product
    searchbox = get_element(driver, searchbox_css)
    if searchbox is None:
    	return 0
    searchbox.clear()
    searchbox.send_keys(product)

    # Click submit
    submit_btn = get_element(driver, submit_btn_css)
    if searchbox is None:
    	return 0
    submit_btn.click()

    # This is only for the sake of Safari
    time.sleep(3)

    # Apply operating system filter: iOS
    ios_filter = get_element(driver, ios_filter_css)
    if searchbox is None:
    	return 0
    ios_filter.click()

    # Sort the search results from High to Low price
    sort_dropdown = get_element(driver, sort_dropdown_css)
    if searchbox is None:
    	return 0
    sort_dropdown.click()

    high_to_low = get_element(driver, high_to_low_css)
    if searchbox is None:
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


