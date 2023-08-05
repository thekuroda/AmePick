import requests
from bs4 import BeautifulSoup
import csv
from google.cloud import secretmanager
import os
import json
from google.oauth2.credentials import Credentials
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials


env_value = os.environ.get('GOOGLE_CREDENTIALS')
print(f"GOOGLE_CREDENTIALS value: {env_value}")
google_credentials = json.loads(env_value)


# Get the credentials from the environment variable and convert to a dictionary
google_credentials = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))

# Use the google_credentials dictionary wherever you were using the .json file

# Set up the Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(os.environ.get('GOOGLE_CREDENTIALS'))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open the Google Sheet using its name
sheet = client.open("Ame-Daily Diet").sheet1

# Append data
row = ["URL", "Title", "User"]  # Replace with your data
sheet.append_row(row)
creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')

creds_dict = json.loads(creds_json)
creds = Credentials.from_authorized_user_info(creds_dict)


def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """
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

    # Open the Google Sheet using its name
    sheet = client.open("Ame-Daily Diet").sheet1

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
