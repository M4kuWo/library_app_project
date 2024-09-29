from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models import Loan
from ...database import get_db 

loan_routes_bp = Blueprint('loan_routes', __name__)

@loan_routes_bp.route('/loans', methods=['POST'])
def create_loan():
    data = request.json
    new_loan = Loan(
        id=None,
        book_id=data['book_id'],
        user_id=data['user_id'],
        loan_date=data['loan_date'],
        return_date=None,
        hidden=False
    )
    db: Session = next(get_db())
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return jsonify({"message": "Loan created successfully"}), 201

@loan_routes_bp.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    db: Session = next(get_db())
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan:
        return jsonify({
            "id": loan.id,
            "book_id": loan.book_id,
            "user_id": loan.user_id,
            "loan_date": loan.loan_date,
            "return_date": loan.return_date,
            "hidden": loan.hidden
        }), 200
    return jsonify({"error": "Loan not found"}), 404

@loan_routes_bp.route('/loans', methods=['GET'])
def get_all_loans():
    db: Session = next(get_db())
    loans = db.query(Loan).filter(Loan.hidden == False).all()
    loans_list = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "user_id": loan.user_id,
            "loan_date": loan.loan_date,
            "return_date": loan.return_date,
            "hidden": loan.hidden
        } for loan in loans
    ]
    return jsonify(loans_list), 200

@loan_routes_bp.route('/loans/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    data = request.json
    db: Session = next(get_db())
    updated_loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not updated_loan:
        return jsonify({"error": "Loan not found"}), 404

    updated_loan.book_id = data['book_id']
    updated_loan.user_id = data['user_id']
    updated_loan.loan_date = data['loan_date']
    updated_loan.return_date = data.get('return_date')
    updated_loan.hidden = data.get('hidden', False)

    db.commit()
    return jsonify({"message": "Loan updated successfully"}), 200

@loan_routes_bp.route('/loans/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    db: Session = next(get_db())
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    loan.hidden = True  # Soft delete
    db.commit()
    return jsonify({"message": "Loan hidden successfully"}), 200
