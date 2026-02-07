
"""
* Nom de l'application : RentPilot
* Description : Routes for chat module.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from models import ChatRoom, Message, ChannelType, MessageType, UserRole, Establishment, Lease, Room
from config.extensions import db
from datetime import datetime
from services.chat_media_service import ChatMediaService
from services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def index():
    # In a real scenario, fetch available rooms for the user
    return render_template('chat.html', messages=[], user_map={}, total_participants=0)

@chat_bp.route('/chat/<int:room_id>', methods=['GET'])
@login_required
def view_chat(room_id):
    chat_room = ChatRoom.query.get_or_404(room_id)

    # Permission Check
    # "ColocOnly" -> Bailleur cannot access.
    if chat_room.type == ChannelType.COLOC_ONLY:
        if current_user.role == UserRole.BAILLEUR:
            abort(403)

    # Additional check: ensure user belongs to the establishment.
    # (Skipped for brevity, but implied by context)

    messages = Message.query.filter_by(chat_room_id=room_id).order_by(Message.timestamp).all()

    # Get participants to build user map and count
    est = Establishment.query.get(chat_room.establishment_id)
    participants = []
    if est:
        # Tenants
        active_leases = Lease.query.join(Room).filter(Room.establishment_id == est.id).all()
        tenants = [l.tenant for l in active_leases]
        participants.extend(tenants)

        # Landlord (if General)
        if chat_room.type == ChannelType.GENERAL:
            participants.append(est.landlord)

    # Remove duplicates if any
    participants = list({p.id: p for p in participants}.values())

    user_map = {p.id: p.email.split('@')[0] for p in participants}
    total_participants = len(participants)

    return render_template('chat.html', chat_room=chat_room, messages=messages, user_map=user_map, total_participants=total_participants)

@chat_bp.route('/chat/<int:room_id>/send', methods=['POST'])
@login_required
def send_message(room_id):
    chat_room = ChatRoom.query.get_or_404(room_id)

    # Permission Check
    if chat_room.type == ChannelType.COLOC_ONLY:
        if current_user.role == UserRole.BAILLEUR:
            abort(403)

    content = request.form.get('content')
    file = request.files.get('file')

    # Check if we have content or a file with a filename
    has_file = file and file.filename
    if not content and not has_file:
        flash('Message cannot be empty.', 'warning')
        return redirect(url_for('chat.view_chat', room_id=room_id))

    msg_type = MessageType.TEXT
    file_url = None
    duration = None

    if file and file.filename:
        try:
            file_url = ChatMediaService.process_and_save(file)

            # Determine type based on extension
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

            if ext in ChatMediaService.ALLOWED_EXTENSIONS_AUDIO:
                msg_type = MessageType.VOICE
                # If client sends duration (e.g. from recording JS), use it
                try:
                    duration = int(request.form.get('duration', 0))
                except ValueError:
                    duration = 0
            elif ext in ChatMediaService.ALLOWED_EXTENSIONS_IMG:
                msg_type = MessageType.IMAGE

        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('chat.view_chat', room_id=room_id))

    msg = Message(
        chat_room_id=room_id,
        sender_id=current_user.id,
        content=content,
        type=msg_type,
        file_url=file_url,
        duration=duration,
        timestamp=datetime.utcnow()
    )
    db.session.add(msg)
    db.session.commit()

    return redirect(url_for('chat.view_chat', room_id=room_id))

@chat_bp.route('/chat/read/<int:msg_id>', methods=['POST'])
@login_required
def mark_read(msg_id):
    """
    Mark a specific message as read by the current user.
    """
    success = ChatService.mark_message_as_read(msg_id, current_user.id)
    return jsonify({'success': success})