import openai
import os
from dotenv import load_dotenv
import json
import random
from TopicListGenerator import TopicListGenerator

class TopicGeneratorChatGPT:
    def __init__(self, initial_topic_list):
        self.topic_list = initial_topic_list
        self.messages = [
            {
                "role": "system",
                "content": f"You are a system that predicts software project topic labels based on their repository name and description. "
                           f"Here is the list of topics you have to use for predictions: {', '.join(self.topic_list)}. "
                           f"I don't want an explanation or elaboration, I just want you to reply with a prediction. "
                           f"You are not allowed to create new labels, if none of the given labels match - reply 'unknown'."
            }
        ]
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def generate_prediction(self, message):
        self.messages.append({"role": "user", "content": message})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        reply = chat.choices[0].message.content
        self.messages.append({"role": "system", "content": reply})
        return reply

# Manually created topic list
topic_list = ['machine-learning', 'data-visualization', 'game-engine', 'web-framework', 'text-editor', 'web-game']
# topic_list = ['android', 'api', 'ios', 'cli', 'discord', 'machine-learning', 'macos', 'kubernetes', 'bot', 'actions', 'security', 'linux', 'library', 'blockchain', 'windows', 'json', 'telegram', 'aws', 'testing', 'symfony', 'generator', 'discord-bot', 'video', 'graphql', 'devops', 'game', 'database', 'home-assistant', 'deep-learning', 'monitoring', 'git', 'framework', 'bash', 'scraper', 'google-cloud', 'azure', 'test', 'parser', 'ai', 'sdk', 'open-source', 'markdown', 'tensorflow', 'npm', 'cloud-native', 'shell', 'arduino', 'algorithm', 'editor', 'webpack', 'boilerplate', 'web', 'automation', 'bitcoin', 'handler', 'chatbot', 'slack', 'compiler', 'music', 'rest-api', 'mod', 'wordpress', 'audio']

# Automatically generated topic list
# topic_list_generator = TopicListGenerator('topic_data.json', 'ttt.json')
# topic_list = topic_list_generator.process_topics()

chat_gpt = TopicGeneratorChatGPT(topic_list)

# while True:
#     user_input = input("User: ")
#     if user_input:
#         reply = chat_gpt.generate_prediction(user_input)
#         print(f"ChatGPT: {reply}")
#         # check if within topic_list
#         chatgpt_topics = reply.split(',')
#         for topic in chatgpt_topics:
#             if topic.strip() not in topic_list:
#                 print(f"  Not in topic list: {topic.strip()}")
#             else:
#                 print(f"  In topic list: {topic.strip()}")

with open('readmes1.json', 'r') as f:
    data = json.load(f)

shuffled_keys = list(data.keys())
random.shuffle(shuffled_keys)

for key in shuffled_keys:
    user_input = 'Repository name: ' + key + ', description: ' + data[key]['description']
    try:
        reply = chat_gpt.generate_prediction(user_input)
        print(f"Repository: {key}, ChatGPT: {reply}")
    except Exception as e:
        print(key)
        print(e)
