import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image


try:
    from keras import models
    MODEL_LOADED = True
    model = models.load_model('static/model/bird_species.h5')
except ImportError:
    MODEL_LOADED = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

CLASSES = ['AMERICAN GOLDFINCH', 'BARN OWL', 'CARMINE BEE-EATER', 'DOWNY WOODPECKER', 'EMPEROR PENGUIN', 'FLAMINGO']

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html')
    return render_template('auth.html', active_tab='login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('auth.html', active_tab='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful, please login', 'success')
        return redirect(url_for('login'))
    return render_template('auth.html', active_tab='register')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if 'image_upload' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
        
    file = request.files['image_upload']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
        
    if file:
        filename = secure_filename(file.filename)
        unique_name = str(uuid.uuid4()) + "_" + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        
        if not MODEL_LOADED:
            pred_class = "Model not loaded (install tensorflow)"
        else:
            image = Image.open(filepath)
            image = image.resize((224, 224))
            # The current model was trained on BGR images and scaled by 255.0
            image_arr = np.array(image.convert('RGB'), dtype=np.float32)
            image_arr = image_arr[:, :, ::-1] / 255.0
            image_arr = np.expand_dims(image_arr, axis=0)
            result = model.predict(image_arr)
            ind = np.argmax(result)
            pred_class = CLASSES[ind]
            
        return redirect(url_for('success', filename=unique_name, prediction=pred_class))

@app.route('/success')
def success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    filename = request.args.get('filename')
    prediction = request.args.get('prediction')
    if not filename or not prediction:
        return redirect(url_for('index'))
        
    return render_template('success.html', full_filename=f"uploads/{filename}", pred=prediction)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'image_upload' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['image_upload']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        unique_name = str(uuid.uuid4()) + "_" + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        
        if not MODEL_LOADED:
            pred_class = "Model not loaded"
        else:
            image = Image.open(filepath)
            image = image.resize((224, 224))
            # The current model was trained on BGR images and scaled by 255.0
            image_arr = np.array(image.convert('RGB'), dtype=np.float32)
            image_arr = image_arr[:, :, ::-1] / 255.0
            image_arr = np.expand_dims(image_arr, axis=0)
            result = model.predict(image_arr)
            ind = np.argmax(result)
            pred_class = CLASSES[ind]
            
        return jsonify({
            'success': True,
            'prediction': pred_class,
            'image_url': url_for('static', filename=f"uploads/{unique_name}")
        })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
