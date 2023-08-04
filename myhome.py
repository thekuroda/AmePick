import requests
from bs4 import BeautifulSoup
import csv

# Setup ScrapingBee
api_key = 'IDUZ5WRYJU8NI62W8VMARD1Z3SLYAWYNHFJSWTR9M7CT1GIX052AFKEL1JRNUAQPD7JESV4XJBD4HRGJ'
url = 'https://blogger.ameba.jp/genres/my-home/topics'

response = requests.get(
    'https://app.scrapingbee.com/api/v1/',
    params={
        'api_key': api_key,
        'url': url,
    }
)

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the job posts
job_posts = soup.find_all('li', class_='p-topics__item')

# Prepare to write to a CSV file
with open('myhome.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["URL", "Title", "User"])

    # Write the information of each job post
    for job_post in job_posts:
        url = job_post.find('a', class_='p-topics__anchor u-clearfix')['href']
        title = job_post.find('p', class_='p-topics__title').text
        user = job_post.find('span', class_='p-topics__userName').text
        writer.writerow([url, title, user])
