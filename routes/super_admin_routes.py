from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app, send_file
from flask_login import login_required, current_user
from security.auth import super_admin_required
from models import PlatformSettings, SubscriptionPlan, SaaSInvoice, SaaSInvoiceStatus, PaymentMethod, User, Establishment, Announcement, AnnouncementSenderType, AnnouncementTargetAudience, AnnouncementPriority
from models.saas_config import ReceiptFormat
from services.pdf_service import PDFService
from config.extensions import db
from datetime import datetime
import json

super_admin_bp = Blueprint('super_admin', __name__, url_prefix='/admin')

@super_admin_bp.before_request
@super_admin_required
def check_super_admin():
    """Ensure all routes in this blueprint are protected."""
    pass

@super_admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # Stats
    total_revenue = db.session.query(db.func.sum(SaaSInvoice.amount)).filter(SaaSInvoice.status == SaaSInvoiceStatus.PAID).scalar() or 0.0
    total_users = User.query.count()
    total_establishments = Establishment.query.count()

    return render_template('admin/dashboard.html',
                           total_revenue=total_revenue,
                           total_users=total_users,
                           total_establishments=total_establishments)

@super_admin_bp.route('/stats/export', methods=['GET'])
def export_stats():
    # Default to current year
    now = datetime.utcnow()
    start_date = datetime(now.year, 1, 1)
    end_date = now

    pdf_buffer = PDFService.generate_admin_stats_pdf((start_date, end_date))

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"admin_stats_{now.strftime('%Y%m%d')}.pdf",
        mimetype='application/pdf'
    )

@super_admin_bp.route('/settings/receipts', methods=['POST'])
def update_receipt_settings():
    settings = PlatformSettings.query.first()
    if not settings:
        settings = PlatformSettings()
        db.session.add(settings)

    receipt_format = request.form.get('receipt_format')
    whatsapp = request.form.get('whatsapp_contact_number')

    if receipt_format:
        try:
            settings.receipt_format = ReceiptFormat(receipt_format)
        except ValueError:
            flash('Invalid receipt format.', 'error')
            return redirect(url_for('super_admin.settings_view'))

    settings.whatsapp_contact_number = whatsapp
    db.session.commit()

    flash('Receipt settings updated.', 'success')
    return redirect(url_for('super_admin.settings_view'))

@super_admin_bp.route('/settings', methods=['GET'])
def settings_view():
    settings = PlatformSettings.query.first()
    if not settings:
        settings = PlatformSettings()
        db.session.add(settings)
        db.session.commit()
    return render_template('admin/settings.html', site_settings=settings)

@super_admin_bp.route('/settings', methods=['POST'])
def update_settings():
    settings = PlatformSettings.query.first()
    if not settings:
        settings = PlatformSettings()
        db.session.add(settings)

    settings.app_name = request.form.get('app_name', settings.app_name)
    settings.logo_url = request.form.get('logo_url', settings.logo_url)
    settings.primary_color_hex = request.form.get('primary_color_hex', settings.primary_color_hex)
    settings.secondary_color_hex = request.form.get('secondary_color_hex', settings.secondary_color_hex)
    settings.timezone = request.form.get('timezone', settings.timezone)
    settings.seo_title_template = request.form.get('seo_title_template', settings.seo_title_template)
    settings.seo_meta_desc = request.form.get('seo_meta_desc', settings.seo_meta_desc)

    # Handle maintenance mode checkbox (if not present, it's False)
    settings.is_maintenance_mode = request.form.get('is_maintenance_mode') == 'true'

    db.session.commit()
    flash('Settings updated successfully.', 'success')
    return redirect(url_for('super_admin.settings_view'))

@super_admin_bp.route('/plans', methods=['GET'])
def plans_view():
    plans = SubscriptionPlan.query.all()
    return render_template('admin/plans.html', plans=plans)

@super_admin_bp.route('/plans', methods=['POST'])
def manage_plans():
    plan_id = request.form.get('plan_id')
    name = request.form.get('name')
    price = request.form.get('price_monthly')
    currency = request.form.get('currency', 'EUR')
    features_str = request.form.get('features_json', '{}')

    try:
        features_json = json.loads(features_str)
        price_val = float(price)
    except json.JSONDecodeError:
        flash('Invalid JSON for features.', 'error')
        return redirect(url_for('super_admin.plans_view'))
    except (ValueError, TypeError):
        flash('Invalid price format.', 'error')
        return redirect(url_for('super_admin.plans_view'))

    if plan_id:
        plan = SubscriptionPlan.query.get(plan_id)
        if plan:
            plan.name = name
            plan.price_monthly = price_val
            plan.currency = currency
            plan.features_json = features_json
            flash('Plan updated.', 'success')
    else:
        new_plan = SubscriptionPlan(
            name=name,
            price_monthly=price_val,
            currency=currency,
            features_json=features_json,
            is_active=True
        )
        db.session.add(new_plan)
        flash('Plan created.', 'success')

    db.session.commit()
    return redirect(url_for('super_admin.plans_view'))

@super_admin_bp.route('/invoices', methods=['GET'])
def list_invoices():
    status_filter = request.args.get('status')
    query = SaaSInvoice.query

    if status_filter == 'offline_pending':
        query = query.filter(SaaSInvoice.status == SaaSInvoiceStatus.OFFLINE_PENDING)

    invoices = query.order_by(SaaSInvoice.created_at.desc()).all()
    return render_template('admin/invoices_review.html', invoices=invoices)

@super_admin_bp.route('/invoices/<int:invoice_id>/approve', methods=['POST'])
def approve_invoice(invoice_id):
    invoice = SaaSInvoice.query.get_or_404(invoice_id)

    if invoice.status == SaaSInvoiceStatus.OFFLINE_PENDING:
        invoice.status = SaaSInvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        db.session.commit()
        flash(f'Invoice #{invoice.id} approved.', 'success')
    else:
        flash(f'Invoice #{invoice.id} is not pending approval.', 'warning')

    return redirect(url_for('super_admin.list_invoices'))

@super_admin_bp.route('/announce', methods=['POST'])
def send_announcement():
    title = request.form.get('title')
    content = request.form.get('content')
    target = request.form.get('target_audience') # 'All_Users' or 'Specific_Establishment'
    establishment_id = request.form.get('establishment_id')
    priority_val = request.form.get('priority', 'Normal')

    if not title or not content:
        flash('Title and content are required.', 'error')
        return redirect(url_for('super_admin.dashboard'))

    try:
        target_enum = AnnouncementTargetAudience(target) if target else AnnouncementTargetAudience.ALL_USERS
        priority_enum = AnnouncementPriority(priority_val)
    except ValueError:
        flash('Invalid target audience or priority.', 'error')
        return redirect(url_for('super_admin.dashboard'))

    announcement = Announcement(
        sender_type=AnnouncementSenderType.SUPER_ADMIN,
        target_audience=target_enum,
        title=title,
        content=content,
        priority=priority_enum
    )

    if target_enum == AnnouncementTargetAudience.SPECIFIC_ESTABLISHMENT and establishment_id:
        try:
            announcement.establishment_id = int(establishment_id)
        except (ValueError, TypeError):
            flash('Invalid establishment ID.', 'error')
            return redirect(url_for('super_admin.dashboard'))

    db.session.add(announcement)
    db.session.commit()

    flash('Announcement sent.', 'success')
    return redirect(url_for('super_admin.dashboard'))
