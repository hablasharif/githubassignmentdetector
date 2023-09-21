import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
import os

# Function to validate URLs
def is_valid_url(url):
    return re.match(r"https?://", url)

# Function to fetch repository names from a URL
def fetch_repository_names(url):
    repository_links = {}
    if is_valid_url(url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            repositories = soup.find_all("a", itemprop="name codeRepository")
            repository_links = {repo.get_text().lower(): repo['href'] for repo in repositories}
    return repository_links

# Streamlit app
st.title("GitHub Repository Detector")

# Input fields for URLs and keywords
urls = st.text_area("Enter GitHub URLs (one per line):")
keywords = st.text_area("Enter Keywords (one per line):")

if st.button("Search"):
    urls = [url.strip() for url in urls.split("\n") if url.strip()]
    keywords = [keyword.strip().lower() for keyword in keywords.split("\n") if keyword.strip()]

    # Initialize a dictionary to store repository links by name
    all_repository_links = {}

    # Initialize progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Fetch repository names from input URLs
    for i, url in enumerate(tqdm(urls, desc="Fetching repository names")):
        repository_links = fetch_repository_names(url)
        all_repository_links[url] = repository_links
        time.sleep(1)  # Simulate some processing time
        progress_bar.progress((i + 1) / len(urls))
        progress_text.text(f"Processed: {i + 1}/{len(urls)}")

    # Initialize a dictionary to store repository links containing keywords
    containing_keywords = {keyword: {} for keyword in keywords}

    # Loop through repository links and check for keywords
    for url, repo_links in all_repository_links.items():
        for keyword in keywords:
            for repo_name, repo_link in repo_links.items():
                if keyword in repo_name:
                    containing_keywords[keyword].setdefault(url, []).append(repo_link)

    # Create a folder to store reports
    os.makedirs("reports", exist_ok=True)

    # Display repository links containing each keyword
    for keyword, url_links in containing_keywords.items():
        if url_links:
            st.subheader(f"Repositories containing the keyword '{keyword}':")
            for url, links in url_links.items():
                st.write(f"From URL: {url}")
                for link in links:
                    full_link = f"https://github.com{link}"
                    st.markdown(f"Repository Link: [{full_link}]({full_link})")
            st.write("---")
        else:
            st.write(f"No repositories containing the keyword '{keyword}' found.")

    # Create an HTML report for each keyword
    for keyword, url_links in containing_keywords.items():
        if url_links:
            output_html = f"<html><body>"
            output_html += f"<h2>Repositories containing the keyword '{keyword}':</h2>"

            for url, links in url_links.items():
                output_html += f"<h3>From URL: {url}</h3>"
                for link in links:
                    full_link = f"https://github.com{link}"
                    output_html += f"<p>Repository Link: <a href='{full_link}' target='_blank'>{full_link}</a></p>"
                output_html += "<hr>"

            output_html += "</body></html>"

            # Save the HTML report to a file
            report_filename = os.path.join("reports", f"report_{keyword}.html")
            with open(report_filename, "w") as output_file:
                output_file.write(output_html)

            # Provide a download button for each HTML report
            st.download_button(
                f"Download '{keyword}' Report",
                report_filename,
                key=f"download_{keyword}",
                help=f"Download the HTML report for '{keyword}'",
            )
# Add a hyperlink to the external URL
st.markdown("[Visit GitHub Foolwer Account Along With Their Repositories Detector](https://githabfollwerdetectorandrepositories.streamlit.app/)")


