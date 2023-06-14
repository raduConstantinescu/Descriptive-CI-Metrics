import json

class TopicListGenerator:
    def __init__(self, topic_data_file, mined_projects_file):
        self.topic_data_file = topic_data_file
        self.mined_projects_file = mined_projects_file
        self.github_topics = {}
        self.aliases = {}
        self.mined_projects = {}
        self.ci_topics = {}
        self.sorted_ci_topics = []
        self.topic_list = []

        # These are topic labels that are filtered out so that they're not used in the ChatGPT prompts
        # Reasoning: 
        # - language labels can be determined in other ways - e.g. by querying the languages used in the repository
        # - framework labels can be determined in other ways - e.g. by retrieving dependencies from project files etc.
        # - adhoc labels seem unrelated to a useful context for CI analysis, however they can be adjusted
        self.language_topic_labels = [
            'python', 'javascript', 'c-plus-plus', 'java', 'php', 'csharp', 'c', 'cpp',
            'ruby', 'lua', 'golang', 'go', 'python3', 'rust', 'kotlin', 'swift', 'css',
            'typescript', 'c-sharp', 'dart', 'html', 'elixir', 'rust-lang', 'cpp11', 'tailwindcss', 'http'
        ]
        self.framework_topic_labels = [
            'nodejs', 'pytorch', 'react-native', 'laravel', 'vue', 'flutter', 'django',
            'react', 'reactjs', 'unity', 'vuejs', 'nextjs', 'redux', 'dotnet', 'node',
            'rails', 'spring-boot', 'angular', 'discordjs', 'discord-js', 'express', 'bootstrap',
            'tailwind', 'jekyll'
        ]
        self.adhoc_topic_labels = [
            'hacktoberfest', 'hacktoberfest2021', 'redis', 'docker',
            'mongodb', 'spring', 'nestjs', 'postgresql', 'ethereum',
            'update', 'deprecated', 'async', 'eslint', 'github', 'matrix-org'
        ]
    
        self.load_data()
    
    def load_data(self):
        with open(self.topic_data_file) as f:
            self.github_topics = json.load(f)

        # Extract topic aliases and create a dictionary for quick lookup
        for topic in self.github_topics:
            topic_aliases = topic['aliases'].split(',')
            for alias in topic_aliases:
                self.aliases[alias.strip()] = topic

        # Load mined projects data from file
        with open(self.mined_projects_file, encoding="utf-8") as f:
            self.mined_projects = json.load(f)
    
    def process_topics(self):
        # Process topics in mined projects
        for project in self.mined_projects.keys():
            if self.mined_projects[project]['ci'] is True:
                for topic in self.mined_projects[project]['topics']:
                    actual_topic = topic
                    if topic in self.aliases.keys():
                        actual_topic = self.aliases[topic]['topic']
                    if actual_topic in self.ci_topics.keys():
                        self.ci_topics[actual_topic] += 1
                    else:
                        self.ci_topics[actual_topic] = 1

        # Sort CI topics by count in descending order
        self.sorted_ci_topics = sorted(self.ci_topics.items(), key=lambda x: x[1], reverse=True)


        #Filter out language, framework, and adhoc topics
        self.sorted_ci_topics = [
            topic for topic in self.sorted_ci_topics if topic[0] not in self.language_topic_labels and
            topic[0] not in self.framework_topic_labels and topic[0] not in self.adhoc_topic_labels
        ]

        # Filter topics with count < 5
        self.sorted_ci_topics = [topic for topic in self.sorted_ci_topics if topic[1] >= 5]

        # Create a list of topics (will be used as a query parameter for ChatGPT, to generate topics for new projects)
        self.topic_list = [k for (k, v) in self.sorted_ci_topics]
    
        return self.topic_list

    def print_topics_with_counts(self):
        # Print sorted CI topics with counts
        for topic in self.sorted_ci_topics:
            print(topic)
        print(len(self.sorted_ci_topics))
        print(self.topic_list)

topic_list_generator = TopicListGenerator('topic_data.json', 'ttt.json')
topic_list = topic_list_generator.process_topics()
#topic_list_generator.print_topics_with_counts()