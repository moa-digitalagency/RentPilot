from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from security.auth import bailleur_required, tenant_required
from models.users import UserRole
from models.finance import Invoice, Transaction, PaymentProof, ExpenseType, ValidationStatus
from models.establishment import Lease
from config.extensions import db
from services.upload_service import UploadService
from services.pdf_service import PDFService
from datetime import datetime
import io

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/finance/add-expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    # Only Tenant Responsable
    if current_user.role != UserRole.TENANT_RESPONSABLE:
        abort(403)

    if request.method == 'POST':
        # Need to identify establishment. Assume user has one active lease.
        lease = Lease.query.filter_by(user_id=current_user.id).first()
        if not lease:
            flash('No active lease found', 'error')
            return redirect(url_for('dashboard.dashboard'))

        establishment = lease.room.establishment

        amount = float(request.form.get('amount', 0))
        type_val = request.form.get('type') # EAU, ELEC, WIFI, TRAVAUX, LOYER
        description = request.form.get('description')

        try:
            expense_type = ExpenseType(type_val)
        except ValueError:
            flash('Invalid expense type', 'error')
            return redirect(url_for('finance.add_expense'))

        invoice = Invoice(
            establishment_id=establishment.id,
            type=expense_type,
            amount=amount,
            description=description,
            date=datetime.utcnow().date()
        )
        db.session.add(invoice)
        db.session.commit()

        flash('Expense added', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('finance/add_expense.html')

@finance_bp.route('/finance/upload-proof', methods=['POST'])
@login_required
@tenant_required
def upload_proof():
    # Typically this would be associated with a form where user enters amount
    # and maybe selects an invoice.

    invoice_id = request.form.get('invoice_id')
    amount_str = request.form.get('amount', '0')
    try:
        amount = float(amount_str)
    except ValueError:
        flash('Invalid amount', 'error')
        return redirect(url_for('dashboard.dashboard'))

    file = request.files.get('proof_file')

    if not file:
        flash('No file uploaded', 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Create Transaction
    transaction = Transaction(
        user_id=current_user.id,
        invoice_id=invoice_id if invoice_id else None,
        amount=amount,
        validation_status=ValidationStatus.PENDING
    )
    db.session.add(transaction)
    db.session.commit()

    # Upload File
    try:
        file_path = UploadService.save_file(file, 'proofs')

        proof = PaymentProof(
            transaction_id=transaction.id,
            file_path=file_path
        )
        db.session.add(proof)
        db.session.commit()
        flash('Payment proof uploaded', 'success')

    except Exception as e:
        db.session.delete(transaction)
        db.session.commit()
        flash(f'Upload failed: {str(e)}', 'error')

    return redirect(url_for('dashboard.dashboard'))

@finance_bp.route('/finance/validate-payment/<int:transaction_id>', methods=['POST'])
@login_required
@bailleur_required
def validate_payment(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # In a real app, verify landlord ownership here.

    action = request.form.get('action') # 'validate' or 'reject'

    if action == 'validate':
        transaction.validation_status = ValidationStatus.VALIDATED
        transaction.validation_date = datetime.utcnow()
    elif action == 'reject':
        transaction.validation_status = ValidationStatus.REJECTED

    db.session.commit()
    flash(f'Payment {action}d', 'success')
    return redirect(url_for('dashboard.dashboard'))

@finance_bp.route('/finance/receipt/<int:transaction_id>')
@login_required
def get_receipt(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    # Access control
    if transaction.user_id != current_user.id and current_user.role != UserRole.BAILLEUR:
         abort(403)

    # Prepare data for PDFService
    data = {
        'id': transaction.id,
        'user_name': transaction.payer.email,
        'user_id': transaction.user_id,
        'amount': transaction.amount,
        'date': transaction.date.strftime('%Y-%m-%d') if transaction.date else 'Unknown',
        'description': f"Payment for Invoice #{transaction.invoice_id}" if transaction.invoice_id else "General Payment",
        'property_name': "RentPilot Property"
    }

    if transaction.invoice and transaction.invoice.establishment:
        data['property_name'] = transaction.invoice.establishment.address
    elif transaction.payer.leases:
        # Best effort to find property name
        lease = transaction.payer.leases[0]
        if lease.room and lease.room.establishment:
            data['property_name'] = lease.room.establishment.address

    pdf_buffer = PDFService.generate_receipt(data)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f'receipt_{transaction.id}.pdf',
        mimetype='application/pdf'
    )
