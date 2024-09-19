import os
from nltk.data import find
from nltk.corpus import wordnet
import nltk
from nltk.tokenize import word_tokenize

# Set NLTK data path to the current folder
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.mkdir(nltk_data_path)

nltk.data.path.append(nltk_data_path)

# Ensure necessary NLTK data is downloaded in the same folder
def download_nltk_data():
    try:
        find('corpora/wordnet.zip')
    except LookupError:
        nltk.download('wordnet', download_dir=nltk_data_path)

    try:
        find('tokenizers/punkt.zip')
    except LookupError:
        nltk.download('punkt', download_dir=nltk_data_path)

download_nltk_data()

def get_synonyms(word, limit=3):
    """Get top synonyms for a given word from WordNet, limited to a certain number."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
            if len(synonyms) >= limit:
                return list(synonyms)
    return list(synonyms)

def tokenize_phrase(phrase):
    """Tokenize multi-word phrases like 'sports car' into individual words."""
    return word_tokenize(phrase)

def process_top_features(features):
    """Process top features to find top synonyms and adjust probabilities."""
    processed_features = []
    
    features_sorted = sorted(features, key=lambda x: x['probability'], reverse=True)
    top_half_count = len(features_sorted) // 2
    top_features = features_sorted[:top_half_count]
    
    for feature in top_features:
        feature_value = feature['feature_value']
        
        words = tokenize_phrase(feature_value)
        
        for word in words:
            synonyms = get_synonyms(word, limit=3)
            for synonym in synonyms:
                processed_features.append({
                    "filename": feature['filename'],
                    "feature_type": feature['feature_type'],
                    "feature_value": synonym,
                    "probability": feature['probability'] / 1.5
                })
    
    return processed_features
