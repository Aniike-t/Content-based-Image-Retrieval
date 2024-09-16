from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk

# Ensure necessary NLTK data is downloaded
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')

def get_synonyms(word):
    """Get synonyms for a given word from WordNet."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def tokenize_phrase(phrase):
    """Tokenize a multi-word phrase into individual words."""
    return word_tokenize(phrase)

def process_top_features(features):
    """Process top features to find synonyms and adjust probabilities."""
    processed_features = []
    
    # Sort features by probability in descending order and take the top half
    features_sorted = sorted(features, key=lambda x: x['probability'], reverse=True)
    top_half_count = len(features_sorted) // 2
    top_features = features_sorted[:top_half_count]
    
    for feature in top_features:
        feature_value = feature['feature_value']
        
        # Tokenize multi-word values
        words = tokenize_phrase(feature_value)
        
        # For each word, get synonyms and create new feature entries
        for word in words:
            synonyms = get_synonyms(word)
            for synonym in synonyms:
                processed_features.append({
                    "filename": feature['filename'],
                    "feature_type": feature['feature_type'],
                    "feature_value": synonym,
                    "probability": feature['probability'] / 2
                })
    
    return processed_features
