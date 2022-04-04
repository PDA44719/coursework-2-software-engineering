from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from my_app.messaging.forms import MessageForm, LookForUser
from my_app.models import User, Message, Chat, LastTimeChecked
from my_app import db
from sqlalchemy import desc
from datetime import datetime

messaging_bp = Blueprint('message', __name__)


def check_if_unread_chat(chat, time_check):
    last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()
    if last_message and last_message.post_time > time_check.time:
        return True
    else:
        return False


def check_if_unread():
    time_checks = LastTimeChecked.query.filter_by(user_id=current_user.id).all()
    for time_check in time_checks:
        chat = Chat.query.get(time_check.chat_id)
        if check_if_unread_chat(chat, time_check):
            return True

    return False


@messaging_bp.route('/send_message/<user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    if Chat.query.filter_by(user_1_id=current_user.id, user_2_id=user_id).first() is not None:
        print('Hey')
        chat = Chat.query.filter_by(user_1_id=current_user.id, user_2_id=user_id).first()
        time_check_current_user = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()

    elif Chat.query.filter_by(user_1_id=user_id, user_2_id=current_user.id).first() is not None:
        print('Ho')
        chat = Chat.query.filter_by(user_1_id=user_id, user_2_id=current_user.id).first()
        time_check_current_user = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()
    else:
        print('Huhu')
        chat = Chat(user_1_id=current_user.id, user_2_id=user_id)  # Create the chat
        db.session.add(chat)
        db.session.commit()
        time_check_current_user = LastTimeChecked(time=datetime.now(), chat_id=chat.id, user_id=current_user.id)  # Create the time checks
        time_check_user_2 = LastTimeChecked(time=datetime.now(), chat_id=chat.id, user_id=user_id)
        db.session.add(time_check_current_user)
        db.session.add(time_check_user_2)
        db.session.commit()
        print(chat.id)
        print('Huhu')

    form = MessageForm()
    if request.method == 'POST' and form.validate_on_submit():
        message = Message(text=form.text.data, post_time=datetime.now(), user_sender_id=current_user.id,
                          user_recipient_id=user_id, chat_id=chat.id)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('message.send_message', user_id=user_id))
    print('Poop')
    print(Message.query.filter_by(chat_id=chat.id).first())
    print('Poop')
    chat_messages = Message.query.filter_by(chat_id=chat.id)
    recipient_user = User.query.get(user_id)
    time_check_current_user.time = datetime.now()
    db.session.add(time_check_current_user)
    db.session.commit()
    return render_template('send_message.html', form=form, messages=chat_messages, recipient=recipient_user)


@messaging_bp.route('/view_messages', methods=['GET', 'POST'])
@login_required
def view_messages():
    user_chats_1 = Chat.query.filter_by(user_1_id=current_user.id).all()
    user_chats_2 = Chat.query.filter_by(user_2_id=current_user.id).all()
    user_chats = user_chats_1 + user_chats_2
    users = []
    messages = []
    unread_chats = []
    for chat in user_chats:
        chat_time_check = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()
        id_other_user = chat.user_1_id if chat.user_1_id != current_user.id else chat.user_2_id  # Get the id of the other user involved in the chat
        other_user = User.query.get(id_other_user)  # Grab the user
        users.append(other_user)
        messages.append(last_message)
        unread_chats.append(check_if_unread_chat(chat, chat_time_check))

    all_users = User.query.all()
    available_users = [("", "")] + [(user.first_name, user.first_name) for user in all_users if user.id != current_user.id]
    user_browser = LookForUser(user_choices=available_users)
    if request.method == 'POST' and user_browser.validate_on_submit():
        print('Hey')
        print(user_browser.user.data)
        print('Hey')
        user_selected = User.query.filter_by(first_name=user_browser.user.data).first()
        return redirect(url_for('message.send_message', user_id=user_selected.id))

    return render_template('view_messages.html', users_and_messages_and_unreads=zip(users, messages, unread_chats),
                           form=user_browser)
