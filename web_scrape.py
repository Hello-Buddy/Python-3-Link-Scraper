import os, argparse, sys, time
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.alert import Alert
from http.client import HTTPException, ImproperConnectionState
from bs4 import BeautifulSoup

def web_scrape(webpage):
	links = []
	for link in webpage.find_all("a"):
		url = link.get("href")
		if url:
			links.append(url)
	return links

def get_links(browser, filename, starting_page):
	visited = {}
	visited_list = [starting_page]
	counter = 0
	f = open(filename, "a")
	print("[+] Starting scraper")
	while True:
		try:
			page = BeautifulSoup(browser.page_source, "lxml")
		except (AttributeError, exceptions.UnexpectedAlertPresentException, \
			 exceptions.TimeoutException) as e:
			if e == AttributeError:
				print("[!] The webpage could not be loaded due to an unknown error")
			elif e == exceptions.UnexpectedAlertPresentException:
				print("[!] A acript stopped working on the webpage")
				alert = browser.switch_to_alert()
				alert.dismiss()
			elif e == exceptions.TimeoutException:
				print("[!] The webpage timed out while connecting")
			visited_list.pop(0)
			to_open = visited_list.pop(0)
			browser.get(to_open)
		except (ImproperConnectionState, HTTPException, ConnectionResetError, \
			exceptions.NoSuchWindowException, ConnectionRefusedError):
			print("[!] Can not send request. Browser may have closed.")
			break
		else:
			links = web_scrape(page)
			if links:
				for link in links:
					if link not in visited and "http://" in link or "https://" in link:
						if "www.facebook" not in link:
							visited_list.append(link)
							visited[link] = 1
			if visited_list:
				counter += 1
				to_open = visited_list.pop(0)
				print("[+] Opening {} : Pages opened: {:d}".format(to_open, counter))
				f.write(to_open + "\n")
				try:
					browser.get(to_open)
				except exceptions.TimeoutException:
					print("[!] The webpage has timed out while trying to conenct")
				except:
		                        print("[!] The webpage could not be opened due to an unknow error")

			else:
				print("[!] Out of links! Exiting")
				break
	f.close()

def main():
	os.system("clear")
	parser = argparse.ArgumentParser()
	parser.add_argument("webpage", help = "Enter the webpage to scrape")
	parser.add_argument("file_name", help =  "File to save the links into")
	parser.add_argument("timeout", help = "Number of seconds to wait for a webpage to load before skipping")
	args = parser.parse_args()
	
	try:
		browser = webdriver.Firefox()
	except exceptions.WebDriverException:
		print("[!] Could not open Firefox due to an error in fetching the profile")
	browser.set_page_load_timeout(int(args.timeout))
	try:
		browser.get(args.webpage)
	except exceptions.TimeoutException:
		print("[!] Unable to connect to webpage due to timeout error")
	except exceptions.UnexpectedAlertPresentException:
		print("[!] A acript stopped working on the webpage")
		alert = browser.switch_to_alert()
		alert.dismiss()
	except (ImproperConnectionState, HTTPException, ConnectionResetError):
		print("[!] Can not send request. Browser may have closed.")
	else:
		links_return = get_links(browser, args.file_name, args.webpage)
	try:
		browser.close()
	except ConnectionRefusedError:
		pass
	sys.exit()

try:
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
	print("[!] Interupted by keypress")
	sys.exit()
