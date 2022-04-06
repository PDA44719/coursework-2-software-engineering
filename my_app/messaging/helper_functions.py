from flask_login import current_user
from my_app.models import User, Message, Chat, LastTimeChecked
from my_app import db
from sqlalchemy import desc
from datetime import datetime
import time


def check_if_unread_chat(chat, time_check):
    """
    Check if a specific chat has unread messages.

    Arguments
    ---------
    chat : my_app.models.Chat
        The chat that is to be checked.
    time_check : my_app.models.LastTimeChecked
        The model containing the information about the last time the chat was checked by the user.

    Returns
    -------
    bool
        True if the chat has any unread messages, otherwise False.

    """
    # Get the last message that was stored in the chat
    last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()

    # If there is a last message and it was posted after the last time the chat was checked
    if last_message and last_message.post_time > time_check.time:
        return True
    else:
        return False


def check_if_unread():
    """
    Check if the user has any unread messages.

    Returns
    -------
    bool
        True if the user has any unread messages, otherwise False.

    """
    # Obtain the time checks of all the user's chats
    time_checks = LastTimeChecked.query.filter_by(user_id=current_user.id).all()

    for time_check in time_checks:
        chat = Chat.query.get(time_check.chat_id)  # Get the chat associated with the time check
        if check_if_unread_chat(chat, time_check):
            return True

    return False


def create_chat_and_time_checks(user_id):
    """
    Create a chat between the current user and another user, and a time check of the chat for each of the users.

    Arguments
    ---------
    user_id : str
        The id of the user with whom the current user wants to chat.

    Returns
    -------
    chat : my_app.models.Chat
        The created chat between the two users.
    time_check_current_user : my_app.models.LastTimeChecked
        The time check of the chat for the current user.

    """
    # Create and commit the chat
    chat = Chat(user_1_id=current_user.id, user_2_id=user_id)
    db.session.add(chat)
    db.session.commit()

    # Create and commit the time checks
    time_check_current_user = LastTimeChecked(time=datetime.now(), chat_id=chat.id,
                                              user_id=current_user.id)
    time_check_user_2 = LastTimeChecked(time=datetime.now(), chat_id=chat.id, user_id=user_id)
    db.session.add(time_check_current_user)
    db.session.add(time_check_user_2)
    db.session.commit()

    return chat, time_check_current_user


def get_chat_and_time_check(user_id):
    """
    Get the chat between the current user and another user, and the time check of the chat by the current user. Create
    them if they do not exist.

    Arguments
    ---------
    user_id : str
        The id of the other user involved in the chat.

    Returns
    -------
    chat : my_app.models.Chat
        The chat between the two users.
    time_check_current_user : my_app.models.LastTimeChecked
        The time check of the chat by the current user.

    """
    # If the chat between the two users already exists, get it and the time check
    if Chat.query.filter_by(user_1_id=current_user.id, user_2_id=user_id).first() is not None:
        chat = Chat.query.filter_by(user_1_id=current_user.id, user_2_id=user_id).first()
        time_check_current_user = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()
    elif Chat.query.filter_by(user_1_id=user_id, user_2_id=current_user.id).first() is not None:
        chat = Chat.query.filter_by(user_1_id=user_id, user_2_id=current_user.id).first()
        time_check_current_user = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()

    else:  # If the chat does not exist, create it and the time checks for both users.
        chat, time_check_current_user = create_chat_and_time_checks(user_id)

    return chat, time_check_current_user


def get_user_chats():
    """
    Get all the chats associated with the current user.

    Returns
    -------
    list[my_app.models.Chat]
        The list of all the current user's chats.

    """
    user_chats_1 = Chat.query.filter_by(user_1_id=current_user.id).all()
    user_chats_2 = Chat.query.filter_by(user_2_id=current_user.id).all()
    user_chats = user_chats_1 + user_chats_2

    return user_chats


