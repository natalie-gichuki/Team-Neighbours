from flask import Blueprint, request, jsonify
from app import db
from app.models.fines import Fine
from flasgger.utils import swag_from
from app.utils.auth_helpers import role_required

fine_bp = Blueprint('fine', __name__) 

@fine_bp.route('/fine', methods=['POST'])
@swag_from({
    'tags': ['Fine'],
    'description': 'Record fine for a member',
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
            'description': 'Fine recorded successfully',
            'examples': {
                'application/json': {
                    'msg': 'Fine recorded successfully'
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
def record_fine():    
    data = request.get_json()

    # Basic validation to avoid KeyError
    member_id = data.get('member_id')
    date = data.get('date')
    amount = data.get('amount')

    if not member_id or not date or not amount:
        return jsonify({"msg": "Missing required fields: member_id, date, or amount"}), 400

    # Create a new Fine record
    fine = Fine(member_id=member_id, date=date, amount=amount)

    db.session.add(fine)
    db.session.commit()

    return jsonify({"msg": "Fine recorded successfully"}), 201

@fine_bp.route('/fine/<int:member_id>', methods=['GET'])
@swag_from({
    'tags': ['Fine'],
    'description': 'Get fine records for a member',
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
            'description': 'Fine records retrieved successfully',
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
def get_fine_records(member_id):
    # Query the Fine records for the specified member_id
    fines = Fine.query.filter_by(member_id=member_id).all()

    if not fines:
        return jsonify({"msg": "No fine records found for this member"}), 404

    return jsonify([fine.to_dict() for fine in fines]), 200

# Get all fines
@fine_bp.route('/fines', methods=['GET'])
@swag_from({
    'tags': ['Fine'],
    'description': 'Get all fine records',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Fine records retrieved successfully',
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
def get_all_fines():
    # Query all Fine records
    fines = Fine.query.all()

    return jsonify([fine.to_dict() for fine in fines]), 200

# Edit a fine
@fine_bp.route('/fine/<int:fine_id>', methods=['PUT'])
@swag_from({
    'tags': ['Fine'],
    'description': 'Edit a fine record',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'fine_id',
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
            'description': 'Fine record updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Fine record updated successfully'
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
            'description': 'Fine not found',
            'examples': {
                'application/json': {
                    'msg': 'Fine not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def edit_fine(fine_id):   
    data = request.get_json()

    fine = Fine.query.get(fine_id)

    if not fine:
        return jsonify({"msg": "Fine not found"}), 404

    member_id = data.get('member_id')
    date = data.get('date')
    amount = data.get('amount')

    if member_id:
        fine.member_id = member_id
    if date:
        fine.date = date
    if amount:
        fine.amount = amount

    db.session.commit()

    return jsonify({"msg": "Fine record updated successfully"}), 200


# Delete a fine
@fine_bp.route('/fine/<int:fine_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Fine'],
    'description': 'Delete a fine record',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'fine_id',
            'in': 'path',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        200: {
            'description': 'Fine record deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Fine record deleted successfully'
                }
            }
        },
        404: {
            'description': 'Fine not found',
            'examples': {
                'application/json': {
                    'msg': 'Fine not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def delete_fine(fine_id):
    fine = Fine.query.get(fine_id)

    if not fine:
        return jsonify({"msg": "Fine not found"}), 404

    db.session.delete(fine)
    db.session.commit()

    return jsonify({"msg": "Fine record deleted successfully"}), 200