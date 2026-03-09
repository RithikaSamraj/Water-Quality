from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Reading
from utils import predict_potability, generate_pdf_report
import os

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)

# --- Authentication Routes ---
@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials')
                
    return render_template('auth.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('auth.login'))
        
    user = User(username=username, email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    flash('Registration successful! Please login.')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# --- Main Routes ---
@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    prediction = None
    if request.method == 'POST':
        data = {
            'ph': request.form.get('ph'),
            'hardness': request.form.get('hardness'),
            'solids': request.form.get('solids'),
            'chloramines': request.form.get('chloramines'),
            'sulfate': request.form.get('sulfate'),
            'conductivity': request.form.get('conductivity'),
            'organic_carbon': request.form.get('organic_carbon'),
            'trihalomethanes': request.form.get('trihalomethanes'),
            'turbidity': request.form.get('turbidity')
        }
        
        prediction = predict_potability(data)
        
        # Save to DB
        reading = Reading(
            user_id=current_user.id,
            ph=float(data['ph']),
            hardness=float(data['hardness']),
            solids=float(data['solids']),
            chloramines=float(data['chloramines']),
            sulfate=float(data['sulfate']),
            conductivity=float(data['conductivity']),
            organic_carbon=float(data['organic_carbon']),
            trihalomethanes=float(data['trihalomethanes']),
            turbidity=float(data['turbidity']),
            prediction=prediction
        )
        db.session.add(reading)
        db.session.commit()
        
        # Generate PDF immediately
        generate_pdf_report(reading)
        
    return render_template('dashboard.html', prediction=prediction)

@main_bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    readings = Reading.query.filter_by(user_id=current_user.id).order_by(Reading.timestamp.desc()).paginate(page=page, per_page=10)
    return render_template('history.html', readings=readings)

@main_bp.route('/download/<int:reading_id>')
@login_required
def download_report(reading_id):
    reading = Reading.query.get_or_404(reading_id)
    if reading.user_id != current_user.id:
        return "Unauthorized", 403
        
    filename = f"report_{reading.id}.pdf"
    path = os.path.join("static", "reports", filename)
    
    if not os.path.exists(path):
        generate_pdf_report(reading)
        
    return send_file(path, as_attachment=True)
