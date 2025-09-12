from flask import Blueprint, request, jsonify
from app import db
from app.models.contribution import Contribution
from flasgger.utils import swag_from
from app.utils.auth_helpers import role_required

contribution_bp = Blueprint('contribution', __name__) 

@contribution_bp.route('/contribution', methods=['POST'])
@swag_from({
    'tags': ['Contribution'],
    'description': 'Record contribution for a member',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'member_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number', 'format': 'float'}
                },
                'required': ['member_id', 'date', 'amount']
            }

        }
    ],
    'responses': {
        201: {
            'description': 'Contribution recorded successfully',
            'examples': {
                'application/json': {
                    'msg': 'Contribution recorded successfully'
                }
            }
        },
        400: {
            'description': 'Bad Request',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields or invalid data'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def record_contribution():    
    data = request.get_json()

    # Basic validation to avoid KeyError
    member_id = data.get('member_id')
    date = data.get('date')
    amount = data.get('amount')

    if not member_id or not date or not amount:
        return jsonify({"msg": "Missing required fields: member_id, date, or amount"}), 400

    # Create a new Contribution record
    contribution = Contribution(member_id=member_id, date=date, amount=amount)

    db.session.add(contribution)
    db.session.commit()

    return jsonify({"msg": "Contribution recorded successfully"}), 201

@contribution_bp.route('/contribution/<int:member_id>', methods=['GET'])
@swag_from({
    'tags': ['Contribution'],
    'description': 'Get contribution records for a member',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'member_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        200: {
            'description': 'Contribution records retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'member_id': {'type': 'integer'},
                        'date': {'type': 'string', 'format': 'date'},
                        'amount': {'type': 'number', 'format': 'float'}
                    }
                }
            },
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'member_id': 1,
                        'date': '2023-10-01',
                        'amount': 100.00
                    },
                    {
                        'id': 2,
                        'member_id': 1,
                        'date': '2023-10-02',
                        'amount': 150.75
                    }
                ]
            }
        },
        404: {
            'description': 'Member not found',
            'examples': {
                'application/json': {
                    'msg': 'Member not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary', 'member')
def get_attendance(member_id):
    # Query the Contribution records for the specified member_id
    contributions = Contribution.query.filter_by(member_id=member_id).all()

    if not contributions:
        return jsonify({"msg": "No contribution records found for this member"}), 404

    return jsonify([contribution.to_dict() for contribution in contributions]), 200

# Get all contributions
@contribution_bp.route('/contributions', methods=['GET'])
@swag_from({
    'tags': ['Contribution'],
    'description': 'Get all contribution records',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Contribution records retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'member_id': {'type': 'integer'},
                        'date': {'type': 'string', 'format': 'date'},
                        'amount': {'type': 'number', 'format': 'float'}
                    }
                }
            },
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'member_id': 1,
                        'date': '2023-10-01',
                        'amount': 100.00
                    },
                    {
                        'id': 2,
                        'member_id': 1,
                        'date': '2023-10-02',
                        'amount': 150.75
                    }
                ]
            }
        }
    }
})
@role_required('admin', 'secretary')
def get_all_contributions():
    # Query all Contribution records
    contributions = Contribution.query.all()

    return jsonify([contribution.to_dict() for contribution in contributions]), 200

# Edit a contribution
@contribution_bp.route('/contribution/<int:contribution_id>', methods=['PUT'])
@swag_from({
    'tags': ['Contribution'],
    'description': 'Edit a contribution record',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'contribution_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'member_id': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'amount': {'type': 'number', 'format': 'float'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Contribution record updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Contribution record updated successfully'
                }
            }
        },
        400: {
            'description': 'Bad Request',
            'examples': {
                'application/json': {
                    'msg': 'Invalid data'
                }
            }
        },
        404: {
            'description': 'Contribution not found',
            'examples': {
                'application/json': {
                    'msg': 'Contribution not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def edit_contribution(contribution_id):   
    data = request.get_json()

    contribution = Contribution.query.get(contribution_id)

    if not contribution:
        return jsonify({"msg": "Contribution not found"}), 404

    member_id = data.get('member_id')
    date = data.get('date')
    amount = data.get('amount')

    if member_id:
        contribution.member_id = member_id
    if date:
        contribution.date = date
    if amount:
        contribution.amount = amount

    db.session.commit()

    return jsonify({"msg": "Contribution record updated successfully"}), 200


# Delete a contribution
@contribution_bp.route('/contribution/<int:contribution_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Contribution'],
    'description': 'Delete a contribution record',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'contribution_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        200: {
            'description': 'Contribution record deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Contribution record deleted successfully'
                }
            }
        },
        404: {
            'description': 'Contribution not found',
            'examples': {
                'application/json': {
                    'msg': 'Contribution not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def delete_contribution(contribution_id):
    contribution = Contribution.query.get(contribution_id)

    if not contribution:
        return jsonify({"msg": "Contribution not found"}), 404

    db.session.delete(contribution)
    db.session.commit()

    return jsonify({"msg": "Contribution record deleted successfully"}), 200