import requests
import os
import datetime
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GITHUB_ACCESS_TOKEN')

headers = {"Authorization": f"token {token}"}

response = requests.get('https://api.github.com/rate_limit', headers=headers)

if response.status_code == 200:
    rate_limit_info = response.headers

    limit = rate_limit_info['X-RateLimit-Limit']
    remaining = rate_limit_info['X-RateLimit-Remaining']
    reset_time = int(rate_limit_info['X-RateLimit-Reset'])  # Ensure it's an integer
    reset_time = datetime.datetime.fromtimestamp(reset_time)

    print(f"Limit: {limit}")
    print(f"Remaining: {remaining}")
    print(f"Reset Time: {reset_time}")
else:
    print(f"Failed to get rate limit info. HTTP status code: {response.status_code}")
