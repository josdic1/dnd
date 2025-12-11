# server/demo_server.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
import datetime
import uuid
from functools import wraps

# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app) # Allow the frontend to talk to us
app.config['SECRET_KEY'] = 'demo-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='OPEN')
    requester_id = db.Column(db.String(36), db.ForeignKey('user.id'))

# --- HELPERS ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['sub'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(name=data['name'], phone=data['phone'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created!'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(phone=data['phone']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        token = jwt.encode({'sub': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Could not verify'}), 401

@app.route('/jobs', methods=['POST'])
@token_required
def create_job(current_user):
    data = request.get_json()
    new_job = Job(title=data['title'], price=float(data['price']), zip_code=data['zip_code'], requester_id=current_user.id)
    db.session.add(new_job)
    db.session.commit()
    return jsonify({'message': 'Job posted!'})

@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = Job.query.filter_by(status='OPEN').all()
    output = []
    for job in jobs:
        output.append({'id': job.id, 'title': job.title, 'price': job.price, 'zip': job.zip_code})
    return jsonify({'jobs': output})

# --- RUNNER ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Auto-create DB every time
    app.run(port=5556, debug=True)