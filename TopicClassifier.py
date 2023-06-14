import json

class TopicClassifier:
    def __init__(self, topic_data_file, mined_projects_file):
        self.topic_data_file = topic_data_file
        self.mined_projects_file = mined_projects_file
        self.github_topics = {}
        self.aliases = {}
        self.mined_projects = {}
        self.ci_projects_by_topic = {}

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

    def group_projects_by_topic(self):
        # Group CI projects by topic labels
        for project in self.mined_projects.keys():
            for topic in self.mined_projects[project]['topics']:
                actual_topic = topic
                if topic in self.aliases.keys():
                    actual_topic = self.aliases[topic]['topic']
                if actual_topic in self.ci_projects_by_topic.keys():
                    self.ci_projects_by_topic[actual_topic].append(project)
                else:
                    self.ci_projects_by_topic[actual_topic] = [project]

        return self.ci_projects_by_topic


    def print_projects_by_topic(self):
        # Print list of project names for each topic
        for topic in self.ci_projects_by_topic.keys():
            print(f"Topic: {topic}. Projects: {self.ci_projects_by_topic[topic]}")
    
    def print_clusters_to_csv(self):
        # Print list of project names for each topic in format: topic, [project1, project2, ...]
        # Start with header

        with open('clusters.csv', 'w') as f:
            f.write('topic,projects\n')
            for topic in self.ci_projects_by_topic.keys():
                f.write(f"{topic},{self.ci_projects_by_topic[topic]}")
                f.write('\n')


# Usage
classifier = TopicClassifier('topic_data.json', 'ttt.json')
ci_projects_by_topic = classifier.group_projects_by_topic()
# classifier.print_projects_by_topic()
# classifier.print_clusters_to_csv()



