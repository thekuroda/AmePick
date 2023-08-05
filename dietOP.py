import gspread
import sys
import requests
from bs4 import BeautifulSoup
import os
import json
from google.oauth2.service_account import Credentials

# Load the credentials from the environment variable
creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
creds_dict = json.loads(creds_json)

# Use the service account credentials directly
creds = Credentials.from_service_account_info(creds_dict)

# Create a client to interact with Google Sheets
client = gspread.authorize(creds)

# Open the Google Sheet using its name
sheet = client.open("Ame-Daily Diet").sheet1


def access_secret_version(project_id, secret_id, version_id):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient(credentials=creds)

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')


# Setup ScrapingBee
api_key = access_secret_version("heroic-bird-298712", "scrapingbee", "latest")
url = 'https://blogger.ameba.jp/genres/diet/topics'

try:
    response = requests.get(
        'https://app.scrapingbee.com/api/v1/',
        params={
            'api_key': api_key,
            'url': url,
            'wait': 10,
        }
    )

    # Check if the response from the ScrapingBee API was successful
    if response.status_code != 200:
        raise ValueError(
            f"ScrapingBee request failed with status code {response.status_code}: {response.text}")

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the job posts
    job_posts = soup.find_all('li', class_='p-topics__item')

    # Write the header to the Google Sheet (only if it's a fresh sheet)
    if not sheet.row_values(1):
        sheet.append_row(["URL", "Title", "User"])

    # Write the information of each job post to Google Sheet
    for job_post in job_posts:
        url = job_post.find('a', class_='p-topics__anchor u-clearfix')['href']
        title = job_post.find('p', class_='p-topics__title').text
        user = job_post.find('span', class_='p-topics__userName').text
        sheet.append_row([url, title, user])

except requests.RequestException as e:
    print(f"Network error: {e}")
    sys.exit(1)
except IOError as e:
    print(f"File error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
