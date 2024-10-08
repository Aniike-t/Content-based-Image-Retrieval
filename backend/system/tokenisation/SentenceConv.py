''' Under Development '''
import spacy
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import nltk

'''Download necessary NLTK data (only needed the first time)'''
# nltk.download('stopwords')

class SentenceConverter:
    def __init__(self):
        # Initialize spaCy model and other necessary components
        self.nlp = spacy.load('en_core_web_sm')
        self.ps = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.negation_words = [
            'without', 'no', 'not', 'never', 'none', 'nobody', 'nothing', 
            'neither', 'nor', 'nowhere', 'hardly', 'barely', 'scarcely', 
            'except', 'excluding', 'but', 'minus', 'avoid', 'lack', 'absent', 
            'denied', 'prohibited', 'devoid', 'omit', 'forbid'
        ]

    def convert_to_query(self, sentence):
        # Tokenize and process the sentence
        doc = self.nlp(sentence.lower())

        included_words = []
        excluded_words = []
        negated_words = set()  # Keep track of negated words

        # Process words for inclusion/exclusion
        for i, token in enumerate(doc):
            if token.text in self.negation_words:  # If token is a negation
                next_word = doc[i + 1] if i + 1 < len(doc) else None
                if next_word and next_word.text not in self.stop_words:  # Ensure it's not a stopword
                    stemmed_word = self.ps.stem(next_word.text)
                    excluded_words.append(f"-{stemmed_word}")
                    negated_words.add(next_word.text)
            elif token.text not in self.stop_words and token.text not in negated_words:
                stemmed_word = self.ps.stem(token.text)
                included_words.append(stemmed_word)

        # Construct and return the final query
        return ' '.join(included_words + excluded_words)




# converter = SentenceConverter()
# sentence = "A car behind tree without wheel"
# result = converter.convert_to_query(sentence)
# print(result)  # Output: car tree -bush
