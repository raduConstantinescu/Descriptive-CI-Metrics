import calendar
import time

from github import Github, RateLimitExceededException


class RepositoryExtractor():
    def __init__(self, github):
        self.g = github

    def extract(self):
        intervals = []

        lower_limit = 1
        upper_limit = 600
        num_intervals = 50

        for _ in range(num_intervals):
            intervals.append((lower_limit, upper_limit))
            lower_limit += 600
            upper_limit += 600

        print(intervals)
        for interval in intervals:
            self.search_repositories_with_stars(interval[0], interval[1], 20)

    def search_repositories_with_stars(self, lower_limit, upper_limit, num_repos):
        # Search for repositories with stars between the lower and upper limits
        query = f"is:public template:false fork:false stars:{lower_limit}..{upper_limit}"

        while True:
            try:
                result = self.g.search_repositories(query=query, sort='updated')

                # Extract repository information and save names to a text file
                with open('../outputs_v2/processed_text_files/output.txt', 'a') as file:
                    for i, repo in enumerate(result[:num_repos]):
                        repo_name = f"{repo.owner.login}/{repo.name}"
                        file.write(repo_name + '\n')

                        # Stop extracting repositories once the desired number is reached
                        if i + 1 == num_repos:
                            break
                break
            except RateLimitExceededException as e:
                print(e)
                if self.g.get_rate_limit().core.remaining > 0:
                    print("Secondary rate limit...")
                    time.sleep(60)
                else:
                    print("Rate limit exceeded. Waiting for reset...")
                    core_rate_limit = g.get_rate_limit().core

                    reset_timestamp = calendar.timegm(core_rate_limit.reset.timetuple())
                    sleep_time = reset_timestamp - calendar.timegm(
                        time.gmtime()) + 5  # add 5 seconds to be sure the rate limit has been reset
                    time.sleep(sleep_time)
                    # Retry the current search
                continue

        print(f"Repository names saved to repos.txt")



