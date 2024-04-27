import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
from pi_voice.utils.synchronization import writing_lgbm_data, writing_lgbm_model
from pi_voice.operators.DataOperator import DataOperator
from pi_voice.config import config, get_path_from


class LGBMOperator:
    def __init__(self):
        self.test_size = config["lgbm"]["testSize"]
        self.random_state = config["lgbm"]["randomState"]
        self.data_operator = DataOperator()

    def _convert_time_to_fractional_hours(self, time_str):
        if pd.isna(time_str):
            return np.nan
        hours, minutes = map(int, time_str.split(':'))
        return hours + minutes / 60.0

    def _preprocess_data(self, df):
        df['hour'] = df['time_of_day'].apply(
            self._convert_time_to_fractional_hours
        )

        day_mapping = {
            'Mon': 1,
            'Tue': 2,
            'Wed': 3,
            'Thu': 4,
            'Fri': 5,
            'Sat': 6,
            'Sun': 7
        }
        df['time_of_day'] = pd.to_numeric(df['time_of_day'], errors='coerce')
        df['day_of_week'] = df['day_of_week'].map(day_mapping)
        return df

    def _train_model(self, df, target_column):
        X = df.drop(target_column, axis=1)
        y = df[target_column]
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded,
            test_size=self.test_size,
            random_state=self.random_state
        )

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

    def load_data_and_train_model(self, save=True):
        # Load the dataset using the instance of DataOperator
        writing_lgbm_data.acquire(timeout=2.0)
        df = self.data_operator.load_csv(
            get_path_from(config["lgbm"]["dataset"])
        )
        writing_lgbm_data.release()

        df_preprocessed = self._preprocess_data(df)

        # Train the LightGBM model
        model, label_encoder = self._train_model(
            df_preprocessed,
            target_column='commands'
        )

        if save is True:
            self._save_model(model, label_encoder)

    def _save_model(self, model, label_encoder):
        writing_lgbm_model.acquire(timeout=2.0)
        model.save_model(get_path_from(config["lgbm"]["model"]))
        self.data_operator.save_label_encoder(
            label_encoder,
            get_path_from(config["lgbm"]["labelEncoder"])
        )
        writing_lgbm_model.release()

    def _load_model(self):
        with writing_lgbm_model:
            return lgb.Booster(
                model_file=get_path_from(config["lgbm"]["model"])
            ), self.data_operator.load_label_encoder(
                get_path_from(config["lgbm"]["labelEncoder"])
            )

    def predict(self, data):
        model, label_encoder = self._load_model()
        df = pd.DataFrame(data)
        processed_data = self._preprocess_data(df)
        prediction_probabilities = model.predict(processed_data)

        # Get the index of the max probability
        predicted_index = np.argmax(prediction_probabilities, axis=1)
        # Transform this index back into the original class label
        predicted_command = label_encoder.inverse_transform(predicted_index)

        return predicted_command[0]


def run_test():
    # Create an instance of LGBMOperator
    lgbm_operator = LGBMOperator()

    # Load the data and train the model
    lgbm_operator.load_data_and_train_model()

    # Define a sample data point for prediction
    data_point = {
        'humidity': [62.329812682755794],
        'temperature': [76.38918225943932],
        'light_levels': [28747.42688003669],
        'time_of_day': ['06:00'],
        'day_of_week': ['Tue']
    }

    # Make a prediction using the trained model
    prediction = lgbm_operator.predict(data_point)

    # Print the predicted command
    print(f"Predicted command: {prediction}")
