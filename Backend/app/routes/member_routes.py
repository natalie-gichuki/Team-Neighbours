from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.members import Member
from app.utils.auth_helpers import role_required
from app import db
from flasgger.utils import swag_from

member_bp = Blueprint('member_routes', __name__)

@member_bp.route('/member', methods=['GET'])
@jwt_required()
@role_required('admin')
@swag_from({
    'tags': ['Member'],
    'description': 'List all members excluding disabled accounts',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'List of members',
            'examples': {
                'application/json': [
                    {"id": 1, "name": "john_doe", "email": "john@example.com", "role": "customer"}
                ]
            }
        }
    }
})
def get_members():
    members = Member.query.filter(Member.role != 'disabled').all()

    if not members:
        return jsonify({"msg": "No members found"}), 404

    return jsonify([{
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "role": member.role
    } for member in members]), 200

@member_bp.route('/member/<int:member_id>', methods=['GET'])
@jwt_required()
@role_required('admin', 'member') # Only admin can view member details
@swag_from({    
    'tags': ['Member'],
    'description': 'Get member details by ID',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'member_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID of the member to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Member details retrieved successfully',
            'examples': {
                'application/json': {
                    "id": 1,
                    "name": "john_doe",
                    "email": "john@example.com",
                    "role": "customer"
                }
            }
        }
    }
})
def get_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"msg": "Member not found"}), 404

    return jsonify({
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "role": member.role
    }), 200




@member_bp.route('/member/<int:member_id>/disabled', methods=['PATCH'])
@jwt_required()
@role_required('admin')
@swag_from({
    'tags': ['Member'],
    'description': 'Disable a member account',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'member_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID of the member to disable'
        }
    ],
    'responses': {
        200: {
            'description': 'Member account disabled successfully',
            'examples': {
                'application/json': {
                    "msg": "Member account disabled"
                }
            }
        },
        404: {
            'description': 'Member not found',
            'examples': {
                'application/json': {
                    "msg": "Member not found"
                }
            }
        },
        403: {
            'description': 'Forbidden - Cannot disable admin member',
            'examples': {
                'application/json': {
                    "msg": "Cannot disable an admin member"
                }
            }
        }
    }
})
def disable_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"msg": "Member not found"}), 404

    if member.role == 'admin':
        return jsonify({"msg": "Cannot disable an admin member"}), 403

    member.role = 'disabled'
    db.session.commit()
    return jsonify({"msg": f"Member {member.name} disabled"}), 200


@member_bp.route('/members/disabled', methods=['GET'])
@jwt_required()
@role_required('admin')
@swag_from({
    'tags': ['Member'],
    'description': 'Get all disabled member accounts',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'List of disabled members',
            'examples': {
                'application/json': [
                    {
                        "id": 3,
                        "name": "johndoe",
                        "email": "john@example.com",
                        "role": "disabled"
                    }
                ]
            }
        }
    }
})
def get_disabled_members():
    disabled_members = Member.query.filter_by(role='disabled').all()
    result = [
        {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "role": member.role
        }
        for member in disabled_members
    ]
    return jsonify(result), 200

@member_bp.route('/member/<int:member_id>/enable', methods=['PATCH'])
@jwt_required()
@role_required('admin')
@swag_from({
    'tags': ['Member'],
    'description': 'Enable a disabled member account',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'member_id',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID of the member to enable'
        }
    ],
    'responses': {
        200: {
            'description': 'User account enabled successfully',
            'examples': {
                'application/json': {
                    "msg": "User account enabled"
                }
            }
        },
        404: {
            'description': 'User not found',
            'examples': {
                'application/json': {
                    "msg": "User not found"
                }
            }
        },
        403: {
            'description': 'Forbidden - Cannot enable admin user',
            'examples': {
                'application/json': {
                    "msg": "Cannot enable an admin user"
                }
            }
        }
    }
})
def enable_member(member_id):
    member = Member.query.get(member_id)
    if not member:
        return jsonify({"msg": "Member not found"}), 404

    if member.role == 'admin':
        return jsonify({"msg": "Cannot enable an admin member"}), 403

    member.role = 'customer'
    db.session.commit()
    return jsonify({"msg": f"Member {member.username} enabled"}), 200