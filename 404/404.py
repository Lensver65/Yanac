import json
import re
import requests
from time import sleep

# Define the regex pattern for URLs
pattern = r'https://yanac\.hu[^\s"]+'

# Specify the path to your JSON file
file_path = '404-2026.json'

# Open and read the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)  # Assuming JSON is a list of dictionaries

with open("404_urls-2026.txt", 'w') as kimenet:
# Iterate through JSON records
	for item in data:
		text = item.get('post_content', '')  # Get 'post_content' safely
		title = item.get('post_title', '')

		# Find all URLs that match the regex
		matches = re.findall(pattern, text)

		for match in matches:
			url = match

			try:
				response = requests.get(url, timeout=5)  # Set timeout to prevent hanging
				sleep(5)

				# Print only if the status code is 404
				if response.status_code == 404:
					szoveg = "Cim: " + title + ", URL: " + url + "\n"
					kimenet.write(szoveg)
					# print("Poszt cime: ",title)
					# print(f"URL: {url} | Status Code: {response.status_code}")

			except requests.exceptions.RequestException as e:
				print(f"Error fetching URL {url}: {e}")
file.close()
kimenet.close()
