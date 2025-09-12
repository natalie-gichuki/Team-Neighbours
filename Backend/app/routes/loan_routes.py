from flask import Blueprint, request, jsonify
from app import db
from app.models.loans import Loan
from flasgger.utils import swag_from
from app.utils.auth_helpers import role_required

loan_bp = Blueprint('loan', __name__) 

@loan_bp.route('/loan', methods=['POST'])
@swag_from({
    'tags': ['Loan'],
    'description': 'Record loan for a member',
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
            'description': 'Loan recorded successfully',
            'examples': {
                'application/json': {
                    'msg': 'Loan recorded successfully'
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

    # Create a new Loan record
    loan = Loan(member_id=member_id, date=date, amount=amount)

    db.session.add(loan)
    db.session.commit()

    return jsonify({"msg": "Loan recorded successfully"}), 201

@loan_bp.route('/loan/<int:member_id>', methods=['GET'])
@swag_from({
    'tags': ['Loan'],
    'description': 'Get loan records for a member',
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
            'description': 'Loan records retrieved successfully',
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
def get_loan_records(member_id):
    # Query the Fine records for the specified member_id
    loans = Loan.query.filter_by(member_id=member_id).all()

    if not loans:
        return jsonify({"msg": "No loans records found for this member"}), 404

    return jsonify([loan.to_dict() for loan in loans]), 200

# Get all loans
@loan_bp.route('/loans', methods=['GET'])
@swag_from({
    'tags': ['Loan'],
    'description': 'Get all loan records',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Loan records retrieved successfully',
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
def get_all_loans():
    # Query all Loan records
    loans = Loan.query.all()

    return jsonify([loan.to_dict() for loan in loans]), 200

# Edit a loan
@loan_bp.route('/loan/<int:loan_id>', methods=['PUT'])
@swag_from({
    'tags': ['Loan'],
    'description': 'Edit a loan record',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loan_id',
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
            'description': 'Loan record updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Loan record updated successfully'
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
            'description': 'Loan not found',
            'examples': {
                'application/json': {
                    'msg': 'Loan not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def edit_fine(loan_id):   
    data = request.get_json()

    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify({"msg": "Loan not found"}), 404

    member_id = data.get('member_id')
    date = data.get('date')
    amount = data.get('amount')

    if member_id:
        loan.member_id = member_id
    if date:
        loan.date = date
    if amount:
        loan.amount = amount

    db.session.commit()

    return jsonify({"msg": "Loan record updated successfully"}), 200


# Delete a loan
@loan_bp.route('/loan/<int:loan_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Loan'],
    'description': 'Delete a loan record',
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
            'description': 'Loan record deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Loan record deleted successfully'
                }
            }
        },
        404: {
            'description': 'Loan not found',
            'examples': {
                'application/json': {
                    'msg': 'Loan not found'
                }
            }
        }
    }
})
@role_required('admin', 'secretary')
def delete_loan(loan_id):
    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify({"msg": "Loan not found"}), 404

    db.session.delete(loan)
    db.session.commit()

    return jsonify({"msg": "Loan record deleted successfully"}), 200