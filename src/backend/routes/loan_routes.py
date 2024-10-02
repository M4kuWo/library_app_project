from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from ..models import Loan, Book, User
from ...database import get_db
from datetime import datetime

loan_routes_bp = Blueprint('loan_routes', __name__)

@loan_routes_bp.route('/', methods=['POST'])
def create_loan():
    data = request.json
    required_fields = ['book_id', 'user_id', 'loan_date']

    # Validate required fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    db: Session = next(get_db())

    # Check if book_id exists
    book_exists = db.query(Book).filter(Book.id == data['book_id']).first()
    if not book_exists:
        return jsonify({"error": f"Book ID {data['book_id']} does not exist"}), 400

    # Check if user_id exists
    user_exists = db.query(User).filter(User.id == data['user_id']).first()
    if not user_exists:
        return jsonify({"error": f"User ID {data['user_id']} does not exist"}), 400

    new_loan = Loan(
        book_id=data['book_id'],
        user_id=data['user_id'],
        loan_date=data['loan_date'],
        expected_return_date=None,  # Default to None if not provided
        actual_return_date=None,  # Default to None if not provided
        hidden=False
    )
    
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return jsonify({"message": "Loan created successfully"}), 201

@loan_routes_bp.route('//<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    db: Session = next(get_db())
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan:
        return jsonify({
            "id": loan.id,
            "book_id": loan.book_id,
            "user_id": loan.user_id,
            "loan_date": loan.loan_date,
            "expected_return_date": loan.expected_return_date,
            "actual_return_date": loan.actual_return_date or "Not yet returned",  # Provide default message
            "hidden": loan.hidden
        }), 200
    return jsonify({"error": "Loan not found"}), 404

@loan_routes_bp.route('/', methods=['GET'])
def get_all_loans():
    db: Session = next(get_db())
    loans = db.query(Loan).filter(Loan.hidden == False).all()
    loans_list = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "user_id": loan.user_id,
            "loan_date": loan.loan_date,
            "expected_return_date": loan.expected_return_date,
            "actual_return_date": loan.actual_return_date or "Not yet returned",  # Provide default message
            "hidden": loan.hidden
        } for loan in loans
    ]
    return jsonify(loans_list), 200

@loan_routes_bp.route('/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    data = request.json
    db: Session = next(get_db())
    updated_loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not updated_loan:
        return jsonify({"error": "Loan not found"}), 404

    # Check if book_id exists if provided
    if 'book_id' in data:
        book_exists = db.query(Book).filter(Book.id == data['book_id']).first()
        if not book_exists:
            return jsonify({"error": f"Book ID {data['book_id']} does not exist"}), 400
        updated_loan.book_id = data['book_id']

    # Check if user_id exists if provided
    if 'user_id' in data:
        user_exists = db.query(User).filter(User.id == data['user_id']).first()
        if not user_exists:
            return jsonify({"error": f"User ID {data['user_id']} does not exist"}), 400
        updated_loan.user_id = data['user_id']

    updated_loan.loan_date = data.get('loan_date', updated_loan.loan_date)
    updated_loan.expected_return_date = data.get('expected_return_date', updated_loan.expected_return_date)
    updated_loan.actual_return_date = data.get('actual_return_date', updated_loan.actual_return_date)
    updated_loan.hidden = data.get('hidden', updated_loan.hidden)

    db.commit()
    return jsonify({"message": "Loan updated successfully"}), 200

@loan_routes_bp.route('/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    db: Session = next(get_db())
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    loan.hidden = True  # Soft delete
    db.commit()
    return jsonify({"message": "Loan hidden successfully"}), 200

@loan_routes_bp.route('/bulk', methods=['POST'])
def bulk_create_loans():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of loans"}), 400

    db: Session = next(get_db())
    created_loans = []

    for loan_data in data:
        try:
            # Validate required fields
            required_fields = ['book_id', 'user_id', 'loan_date']
            for field in required_fields:
                if field not in loan_data:
                    return jsonify({"error": f"Missing field: {field} in one of the loan entries"}), 400
            
            # Check if book_id exists
            book_exists = db.query(Book).filter(Book.id == loan_data['book_id']).first()
            if not book_exists:
                return jsonify({"error": f"Book ID {loan_data['book_id']} does not exist"}), 400
            
            # Check if user_id exists
            user_exists = db.query(User).filter(User.id == loan_data['user_id']).first()
            if not user_exists:
                return jsonify({"error": f"User ID {loan_data['user_id']} does not exist"}), 400

            new_loan = Loan(
                book_id=loan_data['book_id'],
                user_id=loan_data['user_id'],
                loan_date=loan_data['loan_date'],
                expected_return_date=loan_data.get('expected_return_date'),  # Default to None if not provided
                actual_return_date=loan_data.get('actual_return_date'),  # Default to None if not provided
                hidden=False
            )
            
            db.add(new_loan)
            db.commit()  # Commit to save the new loan in the database
            db.refresh(new_loan)  # Refresh to get the new loan ID and any defaults
            
            created_loans.append({
                "id": new_loan.id,
                "book_id": new_loan.book_id,
                "user_id": new_loan.user_id,
                "loan_date": new_loan.loan_date,
                "expected_return_date": new_loan.expected_return_date,
                "actual_return_date": new_loan.actual_return_date or "Not yet returned",  # Provide default message
                "hidden": new_loan.hidden
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Loans created successfully", "loans": created_loans}), 201

@loan_routes_bp.route('/bulk', methods=['DELETE'])
def bulk_delete_loans():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Request body must be a list of loan IDs"}), 400

    db: Session = next(get_db())
    deleted_loans = []

    for loan_id in data:
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if loan:
            loan.hidden = True  # Soft delete
            deleted_loans.append(loan_id)

    db.commit()

    return jsonify({"message": "Loans hidden successfully", "deleted_loans": deleted_loans}), 200

@loan_routes_bp.route('/loans/<int:loan_id>/return', methods=['PUT'])
def return_loan(loan_id):
    db: Session = next(get_db())
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    
    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    # Update the actual_return_date to current datetime
    loan.actual_return_date = datetime.now()
    
    db.commit()
    return jsonify({"message": "Loan returned successfully", "actual_return_date": loan.actual_return_date}), 200
