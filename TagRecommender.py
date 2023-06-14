import json
from DataPreprocessor import TextPreprocessor
import os
import pickle
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

class TagRecommender:
    def __init__(self, data_file_path, abbreviations_file_path):
        self.lr_model = None
        self.tfidf_vectorizer = None
        self.preprocessor = TextPreprocessor(abbreviations_file_path)
        self.filename = data_file_path

        with open(self.filename, "r") as f:
            self.data = json.load(f)
    
    def train_tfidf(self, X_train, text_col):
        if (os.path.exists(os.path.join(os.path.dirname(__file__), 'models/tfidf.pkl'))):
            with open(os.path.join(os.path.dirname(__file__), 'models/tfidf.pkl'), 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
            return
        
        self.tfidf_vectorizer = TfidfVectorizer(
            stop_words='english',
            sublinear_tf=True,
            strip_accents='unicode',
            analyzer='word',
            token_pattern=r'\w{2,}',
            ngram_range=(1, 2),
            max_features=20000
        )

        tfidf_time = time.time()
        self.tfidf_vectorizer.fit(X_train[text_col].values.astype('U'))
        end_time = time.time()
        print("tfidf train time: " + str(end_time - tfidf_time))
        
        with open(os.path.join(os.path.dirname(__file__), 'models/tfidf.pkl'), 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)

    def load_lr_model(self, model_path):
        with open(model_path, 'rb') as f:
            self.lr_model = pickle.load(f)
    
    def predict_tags(self, predict_only_unlabeled=False):
        new_data = []
        for repo in self.data.keys():
            if not predict_only_unlabeled or (predict_only_unlabeled and self.data[repo]['topics'] == []):
                text = self.data[repo]['readme']['content']
                processed_text = self.preprocessor.preprocess_text(text)
                new_data.append({'repo_name': repo, 'text': processed_text})

        test_df = pd.DataFrame(new_data)
        X_test = test_df['text'].values.astype('U')
        tfidf_x_test = self.tfidf_vectorizer.transform(X_test)

        y_pred = self.lr_model.predict(tfidf_x_test)

        for i in range(len(y_pred)):
            topic_list = []
            for j in range(len(y_pred[i])):
                if y_pred[i][j] == 1:
                    topic_list.append(y_train.columns[j])
            unique_topics = list(set(self.data[new_data[i]['repo_name']]['topics'] + topic_list))
            self.data[new_data[i]['repo_name']]['topics'] = unique_topics
        
        self.write_to_file(self.data)
    
    def write_to_file(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=3)

train_df = pd.read_csv('./topics220_repos152k_train.csv')
text_col = 'text'
X_train = train_df[[text_col]]
y_train = train_df[train_df.columns.difference([text_col])]

tag_recommender = TagRecommender("readmes1.json", "data_prep_lists/SE_abbr.txt")
tag_recommender.train_tfidf(X_train, text_col)
tag_recommender.load_lr_model(os.path.join(os.path.dirname(__file__), 'models/lr--0--0--Multilabel.pkl'))
tag_recommender.predict_tags(predict_only_unlabeled=True)
