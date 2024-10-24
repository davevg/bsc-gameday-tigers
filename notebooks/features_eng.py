import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, MinMaxScaler

# DataFrame Selector for selecting specific columns - updated
class DataFrameSelector(BaseEstimator, TransformerMixin):
    def __init__(self, attribute_names): 
        self.attribute_names = attribute_names
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X[self.attribute_names]


# Custom transformer to drop rows with missing values
class DropMissingValues(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return X.dropna()

# Custom transformer to round numerical values
class RoundValues(BaseEstimator, TransformerMixin):
    def __init__(self, decimals=2):  # Set default precision to 2
        self.decimals = decimals
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        return np.round(X, self.decimals)  # Round the values to the specified decimal places

# feature engineering function and creating prepared numpy input
def create_prepared_numpy_array(df):

    # features_df = df[['timestamp', 'log_level', 'method', 'status_code', 'response_time']].copy()

    prepared_data_cols = ['log_level', 'PUT', 'GET', 'POST', 'DELETE', 'response_time',] # day_of_week', 'hour'
    # Categorical pipeline for log_level and method
    cat_attributes_log_level = ['log_level']
    cat_attributes_method = ['method']
    # Numerical pipeline for response_time, path_encoded, hour, day_of_week
    # num_attributes_day_time = ['day_of_week', 'hour'] 
    response_time_attributes = ['response_time', ] 

    log_level_pipeline = Pipeline([
        ('selector', DataFrameSelector(cat_attributes_log_level)),
        ('drop_missing', DropMissingValues()),  # Drop rows with missing values
        ('ordinal_encoder', OrdinalEncoder(categories=[['DEBUG', 'INFO', 'WARN', 'ERROR']])),  # Ordinal encoding
        # ('scaler', MinMaxScaler(feature_range=(0.2, 1))),  # Normalize the numerical features
        # ('rounder', RoundValues(decimals=2)), 
    ])

    response_time_pipeline = Pipeline([
        ('selector', DataFrameSelector(response_time_attributes)),
        ('drop_missing', DropMissingValues()),  # Drop rows with missing values
        # ('scaler', StandardScaler()),  # Normalize the numerical features
    ])

    method_pipeline = Pipeline([
        ('selector', DataFrameSelector(cat_attributes_method)),
        ('drop_missing', DropMissingValues()),  # Drop rows with missing values
        # ('onehot_encoder', OneHotEncoder(sparse_output=False))#, drop='first'))  # One-hot encoding
        ('onehot_encoder', OneHotEncoder(categories=[['PUT', 'GET', 'POST', 'DELETE']], 
                                         sparse_output=False, 
                                         handle_unknown='ignore'))  # One-hot encoding for specific values
    ])


    # Full pipeline to combine all pipelines
    full_pipeline = Pipeline(steps=[
        ('union', FeatureUnion(transformer_list=[
            ("log_level_pipeline", log_level_pipeline),# log_level
            ("method_pipeline", method_pipeline), # 'PUT', 'GET', 'POST', 'DELETE'
            ("response_time_pipeline", response_time_pipeline),# 'response_time'  
        ]))
    ])

    # Prepare the data using the full pipeline
    prepared_data = full_pipeline.fit_transform(df)

    # Convert to DataFrame for further processing if needed
    prepared_df = pd.DataFrame(prepared_data, columns=prepared_data_cols)

    # Return prepared data 
    return prepared_data, prepared_df

# Data cleaning 
def df_cleaning(df, columns, inplace=False):
    """
    Clean the DataFrame by dropping rows with missing values in specified columns 
    and removing duplicate rows.

    :param df: DataFrame to clean.
    :param columns: List of column names to check for missing values.
    :param inplace: Boolean value indicating whether to modify the DataFrame in place.
                    If True, the operations will be performed on the original DataFrame. 
                    If False, a new DataFrame will be returned.
    :return: Cleaned DataFrame with rows containing NaN in the specified columns dropped,
             and duplicate rows removed. If inplace=True, returns None.
    
    Steps:
    1. Drop rows with missing values (NaN) in the specified columns.
    2. Drop duplicate rows from the DataFrame.
    """

    if inplace: 
        df.dropna(subset=columns, inplace=inplace)
        df.drop_duplicates(inplace=inplace)
        return None
    else: 
        cleaned_df = df.dropna(subset=columns)
        new_df = cleaned_df.drop_duplicates()
        return new_df

# # Calculate threshold 
def calc_threshold(scores):
    from statistics import mean, stdev

    score_mean = mean(scores)
    score_std = stdev(scores)
    score_max = max(scores)
    
    threshold = score_mean + 3 * score_std
    return threshold, score_mean, score_std

def append_score_and_outlier_to_df_training(df, scores):    
    threshold, score_mean, score_std = calc_threshold(scores)

    df["score"] = pd.Series(scores, index=df.index)
    # Create a new "outlier" column in the DataFrame
    df["outlier"] = df["score"].apply(lambda x: 1 if x > threshold else 0)

    #anomalies = df[df["score"] > threshold2]
    return df 

def append_score_and_outlier_to_df(df, scores, threshold):    

    df["score"] = pd.Series(scores, index=df.index)
    # Create a new "outlier" column in the DataFrame
    df["outlier"] = df["score"].apply(lambda x: 1 if x > threshold else 0)

    #anomalies = df[df["score"] > threshold2]
    return df 


def load_model_metadata_from_s3(bucket_name, s3_key, json_filename):
    import json
    import boto3

    # Download the JSON file from S3
    s3_client = boto3.client('s3')

    # Download the file from S3
    s3_client.download_file(bucket_name, s3_key, json_filename)
    print(f"File downloaded from S3: s3://{bucket_name}/{s3_key}")

    # Load the metadata from the downloaded JSON file
    with open(json_filename, 'r') as f:
        metadata = json.load(f)

    mean_score = metadata['mean_score']
    std_score = metadata['std_score']
    threshold = metadata['threshold']
    print(f"threshold: {threshold}, Mean: {mean_score}, Std Dev: {std_score}, ")
    return threshold, mean_score, std_score
