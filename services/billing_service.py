from datetime import datetime
from config.extensions import db
from models.establishment import Establishment, SaaSBilledTo
from models.finance import SaaSInvoice, SaaSInvoiceStatus, Invoice, ExpenseType, PaymentMethod
from models.saas_config import SubscriptionPlan
from services.upload_service import UploadService

class BillingService:
    @staticmethod
    def generate_monthly_invoices():
        """
        Generates SaaS invoices for all establishments with an active plan.
        Should be called by a monthly cron job.
        """
        establishments = Establishment.query.filter(Establishment.subscription_plan_id.isnot(None)).all()

        generated_count = 0

        for est in establishments:
            # Prevent duplicate billing for the current month
            if BillingService._is_invoiced_this_month(est.id):
                continue

            plan = est.subscription_plan
            if not plan or not plan.is_active:
                continue

            amount = plan.price_monthly

            # Create SaaS Invoice (Debt of Establishment to Platform)
            saas_invoice = SaaSInvoice(
                establishment_id=est.id,
                amount=amount,
                status=SaaSInvoiceStatus.UNPAID,
                payment_method=None, # Will be set upon payment
                created_at=datetime.utcnow()
            )
            db.session.add(saas_invoice)

            # Logic based on who pays
            if est.saas_billed_to == SaaSBilledTo.TENANTS:
                # CAS 2: Tenants Pay -> Add as internal Expense so it splits among them.
                # "Le prix du plan est divisé par le nombre de chambres occupées" -> Managed by CostCalculator via Expense.

                internal_invoice = Invoice(
                    establishment_id=est.id,
                    type=ExpenseType.SAAS,
                    amount=amount,
                    date=datetime.utcnow().date(),
                    description=f"Abonnement RentPilot ({plan.name})"
                )
                db.session.add(internal_invoice)

            generated_count += 1

        db.session.commit()
        return generated_count

    @staticmethod
    def handle_offline_payment(invoice_id, proof_file):
        """
        Handles offline payment proof upload for a SaaS Invoice.
        :param invoice_id: ID of the SaaSInvoice
        :param proof_file: FileStorage object
        """
        invoice = SaaSInvoice.query.get(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")

        # Save proof
        file_path = UploadService.save_file(proof_file, subfolder='saas_proofs')

        invoice.status = SaaSInvoiceStatus.OFFLINE_PENDING
        invoice.proof_file_path = file_path
        invoice.payment_method = PaymentMethod.OFFLINE

        db.session.commit()
        return invoice

    @staticmethod
    def _is_invoiced_this_month(establishment_id):
        today = datetime.utcnow()
        # Simple check: created_at in current month/year
        # Ideally we check specifically for this "period", but strictly monthly cron implies date check is enough.

        # Postgres/SQLAlchemy extract
        # To be DB agnostic or simple, let's query with a range.
        start_of_month = datetime(today.year, today.month, 1)

        # We assume invoices are generated for "this month"
        return SaaSInvoice.query.filter(
            SaaSInvoice.establishment_id == establishment_id,
            SaaSInvoice.created_at >= start_of_month
        ).first() is not None
