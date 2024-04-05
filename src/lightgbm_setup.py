# @title  Data Loading Function
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd


def load_data(filepath):
    """Load dataset from a CSV file."""
    df = pd.read_csv(filepath)
    return df


# @title Data Loading Function
def convert_time_to_fractional_hours(df, time_column):
    """Convert time in 'HH:MM' format to fractional hours."""
    def time_to_fractional_hours(time_str):
        if pd.isna(time_str):
            return np.nan
        hours, minutes = map(int, time_str.split(':'))
        return hours + minutes / 60.0

    df['Hour'] = df[time_column].apply(time_to_fractional_hours)
    return df.drop(columns=[time_column])


def preprocess_data(df):
    """Preprocess the dataset to convert time and day columns to numeric formats."""
    # Convert 'Time of Day' from 'HH:MM' to fractional hours
    def time_to_fractional_hours(time_str):
        hours, minutes = map(int, time_str.split(':'))
        return hours + minutes / 60.0
    df['Hour'] = df['Time of Day'].apply(time_to_fractional_hours)

    # Map 'Day of Week' from abbreviations to numeric values
    day_mapping = {'Mon': 1, 'Tue': 2, 'Wed': 3,
                   'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7}
    df['DayOfWeek'] = df['Day of Week'].map(day_mapping)

    # Drop the original 'Time of Day' and 'Day of Week' columns
    df.drop(columns=['Time of Day', 'Day of Week'], inplace=True)

    print(df)

    return df

def train_model(df, target_column, test_size=0.2, random_state=42):
    """Train a LightGBM model on the dataset."""
    X = df.drop(target_column, axis=1)
    y = df[target_column]

    # Encode the target variable
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state)

    # Prepare datasets for LightGBM
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    params = {
        'objective': 'multiclass',
        'num_class': len(df[target_column].unique()),
        'metric': 'multi_logloss',
        'learning_rate': 0.1,
        'num_leaves': 31,
        'verbose': -1
    }

    lgb_model = lgb.train(params, train_data, valid_sets=[test_data])
    return lgb_model, le

def predict_command(model, label_encoder, data):
    """Predict the command for new sensor data."""
    pred_probs = model.predict([data])
    pred_index = pred_probs.argmax(axis=1)
    command = label_encoder.inverse_transform(pred_index)
    return command[0]

def run_test():
    # Load the dataset
    df = load_data('/Users\\husam\\Documents\\uni\\fyp\\Project\\PiVoice\\daatasets\\sensor_data.csv')
    
    # Preprocess the dataset (specify the correct time column name)
    df_preprocessed = preprocess_data(df)
    
    # Train the LightGBM model
    model, label_encoder = train_model(df_preprocessed, target_column='Commands')
    
    # Predict a command (replace with actual sensor data)
    # Example data; include hour and day of week as numbers
    new_data = [12.33055077274342, -32.87537546617379,
                51475.026243615445, 17.27, 1]
    predicted_command = predict_command(model, label_encoder, new_data)
    print(f'Predicted command: {predicted_command}')