def get_chats_info(user_chats):
    """
    Get information about the users, last messages and whether or not there are any unread messages for each of the
    current user's chats.

    Arguments
    ---------
    user_chats : list[my_app.models.Chat]
        List of the current user's chats.

    Returns
    -------
    users : list[my_app.models.User]
        List of users that the current user has a chat with.
    messages : list[my_app.models.Message]
        List containing the last messages in each of the chats (can be None if the chat has no messages).
    unread_chats : list[bool]
        A list containing boolean values. If a chat has unread messages True will be appended, otherwise False.

    """
    users, messages, unread_chats = ([] for i in range(3))  # Initialize the lists
    for chat in user_chats:
        # Get the id of the other user involved in the chat
        id_other_user = chat.user_1_id if chat.user_1_id != current_user.id else chat.user_2_id
        other_user = User.query.get(id_other_user)
        users.append(other_user)

        # Obtain the last message in the chat
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()
        messages.append(last_message)

        # Get time check of the chat by the current user
        chat_time_check = LastTimeChecked.query.filter_by(chat_id=chat.id, user_id=current_user.id).first()
        unread_chats.append(check_if_unread_chat(chat, chat_time_check))

    return users, messages, unread_chats


def reverse_order(tup):
    """
    Reverse the order of the elements inside a tuple.

    Arguments
    ---------
    tup : tuple
        The tuple that is to be inverted.

    Returns
    -------
    list
        A list containing the values of the tuple in reverse order.

    """
    reversed_list = [element for element in reversed(tup)]
    return reversed_list


def dt_with_delay():
    """
    Get the current datetime and introduce a delay.

    This function will be used to introduce datetimes for chats that contain no messages, so that they can be compared
    to those with messages (chats with no messages will not be displayed in view_messages.html, but their last_message
    value, which is None, can lead to errors). The delay is introduced to prevent two empty last_messages to be given
    the same datetime value.

    Returns
    -------
    datetime.datetime
        The current datetime.

    """
    dt = datetime.now()
    time.sleep(0.000000001)
    return dt


def order_chats_info(users, last_messages, unread_chats):
    """
    Order to information about all the chats of the current user (the other users in the chat, the last messages in the
    chat and whether or not those chats have unread messages) according to post time of the last messages.

    Arguments
    ---------
    users : list[my_app.models.User]
        List of users that the current user has a chat with.
    last_messages : list[my_app.models.Message]
        List containing the last messages in each of the chats.
    unread_chats : list[bool]
        A list containing boolean values. Chats with unread messages will have a value of True, otherwise False.

    Returns
    -------
    lists
        The same lists as the ones in the arguments, but ordered according to the post time of the last messages
        (descending order).

    """
    if last_messages:
        # Get the post times of each of the last messages. If a chat has no messages, use dt_with_delay()
        p_times = [message.post_time if message is not None else dt_with_delay() for message in last_messages]

        # Order all the lists with respect to post_times (ascending order and the lists are converted to tuples)
        p_times, last_messages, users, unread_chats = zip(*sorted(zip(p_times, last_messages, users, unread_chats)))

        # Convert the tuples back to lists and reverse their order
        users = reverse_order(users)
        last_messages = reverse_order(last_messages)
        unread_chats = reverse_order(unread_chats)

    return users, last_messages, unread_chats


def check_if_no_messages(list_of_messages):
    """
    Check if a user has not received/sent any messages.

    Arguments
    ---------
    list_of_messages : list[my_app.models.Message]
        A list of messages.

    Returns
    -------
    bool
        True if the user has not chats or all the chats are empty, otherwise False.

    """
    if not list_of_messages:  # List is empty (there user has not started any chats).
        return True
    else:
        return all(message is None for message in list_of_messages)  # True if all the chats are empty else False


def create_and_commit_message(m_form, recipient_id, chat_id):
    """
    Create a message from the data stored in a form and commit it.

    Arguments
    ---------
    m_form : my_app.messaging.forms.MessageForm
        The form that has stored the message's text.
    recipient_id : str
        The string that represents the id of the recipient of the message.
    chat_id : int
        The id of the chat between the current user and the recipient.

    """
    message = Message(text=m_form.text.data, post_time=datetime.now(), user_sender_id=current_user.id,
                      user_recipient_id=recipient_id, chat_id=chat_id)
    db.session.add(message)
    db.session.commit()
