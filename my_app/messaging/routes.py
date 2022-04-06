from my_app.messaging.helper_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from my_app.messaging.forms import MessageForm, LookForUser
from my_app.models import User, Message
from my_app import db
from datetime import datetime


messaging_bp = Blueprint('message', __name__)


@messaging_bp.route('/send_message/<user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    """Route utilized to send messages to a specific user."""
    # If the user is trying to create a chat with themselves or the recipient does not exist
    if user_id == str(current_user.id) or User.query.get(user_id) is None:
        flash('Chat could not be established: user is trying to create a chat with an invalid user.')
        return redirect(url_for('message.view_messages'))

    chat, time_check_current_user = get_chat_and_time_check(user_id)
    form = MessageForm()
    if request.method == 'POST' and form.validate_on_submit():  # If message form is completed and validated.
        create_and_commit_message(form, user_id, chat.id)
        return redirect(url_for('message.send_message', user_id=user_id))

    # Get the chat messages, recipient user and update the time check of the chat by the current user
    chat_messages = Message.query.filter_by(chat_id=chat.id)
    recipient_user = User.query.get(user_id)
    time_check_current_user.time = datetime.now()  # Checked now
    db.session.commit()
    return render_template('send_message.html', form=form, messages=chat_messages, recipient=recipient_user,
                           unread_messages=check_if_unread())


@messaging_bp.route('/view_messages', methods=['GET', 'POST'])
@login_required
def view_messages():
    """Route used to view all the chats (with at least one messages) of the current user."""
    # Get the ordered information about the chats
    user_chats = get_user_chats()
    users, messages, unread_chats = get_chats_info(user_chats)
    users, messages, unread_chats = order_chats_info(users, messages, unread_chats)

    # Get the email of the available users for a chat (all the users except the current) and place them as
    # choices in LookForUser
    all_users = User.query.all()
    available_users = [("", "")] + [(f'{user.email}', f'{user.email}')
                                    for user in all_users if user.id != current_user.id]
    user_browser = LookForUser(user_choices=available_users)

    if request.method == 'POST' and user_browser.validate_on_submit():  # Open the chat with the selected user
        user_selected = User.query.filter_by(email=user_browser.user.data).first()
        return redirect(url_for('message.send_message', user_id=user_selected.id))

    return render_template('view_messages.html', users_and_messages_and_unreads=zip(users, messages, unread_chats),
                           form=user_browser, no_messages=check_if_no_messages(messages),
                           unread_messages=check_if_unread())
