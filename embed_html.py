import os
import time
import pandas as pd

from unstructured.cleaners.core import replace_unicode_quotes
from unstructured.partition.auto import partition
from unstructured.cleaners.core import clean_non_ascii_chars
from unstructured.cleaners.core import clean_extra_whitespace
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer

# define function to get all html files in a directory
def get_html_files(directory):
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                html_files.append(os.path.join(root, file))
    return html_files

# set directory to search for html files
directory = "C:\Projects\MainConda\AI Components\html_output"

html_files = []
output_list = []
html_files = get_html_files(directory)

# add debug line to measure how long it takes to embed text with the SentenceTransformer  model.
time_start = time.time()

# loop through all html files and extract text
for i in html_files:
    elements = partition(filename=i)
    for element in elements[:5]:
        element.apply(replace_unicode_quotes)
        element.apply(clean_non_ascii_chars)
        element.apply(clean_extra_whitespace)
        output_list.append(element)


# embed text
final_text = clean_non_ascii_chars(replace_unicode_quotes("\n\n".join([str(el) for el in output_list])))
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device='cuda')
model.max_seq_length = 512  # Set max_seq_length to 512, as the MPNet model was trained with this value
sentences = sent_tokenize(final_text)
embeddings = model.encode(sentences, show_progress_bar=True)


# save embeddings to csv
df = pd.DataFrame(embeddings)  # Convert your output to a pandas DataFrame
df.to_csv('embeddings.csv', index=False)  # Save the DataFrame to a CSV file

time_end = time.time()
print("Time taken to embed text: ", time_end - time_start)
