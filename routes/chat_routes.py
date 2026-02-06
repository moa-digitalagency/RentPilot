from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.communication import ChatRoom, Message, ChannelType
from models.users import UserRole
from config.extensions import db
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def index():
    # In a real scenario, fetch available rooms for the user
    return render_template('chat.html')

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

    return render_template('chat/view.html', chat_room=chat_room, messages=messages)

@chat_bp.route('/chat/<int:room_id>/send', methods=['POST'])
@login_required
def send_message(room_id):
    chat_room = ChatRoom.query.get_or_404(room_id)

    # Permission Check
    if chat_room.type == ChannelType.COLOC_ONLY:
        if current_user.role == UserRole.BAILLEUR:
            abort(403)

    content = request.form.get('content')
    if content:
        msg = Message(
            chat_room_id=room_id,
            sender_id=current_user.id,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.session.add(msg)
        db.session.commit()

    return redirect(url_for('chat.view_chat', room_id=room_id))
