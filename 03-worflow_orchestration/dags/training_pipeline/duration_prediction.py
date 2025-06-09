import os
import pandas as pd
import pickle
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import root_mean_squared_error
import mlflow
import xgboost as xgb
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll import scope

def read_dataframe(year, month):
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    return df

def create_x(df, dv=None):
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    if dv is None: 
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else: 
        X = dv.transform(dicts)
    return X, dv

def train_model(X_train, y_train, X_val, y_val, dv):
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("nyc-taxi-experiment")
    train = xgb.DMatrix(X_train, label=y_train)
    valid = xgb.DMatrix(X_val, label=y_val)

    def objective(params):
        with mlflow.start_run():
            mlflow.set_tag("model", "xgboost")
            mlflow.log_params(params)
            booster = xgb.train(
                params=params,
                dtrain=train,
                num_boost_round=2,
                evals=[(valid, 'validation')],
                early_stopping_rounds=2
            )
            y_pred = booster.predict(valid)
            rmse = root_mean_squared_error(y_val, y_pred)
            mlflow.log_metric("rmse", rmse)
        return {'loss': rmse, 'status': STATUS_OK}

    search_space = {
        'max_depth': scope.int(hp.quniform('max_depth', 4, 100, 1)),
        'learning_rate': hp.loguniform('learning_rate', -3, 0),
        'reg_alpha': hp.loguniform('reg_alpha', -5, -1),
        'reg_lambda': hp.loguniform('reg_lambda', -6, -1),
        'min_child_weight': hp.loguniform('min_child_weight', -1, 3),
        'objective': 'reg:squarederror',
        'seed': 42
    }

    best_result = fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=50,
        trials=Trials()
    )

    mlflow.xgboost.autolog(disable=True)
    with mlflow.start_run():
        best_params = {
            'learning_rate': 0.09585355369315604,
            'max_depth': 30,
            'min_child_weight': 1.060597050922164,
            'objective': 'reg:squarederror',
            'reg_alpha': 0.018060244040060163,
            'reg_lambda': 0.011658731377413597,
            'seed': 42
        }
        mlflow.log_params(best_params)
        booster = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=1000,
            evals=[(valid, 'validation')],
            early_stopping_rounds=50
        )
        y_pred = booster.predict(valid)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("rmse", rmse)

        # Ensure the models directory exists
        os.makedirs("03-worflow_orchestration/models", exist_ok=True)
        preprocessor_path = "03-worflow_orchestration/models/preprocessor.b"
        with open(preprocessor_path, "wb") as f_out:
            pickle.dump(dv, f_out)
        mlflow.log_artifact(preprocessor_path, artifact_path="preprocessor")
        mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")
    return None

def run(year, month):
    df_train = read_dataframe(year=year, month=month)
    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1 
    df_val = read_dataframe(year=next_year, month=next_month)
    X_train, dv = create_x(df_train)
    X_val, _ = create_x(df_val, dv)
    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values
    train_model(X_train, y_train, X_val, y_val, dv)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train a model to predict the taxi trip duration")
    parser.add_argument('--year', type=int, required=True, help="Year of the data to train on")
    parser.add_argument('--month', type=int, required=True, help="Month of the data to train on")
    args = parser.parse_args()
    run(year=args.year, month=args.month)