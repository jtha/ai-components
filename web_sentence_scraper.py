# TODO: Add a progress bar to show the progress of the scraping process.
# TODO: Add a function to further clean the text, replacing special characters with their English equivalents.
# TODO: Make the script more robust by adding error handling.
# TODO: Add a function to extract the title of the webpage.
# TODO: Make the script more efficient by using multithreading.
# TODO: Make the whole script into a function that can be called from another script, which sets the parameters 'url', 'sleep_time', and 'text_container'.
# TODO: Add a function to automatically detect the content container.

import csv
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

# root url of the website to be scraped
url = "https://python.langchain.com/en/latest/"
# css selector of the main content container to be scraped
text_container = "#main-content > div.bd-content > div.bd-article-container"
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


# function to extract text and headers from a webpage
def extract_text_and_headers(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    main_content = soup.select_one(text_container)

    if main_content:
        headers = main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        paragraphs = main_content.find_all("p")
        text = " ".join([p.text for p in paragraphs])
    else:
        headers, text = [], ""

    return text, headers


# function to find the nearest header to a sentence
def nearest_header(headers, index):
    if not headers:
        return ""

    nearest = None
    distance = None

    for header in headers:
        header_index = header.parent.index(header)
        current_distance = abs(header_index - index)

        if distance is None or current_distance < distance:
            distance = current_distance
            nearest = header

    return nearest.text.strip()


# function to clean text
def clean_text(text):
    cleaned_text = " ".join(text.split())
    return cleaned_text


# function to extract sentences from a webpage
def extract_sentences(link, text, headers):
    sentences = sent_tokenize(text)
    header_sentences = [(link, nearest_header(headers, i), sentence) for i, sentence in enumerate(sentences)]
    return header_sentences


# get all links from the webpage
links = get_links(url)

# set up a list to store all sentences
all_sentences = []

# loop through all links and extract sentences
for link in links:
    if is_valid_url(link):
        text, headers = extract_text_and_headers(link)
        cleaned_text = clean_text(text)
        sentences = extract_sentences(link, cleaned_text, headers)
        all_sentences.extend(sentences)
        time.sleep(sleep_time)
        print(link)

# export all_sentences to a CSV file
with open("../output.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Link", "Nearest Header", "Sentence"])
    for row in all_sentences:
        csv_writer.writerow(row)

print("CSV file has been created.")
