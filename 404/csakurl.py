import json
import re
import requests

# Define the regex pattern for URLs
pattern = r'https:\/\/yanac\.hu\S*\/'

# Specify the path to your JSON file
file_path = 'wp_posts2.json'

# Open and read the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)  # Assuming JSON is a list of dictionaries

# Iterate through JSON records
for item in data:
	text = item.get('post_content', '')  # Get 'post_content' safely
	title = item.get('post_title', '')

	# Find all URLs that match the regex
	matches = re.findall(pattern, text)

	for match in matches:
		url = match  # Remove trailing slash if needed

		try:
			response = requests.get(url, timeout=5)  # Set timeout to prevent hanging

			# Print only if the status code is 404
			if response.status_code == 404:
				print("Poszt cime: ",title)
				print(f"URL: {url} | Status Code: {response.status_code}")

		except requests.exceptions.RequestException as e:
			print(f"Error fetching URL {url}: {e}")
