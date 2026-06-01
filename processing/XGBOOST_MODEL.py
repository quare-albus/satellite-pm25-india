from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import GridSearchCV
import pandas as pd 
from pathlib import Path
import xgboost as xgb
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

import matplotlib.pyplot as plt



current_folder = Path(__file__).parent.resolve()

# Load the merged dataset
master_df = pd.read_csv(current_folder / "../data/processed/master_data.csv")

#convert it to datetime and sort it by time and station id
master_df["time"] = pd.to_datetime(master_df["time"]).dt.date
master_df = master_df.sort_values(by=["Station_Id", "time"]).reset_index(drop=True)

master_df["month"] = pd.to_datetime(master_df["time"]).dt.month
master_df["day"] = pd.to_datetime(master_df["time"]).dt.day
master_df["dayofweek"] = pd.to_datetime(master_df["time"]).dt.dayofweek
master_df["sin_day"] = np.sin(2 * np.pi * master_df["day"] / 31)
master_df["cos_day"] = np.cos(2 * np.pi * master_df["day"] / 31)
master_df["sin_month"] = np.sin(2 * np.pi * master_df["month"] / 12)
master_df["cos_month"] = np.cos(2 * np.pi * master_df["month"] / 12)


# THE SPLIT
train_df = master_df[master_df["time"] < pd.to_datetime("2025-10-01").date()]
test_df = master_df[master_df["time"] >= pd.to_datetime("2025-10-01").date()]

# Define features and target variable
X_train = train_df.drop(columns=["PM2.5", "time"])
y_train = train_df["PM2.5"] 

X_test = test_df.drop(columns=["PM2.5", "time"])
y_test = test_df["PM2.5"]

# Train the XGBoost model
model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=200, learning_rate=0.5, max_depth=6, random_state=42)
model.fit(X_train, y_train)


#tuing the model using GridSearchCV
param_grid = {
    "n_estimators": [100, 300],
    "max_depth": [4, 6, 8],
    "learning_rate": [0.03, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0]
}

grid = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    cv=3,
    scoring="r2",
    verbose=1,
    n_jobs=-1
)

grid.fit(X_train, y_train)

print(grid.best_params_)

best_model = grid.best_estimator_

# Predict on the test set
y_pred = best_model.predict(X_test)

# Evaluate the model

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R^2 Score: {r2}")

# Assuming y_test is your actual data and y_pred is your model's prediction
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.5)

# Add a diagonal line for reference
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)

plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Actual vs Predicted')
plt.show()