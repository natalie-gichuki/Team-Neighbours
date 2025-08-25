from flask import Blueprint, request, jsonify
from app import db
from app.models.members import Member
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger.utils import swag_from

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new member',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                    'gender': {'type': 'string'},
                    'phone': {'type': 'string'},
                    'password': {'type': 'string'},
                    'role': {'type': 'string', 'default': 'customer'}
                },
                'required': ['username', 'email', 'password', 'gender', 'phone']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {
                    'msg': 'User registered successfully'
                }
            }
        },
        400: {
            'description': 'Bad Request',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields'
                }
            }
        }
    }
})

def register():
    data = request.get_json()

    # Basic validation to avoid KeyError
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    gender = data.get('gender')
    password = data.get('password')
    role = data.get('role', 'customer')

    if not username or not email or not password or not phone or not gender:
        return jsonify({"msg": "Missing required fields: username, email, password, phone, or gender"}), 400

    if Member.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = Member(
        username=username,
        email=email,
        phone=phone,
        gender=gender,
        password_hash=generate_password_hash(password),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'User login',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'examples': {
                'application/json': {
                    'access_token': '<JWT Token>'
                }
            }
        },
        401: {
            'description': 'Unauthorized',
            'examples': {
                'application/json': {
                    'msg': 'Invalid email or password'
                }
            }
        },
        403: {
            'description': 'Forbidden',
            'examples': {
                'application/json': {
                    'msg': "User account is disabled"
                }
            }
        }
    }
})
def login():
    data = request.get_json()
    user = Member.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"msg": "Invalid email or password"}), 401
    
    if user.role == 'disabled':
        return jsonify({"msg": "User account is disabled"}), 403

    access_token = create_access_token(
        identity=user.id,
        additional_claims={ "email": user.email, "role": user.role}  # Include user role in the token
    )
    return jsonify(access_token=access_token), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'description': 'Get user profile',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'User profile retrieved successfully',
            'examples': {
                'application/json': {
                    'id': 1,
                    'username': 'john_doe',
                    'email': 'john_doe@example.com',
                    'role': 'customer',
                    'phone': '123-456-7890',
                    'gender': 'male'
                }
            }
        },
        401: {
            'description': 'Unauthorized',
            'examples': {
                'application/json': {
                    'msg': 'Missing or invalid token'
                }
            }
        }
    }
})
def profile():
    user_id = get_jwt_identity()
    user = Member.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user:
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "gender": user.gender,
            "role": user.role
        }), 200