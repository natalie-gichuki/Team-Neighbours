from flask import Blueprint, request, jsonify
from app import db
from app.models.attendance import Attendance
from flasgger.utils import swag_from
from app.utils.auth_helpers import role_required

attendance_bp = Blueprint('attendance', __name__) 

@attendance_bp.route('/attendance', methods=['POST'])
@swag_from({
    'tags': ['Attendance'],
    'description': 'Record attendance for a member',
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
                    'status': {'type': 'string', 'enum': ['present', 'absent', 'late']}
                },
                'required': ['member_id', 'date', 'status']
            }

        }
    ],
    'responses': {
        201: {
            'description': 'Attendance recorded successfully',
            'examples': {
                'application/json': {
                    'msg': 'Attendance recorded successfully'
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
def record_attendance():    
    data = request.get_json()

    # Basic validation to avoid KeyError
    member_id = data.get('member_id')
    date = data.get('date')
    status = data.get('status')

    if not member_id or not date or not status:
        return jsonify({"msg": "Missing required fields: member_id, date, or status"}), 400

    # Create a new Attendance record
    attendance = Attendance(member_id=member_id, date=date, status=status)

    db.session.add(attendance)
    db.session.commit()

    return jsonify({"msg": "Attendance recorded successfully"}), 201

@attendance_bp.route('/attendance/<int:member_id>', methods=['GET'])
@swag_from({
    'tags': ['Attendance'],
    'description': 'Get attendance records for a member',
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
            'description': 'Attendance records retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'member_id': {'type': 'integer'},
                        'date': {'type': 'string', 'format': 'date'},
                        'status': {'type': 'string'}
                    }
                }
            },
            'examples': {
                'application/json': [
                    {
                        'id': 1,
                        'member_id': 1,
                        'date': '2023-10-01',
                        'status': 'present'
                    },
                    {
                        'id': 2,
                        'member_id': 1,
                        'date': '2023-10-02',
                        'status': 'absent'
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
    # Query the Attendance records for the specified member_id
    attendances = Attendance.query.filter_by(member_id=member_id).all()

    if not attendances:
        return jsonify({"msg": "No attendance records found for this member"}), 404

    return jsonify([attendance.to_dict() for attendance in attendances]), 200
