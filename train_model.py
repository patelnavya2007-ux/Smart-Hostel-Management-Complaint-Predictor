import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

import joblib


# Load complaint data
data = pd.read_csv("complaint_data.csv")

# Input and output
X = data["complaint"]
y = data["category"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)


# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])


# Train model
model.fit(X_train, y_train)


# Save model
joblib.dump(model, "complaint_model.pkl")

print("AI Complaint Predictor trained successfully!")
print("Model saved as complaint_model.pkl")