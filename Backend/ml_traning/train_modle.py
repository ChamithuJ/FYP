import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("Step 1: Loading the dataset...")

df = pd.read_csv("squat_features_augmented.csv")

print("Step 2: Preparing the data...")

target_column = 'label' 


X = df.drop(columns=[target_column, 'video_file', 'frame'], errors='ignore')


feature_names = X.columns.tolist()
print(f"Features the model will learn from: {feature_names}")

y = df[target_column]

print("\nStep 3: Splitting data into Training (80%) and Testing (20%) sets...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Step 4: Training the Random Forest Model...")

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("Step 5: Testing the Model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%\n")

print("Detailed Report:")
print(classification_report(y_test, y_pred))

print("Step 6: Saving the Model...")

joblib.dump(model, "squat_rf_model.pkl")


joblib.dump(feature_names, "model_features.pkl")

print("Model saved successfully as 'squat_rf_model.pkl'!")