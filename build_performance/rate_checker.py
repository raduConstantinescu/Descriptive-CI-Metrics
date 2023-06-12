import requests
import os
import datetime
from dotenv import load_dotenv
load_dotenv()

def check_rate(token):
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


token0 = os.getenv('GITHUB_ACCESS_TOKEN0')
token1 = os.getenv('GITHUB_ACCESS_TOKEN1')
token2 = os.getenv('GITHUB_ACCESS_TOKEN2')
token3 = os.getenv('GITHUB_ACCESS_TOKEN3')


check_rate(token0)
check_rate(token1)
check_rate(token2)
check_rate(token3)



# I have multiple tokens, so I can run this script multiple times to get the rate limit info for each token.
# I can then compare the rate limit info for each token to see which one has the most remaining requests.
