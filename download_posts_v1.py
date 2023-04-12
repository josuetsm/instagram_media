import os
import time
import random
from selenium import webdriver
from pyquery import PyQuery

# Set the target medio
medio = 'teletrece'

# Make dirs
os.makedirs(f'data/posts/{medio}', exist_ok=True)

# Initialize the webdriver and navigate to Instagram
driver = webdriver.Chrome()
driver.get('https://www.instagram.com')

# Navigate to the target medio's Instagram page
driver.get(f'https://www.instagram.com/{medio}')

# Initialize variables
page_index = 0
previous_post_codes = ['']
scroll_attempts = 0
max_scroll_attempts = 10

# Record the start time
start_time = time.time()

# Start a loop to scrape posts
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
        if scroll_attempts >= max_scroll_attempts:
            print('Too many attempts')
            break
    else:
        scroll_attempts = 0

    # Write the page source and codes to disk
    with open(f"data/posts/{medio}/page_source_{str(page_index).zfill(4)}.html", "w", encoding="utf-8") as f:
        f.write(page_source)
    with open(f"data/posts/{medio}/codes.txt", "a", encoding="utf-8") as f:
        for code in current_post_codes:
            f.write(code + "\n")

    # Update the previous post codes variable and scroll down to load more posts
    previous_post_codes = current_post_codes.copy()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Add a random sleep to avoid bot detection
    time.sleep(random.uniform(4, 5))

    # Print the current page index and the time elapsed since the loop started
    page_index += 1
    print(f"Scraped {page_index} pages in {time.time() - start_time:.2f} seconds")

