import pickle
import os
import numpy as np
from fpdf import FPDF
from models import Reading

MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'

_model = None
_scaler = None

def load_model():
    global _model, _scaler
    if _model is None:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
        else:
            print("Warning: Model file not found.")
            
    if _scaler is None:
        if os.path.exists(SCALER_PATH):
            with open(SCALER_PATH, 'rb') as f:
                _scaler = pickle.load(f)
        else:
            print("Warning: Scaler file not found.")

def predict_potability(data):
    """
    Predicts potability based on input dictionary.
    data: dict with keys matching Reading model fields (excluding user_id, timestamp, id, prediction)
    Returns: "Potable" or "Not Potable"
    """
    load_model()
    if _model is None or _scaler is None:
        return "Model Error"
    
    # Ensure order matches training
    # Feature order: ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity
    # Note: Training used 'Hardness' (capital H), etc. Need to match.
    # Input dictionary keys are lowercase from form (assumed). Map them.
    
    try:
        features = [
            float(data.get('ph', 7.0)),
            float(data.get('hardness', 0)),
            float(data.get('solids', 0)),
            float(data.get('chloramines', 0)),
            float(data.get('sulfate', 0)),
            float(data.get('conductivity', 0)),
            float(data.get('organic_carbon', 0)),
            float(data.get('trihalomethanes', 0)),
            float(data.get('turbidity', 0))
        ]
        
        features_array = np.array([features])
        scaled_features = _scaler.transform(features_array)
        prediction = _model.predict(scaled_features)[0]
        
        return "Potable" if prediction == 1 else "Not Potable"
    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Error"

def get_parameter_status(param_name, value):
    """
    Returns a status string and advice based on parameter value.
    Rough thresholds based on general water quality standards (WHO/EPA).
    """
    status = ""
    advice = ""
    
    if param_name == 'ph':
        if value < 6.5:
            status = "Acidic"
            advice = "Water is acidic. Can cause corrosion of pipes and release metals like lead/copper. Potential health risks include gastrointestinal irritation."
        elif value > 8.5:
            status = "Alkaline"
            advice = "Water is alkaline. Can cause scaling in pipes and aesthetic problems (taste). Generally not a major health risk but affects treatment."
        else:
            status = "Neutral/Safe"
            advice = "pH is within the safe range (6.5 - 8.5). Suitable for consumption."
            
    elif param_name == 'hardness':
        if value > 200:
             status = "Hard"
             advice = "High mineral content. Can cause scaling and reduce soap efficiency. Not a direct health risk."
        else:
            status = "Acceptable"
            advice = "Hardness level is acceptable."

    elif param_name == 'solids': # TDS
        if value > 1000:
             status = "High TDS"
             advice = "High Total Dissolved Solids. May indicate presence of salts or contaminants. Can affect taste."
        else:
             status = "Acceptable"
             advice = "TDS levels are within acceptable limits."
             
    elif param_name == 'chloramines':
        if value > 4:
            status = "High"
            advice = "Chloramines exceeding 4 mg/L can cause eye/nose irritation and stomach discomfort."
        else:
            status = "Safe"
            advice = "Chloramine levels are safe."

    elif param_name == 'sulfate':
         if value > 250:
             status = "High"
             advice = "High sulfate can cause laxative effects and gastrointestinal issues, especially in infants."
         else:
             status = "Safe"
             advice = "Sulfate levels are within safe limits."
             
    elif param_name == 'conductivity':
        if value > 400: # Rough guide
             status = "High"
             advice = "High conductivity indicates high dissolved mineral content."
        else:
             status = "Normal"
             advice = "Conductivity is within normal range."
             
    elif param_name == 'organic_carbon':
        if value > 4: # TOC often < 2-4 mg/L in treated water
             status = "High"
             advice = "Elevated organic carbon may indicate potential for bacteria growth or disinfection byproducts."
        else:
             status = "Safe"
             advice = "Organic carbon levels are low."
             
    elif param_name == 'trihalomethanes':
        if value > 80: # EPA limit 80 ppb
             status = "High (Check)"
             advice = "High THMs are linked to increased cancer risk over long-term exposure. Liver/kidney issues possible."
        else:
             status = "Safe"
             advice = "Trihalomethanes are within regulatory limits."
             
    elif param_name == 'turbidity':
        if value > 5: # WHO limit
             status = "High"
             advice = "High turbidity indicates suspended particles. Can shelter pathogens and interfere with disinfection."
        else:
             status = "Safe"
             advice = "Turbidity is low and acceptable."
             
    return status, advice

def generate_pdf_report(reading):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Water Quality Analysis Report', 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Report Info
    pdf.cell(0, 10, f"Report ID: {reading.id}", 0, 1)
    pdf.cell(0, 10, f"Date: {reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 10, f"User: {reading.user.username}", 0, 1)
    pdf.ln(5)
    
    # Result
    pdf.set_font("Arial", 'B', 14)
    color = (0, 128, 0) if reading.prediction == "Potable" else (255, 0, 0)
    pdf.set_text_color(*color)
    pdf.cell(0, 10, f"Prediction Result: {reading.prediction}", 0, 1)
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.ln(5)
    
    # Detailed Analysis
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detailed Parameter Analysis:", 0, 1)
    pdf.set_font("Arial", size=11)
    
    parameters = [
        ('pH', reading.ph, 'ph'),
        ('Hardness', reading.hardness, 'hardness'),
        ('Solids (TDS)', reading.solids, 'solids'),
        ('Chloramines', reading.chloramines, 'chloramines'),
        ('Sulfate', reading.sulfate, 'sulfate'),
        ('Conductivity', reading.conductivity, 'conductivity'),
        ('Organic Carbon', reading.organic_carbon, 'organic_carbon'),
        ('Trihalomethanes', reading.trihalomethanes, 'trihalomethanes'),
        ('Turbidity', reading.turbidity, 'turbidity')
    ]
    
    for label, value, key in parameters:
        status, advice = get_parameter_status(key, value)
        
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(50, 8, f"{label}: {value:.2f}", 0, 0)
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(0, 8, f"Status: {status}", 0, 1)
        
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 5, f"Analysis: {advice}")
        pdf.ln(2)
        
    filename = f"report_{reading.id}.pdf"
    path = os.path.join("static", "reports", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return path
