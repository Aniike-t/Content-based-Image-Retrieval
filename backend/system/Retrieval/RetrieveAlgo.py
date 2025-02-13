# --- START OF FILE RetrieveAlgo.py --- (Corrected)

import pandas as pd
import numpy as np
import os
from nltk.corpus import wordnet

class VectorSpaceModel:
    def __init__(self, db_manager, included_words, query):
        self.db_manager = db_manager
        self.included_words = included_words
        self.query = query
        self.vector_df = self.create_vector_space_model()

    def get_synonyms(self, word, limit=10):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
                if len(synonyms) >= limit:
                    print(synonyms)
                    return list(synonyms)
        print(synonyms)           
        return list(synonyms)

    def create_vector_space_model(self):
        # --- Stage 1: Broad Feature Selection ---
        all_query_terms = self.included_words.copy()
        for word in self.included_words:
            all_query_terms.extend(self.get_synonyms(word))
        all_query_terms = list(set(all_query_terms))

        placeholders = ', '.join(['?'] * len(all_query_terms))
        broad_sql_query = f"""
            SELECT DISTINCT filename
            FROM Imagefeatures
            WHERE feature_value IN ({placeholders})
        """
        relevant_filenames_result = self.db_manager.fetch_query_results(broad_sql_query, tuple(all_query_terms))

        if not relevant_filenames_result:
            return pd.DataFrame()

        relevant_filenames = [os.path.basename(row[0]) for row in relevant_filenames_result]
        filename_placeholders = ', '.join(['?'] * len(relevant_filenames))
        filename_where_clause = f"filename IN ({filename_placeholders})"

        # --- Stage 2: Precise Feature Selection ---
        precise_sql_query = f"""
            SELECT filename, feature_value, probability
            FROM Imagefeatures
            WHERE {filename_where_clause}
        """
        sql_query_result = self.db_manager.fetch_query_results(precise_sql_query, tuple(relevant_filenames))

        if not sql_query_result:
            return pd.DataFrame()

        df = pd.DataFrame(sql_query_result, columns=['filename', 'feature_value', 'probability'])
        df['filename'] = df['filename'].apply(os.path.basename)

        # --- Pivot (WITHOUT fill_value) ---
        pivot_df = df.pivot_table(index='filename', columns='feature_value', values='probability', aggfunc='first')

        # --- Impute Missing Values (AFTER pivoting) ---
        # Find a small value to impute (e.g., 1/10th the smallest non-zero probability)
        min_prob = df['probability'][df['probability'] > 0].min()
        imputation_value = min_prob / 10.0 if not pd.isna(min_prob) else 0.0001 # Default if no probabilities > 0

        pivot_df = pivot_df.fillna(imputation_value)

        # Ensure all features from the query (and synonyms) are present,
        # filling any that are still missing *after* the initial imputation
        for feature in all_query_terms:
            if feature not in pivot_df.columns:
                pivot_df[feature] = imputation_value

        
        # --- Weighting and Normalization ---
        image_vectors = pivot_df.to_numpy()
        print(image_vectors)
        weights = np.array([3.5 if feature in self.included_words else 0.75 for feature in pivot_df.columns])
        weighted_vectors = image_vectors * weights
        print(weighted_vectors)
        norms = np.linalg.norm(weighted_vectors, axis=1, keepdims=True)
        with np.errstate(divide='ignore', invalid='ignore'):
            normalized_vectors = np.where(norms != 0, weighted_vectors / norms, 0)
        vector_df = pd.DataFrame(normalized_vectors, index=pivot_df.index, columns=pivot_df.columns)
        print(vector_df)
        return vector_df

    def construct_sql_query(self):
        return None, None

    def get_sorted_vector_df(self):
        if self.vector_df.empty:
            return pd.DataFrame()

        query_vector = self.create_query_vector()
        image_vectors = self.vector_df.to_numpy()
        similarity_scores = np.dot(image_vectors, query_vector)
        sorted_df = self.vector_df.copy()
        sorted_df['similarity'] = similarity_scores
        sorted_df = sorted_df.sort_values(by='similarity', ascending=False)
        return sorted_df

    def create_query_vector(self):
        query_vector = pd.Series(0.0, index=self.vector_df.columns)
        all_query_terms = self.included_words.copy()
        for word in self.included_words:
            all_query_terms.extend(self.get_synonyms(word))
        all_query_terms = list(set(all_query_terms))

        for term in all_query_terms:
            if term in query_vector.index:
                weight = 3.5 if term in self.included_words else 0.75
                query_vector[term] = weight

        norm = np.linalg.norm(query_vector.to_numpy())
        if norm > 0:
            query_vector = query_vector / norm
        return query_vector.to_numpy()