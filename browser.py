import os
import psutil
import signal
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def cleanup(browser, cls):
	if browser:
		try:
			browser.close()
			browser.quit()
		except Exception as e:
			cls.get_logger().error(f"Caught exception while attempting to close the browser {repr(e)}") if cls else None
			browser.quit()
			raise Exception(f"Caught exception while attempting to close the browser: {repr(e)}")
		finally:
			try:
				if browser and hasattr(browser, "service") and hasattr(browser.service, "process") \
					and hasattr(browser.service.process, "pid") and browser.service.process.pid:
					driver_process = psutil.Process(browser.service.process.pid)
					children = driver_process.children()
					if children:
						chrome_process = children[0]
						chrome_process.terminate()
					elif driver_process:
						driver_process.terminate()
					cls.get_logger().info(f"Killing chromedriver pid {driver_process.pid}") if cls else None
					os.kill(driver_process.pid, signal.SIGTERM)
			except Exception as e:
				cls.get_logger().error(f"Attempted to hard-kill the ChromeDriver, but something went wrong: {repr(e)}")
	else:
		cls.get_logger().info("No browser initialised; nothing to clean up.")

def get_browser(headless=True):
	options = webdriver.ChromeOptions()
	options.add_experimental_option("excludeSwitches", ['enable-automation'])
	#if headless:
	#	options.add_argument('headless')
	options.add_argument('--no-sandbox')
	if headless: 
		options.headless = True
	browser = webdriver.Chrome(options=options)
	browser.set_window_size(1200, 800)
	
	return browser

# Here, the assumption is that with a max_scroll_count of 1000, we will definitely see a new section if one exists.
# This appears to be the case provided we specify what the browser window size is prior to initialising it.
def page_down(browser, body, max_scroll_count=30):
	scroll_count = 0
	html = browser.page_source
	while max_scroll_count > scroll_count:
		scroll_count += 1
		body.send_keys(Keys.PAGE_DOWN)
		body.send_keys(Keys.PAGE_DOWN)
		time.sleep(30)
		if not scroll_count % 5:
			print(html == browser.page_source)
			html = browser.page_source
