import pandas as pd
from collections import defaultdict

class VectorSpaceModel:
    def __init__(self, sql_query_result, included_words):
        """
        Initializes the VectorSpaceModel with the SQL query results and included words.
        
        Parameters:
        - sql_query_result: List of tuples containing the SQL query results.
        - included_words: List of words that are included in the query.
        """
        self.sql_query_result = sql_query_result
        self.included_words = included_words
        self.vector_df = self.create_vector_space_model()
        
    def create_vector_space_model(self):
        """
        Creates a vector space model from the SQL query results.
        
        Returns:
        - DataFrame representing the vector space model.
        """
        # Process the SQL query result to create a vector space model
        df = pd.DataFrame(self.sql_query_result, columns=['id', 'filename', 'classification', 'feature_value', 'weight'])
        
        # Create a set of unique features
        features = sorted(df['feature_value'].unique())
        
        # Initialize a dictionary to store the vectors for each file
        file_vectors = defaultdict(lambda: [0] * len(features))

        # Fill in the vectors with corresponding weights
        for _, row in df.iterrows():
            filename = row['filename']
            feature = row['feature_value']
            weight = row['weight']
            
            # Check if the feature is in the included_words list
            query_weight = 1.0  # Default weight
            if feature in self.included_words:
                query_weight = 3.0  # Example increased weight for included words
            
            # Update the vector for this filename
            feature_index = features.index(feature)
            file_vectors[filename][feature_index] = weight * query_weight

        # Convert to a DataFrame for easy visualization
        vector_df = pd.DataFrame.from_dict(file_vectors, orient='index', columns=features)
        return vector_df
    
    def get_sorted_vector_df(self):
        """
        Returns the sorted vector DataFrame in descending order.
        
        Returns:
        - DataFrame sorted by feature weights.
        """
        sorted_vector_df = self.vector_df.sort_values(by=list(self.vector_df.columns), ascending=False, axis=0)
        return sorted_vector_df