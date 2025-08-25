from app import db

class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    member = db.relationship('Member', back_populates='attendances')

    def __repr__(self):
        return f'<Attendance {self.id} - Member {self.member_id} on {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'date': self.date,
            'status': self.status
        }