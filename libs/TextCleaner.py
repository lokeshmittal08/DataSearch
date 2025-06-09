from  singleton_decorator import singleton
import re
import nltk
from nltk.corpus import stopwords


@singleton
class TextCleaner:
    def __init__(self):
        nltk.download('stopwords', quiet=True)
        self.stop_words = set(stopwords.words('english'))
        
    def clean(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)  # normalize whitespace
        text = re.sub(r'[^a-z0-9\s]', '', text)  # remove punctuation
        text = ' '.join([word for word in text.split() if word not in self.stop_words])
        return text