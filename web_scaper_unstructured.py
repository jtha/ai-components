from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import threading
import time

# root url of the website to be scraped
url = "https://python.langchain.com/en/latest/"
# set number of threads to use
num_threads = 4
# time to sleep between each request
sleep_time = 2


# function to check if a link is valid
def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# function to get all links from a webpage
def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("#"):
            href = urljoin(url, href)
            links.append(href)

    return links


def save_page(url):
    response = requests.get(url)
    filename = url.split('//')[-1].replace('/', '') #+ '.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    time.sleep(sleep_time)


def worker(chunks):
    for chunks in chunks:
        if is_valid_url(chunks):
            save_page(chunks)
            print(chunks)


# get all links from the webpage
links = get_links(url)
unique_links = []
for element in links:
    if element not in unique_links:
        unique_links.append(element)

print("Total links:" + str(len(links)))
print("Unique links:" + str(len(unique_links)))

# Split the URLs into 4 equal parts
for l in unique_links:
    chunk_size = len(unique_links) // num_threads
    chunks = [unique_links[i:i+chunk_size] for i in range(0, chunk_size * num_threads, chunk_size)]

# Create a list of threads
for l in chunks:
    threads = []

# Create and start 4 threads, one for each chunk
for i in range(num_threads):
    t = threading.Thread(target=worker, args=(chunks[i],))
    threads.append(t)
    t.start()

# Wait for all threads to finish
for t in threads:
    t.join()

print("All workers have completed")
