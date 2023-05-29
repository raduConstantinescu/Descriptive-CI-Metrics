import os

from dotenv import load_dotenv

from repository_extractor import RepositoryExtractor, ClusterProperties


def setup():
    """Sets up external dependencies for the tool. For now, this is just environment loading."""
    load_dotenv()


def main(access_token, cluster_type):
    RepositoryExtractor(access_token, cluster_type).extract_repos()
    # # Create instances of the classes
    # extractor = RepositoryExtractor()
    # filter = RepositoryFilter()
    #
    # # Call methods in the appropriate order
    # extracted_data = extractor.extract()
    # filtered_data = filter.filter(extracted_data)
    #
    # # Further processing or outputting the collected data


if __name__ == "__main__":
    setup()
    ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN")
    CLUSTER_TYPE = ClusterProperties.MIDDLE
    main(ACCESS_TOKEN, CLUSTER_TYPE)


