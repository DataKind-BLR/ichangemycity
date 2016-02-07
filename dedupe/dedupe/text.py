import nltk
import math
from nltk.stem.porter import PorterStemmer
import nltk.data
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.corpus import stopwords
from collections import Counter

class TextUtils(object):
    """
    Helper class that handles text processing
    """
    
    # The Punkt sentence tokenizer 
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    # The TreeBank word tokenizer
    tokenizer = TreebankWordTokenizer()
    # Porter Stemmer
    stemmer = PorterStemmer()
    # common english stop words
    stop_words = set(stopwords.words('english')).union([stemmer.stem(sw) for sw in stopwords.words('english')])


    @staticmethod
    def tokenizeText(text):
        """
        Given a string, performs the following steps in order:
            - Lowercases and tokenizes the string into sentences
            - tokenizes each sentence and adds each tokenized sentence to the list
            - performs stemming on each token
            - filters only alpha-numeric data from the list
            
        """
        sentences = TextUtils.sent_detector.tokenize(text.lower())
        tokens = []
        for sentence in sentences:
            # tokenize
            toks = TextUtils.tokenizer.tokenize(sentence)
            # strip and stem the words
            tokens.extend(map(lambda x: TextUtils.stemmer.stem(x.strip()), toks))    
        # filter out non-alphanumeric words i.e punctuation and remove stop words
        # TODO normalize words here - this should not filter out don't - etc
        return filter(lambda x: x.isalnum() and x not in TextUtils.stop_words, tokens)