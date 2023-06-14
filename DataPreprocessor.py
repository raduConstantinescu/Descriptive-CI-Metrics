import string
import nltk
import unicodedata
import ast
import re
from spiral.simple_splitters import heuristic_split
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self, abbreviations_file_path):
        self.abbreviations = self.read_abbreviations(abbreviations_file_path)
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    @staticmethod
    def remove_dates(text):
      nDAY = r'(?:[0-3]?\d)'  # day can be from 1 to 31 with a leading zero 
      nMNTH = r'(?:11|12|10|0?[1-9])' # month can be 1 to 12 with a leading zero
      nYR = r'(?:(?:19|20)\d\d)' 

      NUM_DATE = f"""
          (?P<num_date>
              (?:^|\D) # new bit here
              (?:
              # YYYY-MM-DD
              (?:{nYR}(?P<delim1>[\/\-\._]?){nMNTH}(?P=delim1){nDAY})
              |
              # YYYY-DD-MM
              (?:{nYR}(?P<delim2>[\/\-\._]?){nDAY}(?P=delim2){nMNTH})
              |
              # DD-MM-YYYY
              (?:{nDAY}(?P<delim3>[\/\-\._]?){nMNTH}(?P=delim3){nYR})
              |
              # MM-DD-YYYY
              (?:{nMNTH}(?P<delim4>[\/\-\._]?){nDAY}(?P=delim4){nYR})
              )
              (?:\D|$) # new bit here
          )"""

      myDate = re.compile(NUM_DATE, re.IGNORECASE | re.VERBOSE | re.UNICODE)
      text = myDate.sub('', text)
      return text

    @staticmethod
    def read_abbreviations(file_path):
      with open(file_path, 'r') as file:
          content = file.read()
      abbreviations = ast.literal_eval(content)
      return abbreviations

    def preprocess_text(self, text):
        # Remove code snippets
        text = re.sub(r'```[\s\S]*?```', '', text)  # Remove multiline code blocks
        text = re.sub(r'`[^`]+`', '', text)  # Remove inline code snippets

        # Remove markdown symbols
        text = re.sub(r'[\*_`~]', '', text)  # Remove emphasis, bold, code, and strikethrough symbols
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Remove hyperlinks [text](url)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Remove image tags ![alt text](url)
        text = re.sub(r'\[.*?\]', '', text) # Remove remaining hyperlink text [text]

        # Remove urls
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        text = url_pattern.sub('', text)

        # Remove emails
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        text = re.sub(email_regex, '', text)

        # Remove dates
        text = self.remove_dates(text)

        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove digits
        text = text.translate(str.maketrans('', '', string.digits))

        # Remove non-English characters
        words = nltk.word_tokenize(text)
        words = [word for word in words if word.isalpha()]

        # Remove non-ASCII characters
        words = [unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8') for word in words]

        # Split snake case, camel case
        words = [heuristic_split(word) for word in words]
        words = [word for word_list in words for word in word_list]

        # Convert to lower case
        words = [word.lower() for word in words]

        # Replace abbreviations
        words = [self.abbreviations.get(word, word) for word in words]

        # Join the words back into a single string
        processed_text = ' '.join(words)

        # Remove subsequent spaces
        processed_text = re.sub(r'\s+', ' ', processed_text)

        # Tokenize the text into individual words
        tokens = word_tokenize(processed_text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words]
        
        # Lemmatize the tokens
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]
        
        # Join the tokens back into a single string
        processed_text = ' '.join(tokens)

        return processed_text