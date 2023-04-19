import os
import time
import json
import random
import gzip
from pyquery import PyQuery
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Define a function to retrieve specific data requests based on type
def get_data_requests(username, data_type):
    # If the data type is user data, retrieve the request and extract the data
    if data_type == "user_data":
        user_data_request = [request for request in driver.requests
                             if request.method == 'GET' and request.url == f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'][0]
        data_str = gzip.decompress(user_data_request.response.body)
        data = json.loads(data_str)
        user_data = data['data']['user']
        return user_data
    # If the data type is post data, retrieve the request and extract the data
    if data_type == "posts_data":
        posts_data_request = [request for request in driver.requests
                              if request.method == 'GET' and
                              f'https://www.instagram.com/api/v1/feed/user' in request.url]
        # Retrieve the post data from each request and return as a list
        posts_data = [json.loads(gzip.decompress(request.response.body)) for request in posts_data_request]
        return sum([post_data['items'] for post_data in posts_data], [])

# Set the target username
username = 'teletrece'

# Create directories to store the scraped data
os.makedirs(f'data/{username}/posts', exist_ok=True)
os.makedirs(f'data/{username}/comments', exist_ok=True)

# Set up the Selenium web driver and navigate to Instagram
svc = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=svc)
driver.maximize_window()
driver.get('https://www.instagram.com')

#########################################################################
# Ejecutar hasta aqui y logear

# Navigate to the target username's Instagram page
driver.get(f'https://www.instagram.com/{username}')

#########################################################################
# Esperar a que cargue la pagina

# Retrieve the user data and the number of posts
user_data = get_data_requests(username, 'user_data')
num_posts = user_data['edge_owner_to_timeline_media']['count']

# Save the user data to disk
with open(f"data/{username}/user_data.json", 'w') as f:
    json.dump(user_data, f)

# Initialize variables for the loop
page_index = 0
previous_post_codes = ['']
codes = set()
scroll_attempts = 0
max_scroll_attempts = 10

# Record the start time
start_time = time.time()

# Start a loop to scrape the posts
while True:
    # Get the page source and parse it with PyQuery
    page_source = driver.page_source
    parsed_page = PyQuery(page_source)

    # Get the codes of the posts on the current page
    current_post_codes = [PyQuery(node).attr('href').split('/')[2] for node in parsed_page('div._aabd > a.x1i10hfl')]

    # If the last code on the current page is the same as the last code on the previous page, we've reached the end of the posts
    if current_post_codes[-1] == previous_post_codes[-1]:
        scroll_attempts += 1
        print('Scroll attempts:', scroll_attempts)
        # If we've reached the maximum number of scroll attempts, break out of the loop
        if scroll_attempts >= max_scroll_attempts:
            print('Too many attempts')
            break
    else:
        scroll_attempts = 0

    # Retrieve the post data for the current page
    posts_data = get_data_requests(username, 'posts_data')
    posts_data = [item for item in posts_data if item['code'] not in codes]
    codes = codes.union([item['code'] for item in posts_data])

    # Write the page source and codes to disk
    with open(f"data/{username}/posts/data_{str(page_index).zfill(4)}.json", 'w', encoding="utf-8") as f:
        json.dump(posts_data, f)
    with open(f"data/{username}/codes.txt", "a", encoding="utf-8") as f:
        for code in current_post_codes:
            f.write(code + "\n")

    # Update the previous post codes variable and scroll down to load more posts
    previous_post_codes = current_post_codes.copy()

    # Delete requests
    del driver.requests
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Add a random sleep to avoid bot detection
    time.sleep(random.uniform(2, 3))

    # Print the current page index and the time elapsed since the loop started
    page_index += 1

    # Iterate over the posts and stop when a post before October 1, 2018 is found
    if sum([item['taken_at'] < 1538352000 for item in posts_data]) > 0:
        break

    print(f"Scraped {page_index} pages in {time.time() - start_time:.2f} seconds")
