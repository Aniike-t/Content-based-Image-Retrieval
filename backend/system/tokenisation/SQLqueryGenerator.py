import nltk
from nltk.corpus import wordnet
from autocorrect import Speller  # Use Speller from autocorrect

nltk.download('wordnet')

class SQLQueryGenerator:
    def __init__(self, result):
        self.result = result
        self.included_words = []
        self.excluded_words = []
        self.sql_query = ""
        self.spell = Speller()  # Initialize autocorrect Speller
        self.fixed_words = []

    def _parse_result(self):
        # Split the result into included and excluded words
        for word in self.result.split():
            if word.startswith('-'):
                self.excluded_words.append(word[1:])  # Remove the '-' for the excluded word
            else:
                # Apply autocorrect on included words
                # corrected_word = word
                self.included_words.append(word)

    def get_query_synonyms(self):
        # Generate a list of synonyms for each included word
        synonyms = []
        for word in self.included_words:
            syns = wordnet.synsets(word)
            word_synonyms = set()
            for syn in syns:
                for lemma in syn.lemmas():
                    word_synonyms.add(lemma.name())  # Collect synonyms
            synonyms.extend(word_synonyms)
        return self.included_words + list(synonyms)   # Include the original words

    def generate_query(self):
        self.fixed_words = self.included_words
        self._parse_result()
        self.included_words = self.get_query_synonyms()  # Get synonyms after parsing
        
        # Construct the SQL query
        self.sql_query = "SELECT * FROM Imagefeatures WHERE ("

        # Include feature_value conditions
        if self.included_words:
            self.sql_query += " OR ".join([f"feature_value = '{word}'" for word in self.included_words])
        
        # Add AND for excluded conditions
        if self.excluded_words:
            self.sql_query += f") AND (feature_value != '{self.excluded_words[0]}'"
            for word in self.excluded_words[1:]:
                self.sql_query += f" AND feature_value != '{word}'"
        
        self.sql_query += ") ORDER BY filename;"  # Add GROUP BY clause
        return self.sql_query, self.fixed_words

# Example usage
# result = "car behind tree -wheel"
# query_generator = SQLQueryGenerator(result)
# sql_query = query_generator.generate_query()
# print(sql_query)
