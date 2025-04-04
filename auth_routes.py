from flask import Blueprint, request, jsonify
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
            
        # Créer l'utilisateur dans notre base de données
        new_user = User(
            email=email,
            password_hash=password,  # Dans un vrai système, utilisez un hash
            name=data.get('name', 'Utilisateur')
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'Utilisateur créé avec succès', 'id': new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email et mot de passe requis'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.password_hash == data['password']:  # Use proper password hashing in production
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name
        }), 200
    
    return jsonify({'error': 'Email ou mot de passe incorrect'}), 401