import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


def load_more_comments(driver):
    """Click on the button to load more comments and wait for new comments to appear."""
    load_more_button = driver.find_element(
        By.CSS_SELECTOR,
        "button._abl- svg[aria-label='Cargar más comentarios']"
    ).find_element(By.XPATH, '..')
    load_more_button.click()
    time.sleep(3 + random.random())  # Wait for the new comments to appear


# Load the dataframe with posts
df = pd.read_csv('data/posts_df/posts_biobiochile.csv')

# Initialize the webdriver and navigate to Instagram
driver = webdriver.Chrome()
driver.get('https://www.instagram.com')

# Iterate through the posts in the dataframe
for i in range(14, len(df)):  # Skip the first 4 posts
    print(f"Loading post number: {i}")
    post_id = df['code'][i]
    post_url = f"https://www.instagram.com/p/{post_id}/"

    # Navigate to the post URL
    driver.get(post_url)
    time.sleep(3 + random.random())

    # Load more comments
    c = 0
    while True:
        print(f"Loading more comments: {c}")
        try:
            load_more_comments(driver)
            c += 1
        except:
            print('No more comments')
            break

    # Load replies to comments
    r = 0
    while True:
        see_more_buttons = driver.find_elements(By.CSS_SELECTOR, "button > span")
        see_more_buttons = [button for button in see_more_buttons if button.text.startswith("Ver respuestas (")]
        if len(see_more_buttons) == 0:
            print("No more replies")
            break
        for i, button in enumerate(see_more_buttons):
            button.click()
            print(f"Loading more replies: {r}")
            r += 1
            time.sleep(3 + random.random())  # Wait for the new replies to appear

    # Save the page source to a file
    page_source = driver.page_source
    with open(f"data/page_sources/{post_id}.html", "w", encoding="utf-8") as f:
        f.write(page_source)
