import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import pickle
import os

def train():
    # Load data
    print("Loading data...")
    if not os.path.exists("water_potability.csv"):
        print("Error: water_potability.csv not found!")
        return

    df = pd.read_csv("water_potability.csv")
    
    # Handle missing values
    print("Handling missing values...")
    imputer = SimpleImputer(strategy='mean')
    df['ph'] = df['ph'].fillna(df['ph'].mean())
    df['Sulfate'] = df['Sulfate'].fillna(df['Sulfate'].mean())
    df['Trihalomethanes'] = df['Trihalomethanes'].fillna(df['Trihalomethanes'].mean())
    
    X = df.drop('Potability', axis=1)
    y = df['Potability']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale data (optional for RF but good practice)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Model Accuracy: {accuracy:.4f}")
    
    # Save artifacts
    print("Saving model and scaler...")
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
        
    print("Done!")

if __name__ == "__main__":
    train()
