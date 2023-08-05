import requests
from bs4 import BeautifulSoup
import csv
from google.cloud import secretmanager

def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')


# Setup ScrapingBee
api_key = access_secret_version("heroic-bird-298712", "scrapingbee", "latest")
url = 'https://blogger.ameba.jp/genres/diet/topics'

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
with open('diet.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["URL", "Title", "User"])

    # Write the information of each job post
    for job_post in job_posts:
        url = job_post.find('a', class_='p-topics__anchor u-clearfix')['href']
        title = job_post.find('p', class_='p-topics__title').text
        user = job_post.find('span', class_='p-topics__userName').text
        writer.writerow([url, title, user])
