from app import db

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)

    member = db.relationship('Member', back_populates='loans')

    def __repr__(self):
        return f'<Loan {self.id} - Member {self.member_id} on {self.date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'amount': self.amount,
            'date': self.date
        }
