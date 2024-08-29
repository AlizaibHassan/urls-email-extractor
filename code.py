import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import csv
from concurrent.futures import ThreadPoolExecutor

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"URL returned status code {response.status_code}: {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to establish connection to {url}: {e}")
        return None

def extract_emails(page_content):
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    return email_pattern.findall(page_content)

def crawl_page(url, results, url_number):
    page_content = fetch_page(url)
    if page_content:
        emails = extract_emails(page_content)
        domain = urlparse(url).netloc
        if emails:
            print(f"URL {url_number}: Emails found in {url}: {emails}")
            results[domain] = emails

def save_to_csv(data, filename="emails.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Domain", "Email"])
        for domain, emails in data.items():
            for email in emails:
                writer.writerow([domain, email])

def main():
    input_file = "input.txt"
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    results = {}
    threads = min(20, len(urls))  # You can adjust the number of threads as needed

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(crawl_page, url, results, i+1) for i, url in enumerate(urls)]
        for future in futures:
            future.result()

    print("All emails found:")
    for domain, emails in results.items():
        print(f"{domain}: {emails}")

    save_to_csv(results)
    print("Emails have been saved to emails.csv")

if __name__ == "__main__":
    main()
