from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from my_app.main.forms import ProfileForm, Profile, ProposalForm, MessageForm
from my_app.models import User, Proposal, Character, Genre, Message, Chat, LastTimeChecked
from my_app import photos, db
from sqlalchemy import or_, desc, update
from sqlalchemy.sql import select
from datetime import datetime

main_bp = Blueprint('main', __name__)


def check_if_unread():
    time_checks = LastTimeChecked.query.filter_by(user_id=current_user.id).all()
    for time_check in time_checks:
        chat = Chat.query.get(time_check.chat_id)
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()
        print('Yo')
        print(last_message.post_time)
        print(time_check.time)
        print('Yo')
        if last_message.post_time > time_check.time:
            print('It worked')
            return True

    return False


@main_bp.route('/')
@login_required
def index():
    if not current_user.is_anonymous:
        name = current_user.first_name
        flash(f'Hello {name}. ')
    return render_template('main_page.html', unread_messages=check_if_unread())


@main_bp.route('/dash_app/')
@login_required
def dash_app():
    return redirect('/dash_app/')


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = Profile.query.join(User, User.id == Profile.user_id).filter(User.id == current_user.id).first()
    if profile is not None:
        return render_template('profile_options.html', already_has_profile=True)
    else:
        return render_template('profile_options.html', already_has_profile=False)


@main_bp.route('/create_proposal', methods=['GET', 'POST'])
@login_required
def create_proposal():
    form = ProposalForm()
    if request.method == 'POST':
        if request.form['button'] == 'Add Character':
            form.characters.append_entry()
        if request.form['button'] == 'Remove Character':
            form.characters.pop_entry()
        if request.form['button'] == 'Add Genre':
            form.genres.append_entry()
        if request.form['button'] == 'Remove Genre':
            form.genres.pop_entry()
        if request.form['button'] == 'Submit Proposal' and form.validate_on_submit():
            proposal = Proposal(title=form.title.data, plot=form.plot.data,
                                user_id=current_user.id)
            db.session.add(proposal)
            db.session.commit()
            for element in range(len(form.characters.data)):
                character = Character(character_name=form.characters.data[element]['character_name'],
                                      character_description=form.characters.data[element]['character_description'],
                                      proposal_id=proposal.id)
                db.session.add(character)

            for element in range(len(form.genres.data)):
                genre = Genre(genre_name=form.genres.data[element]['genre'], proposal_id=proposal.id)
                db.session.add(genre)

            db.session.commit()

            return redirect(url_for('main.index'))
    return render_template('proposal_form.html', form=form)


@main_bp.route('/display_proposals')
@login_required
def view_proposals():
    proposals = Proposal.query.all()
    genres = Genre.query.all()
    return render_template('proposals.html', proposals=proposals, genres=genres)


@main_bp.route('/display_proposals/<proposal_id>')
@login_required
def view_specific_proposal(proposal_id):
    proposal = Proposal.query.get(proposal_id)
    print('Hey')
    print(proposal)
    print('Hey')
    proposal_genres = Genre.query.filter_by(proposal_id=proposal_id)
    proposal_characters = Character.query.filter_by(proposal_id=proposal_id)
    print(proposal_genres)
    print('Hey')
    return render_template('specific_proposal.html', proposal=proposal, genres=proposal_genres,
                           characters=proposal_characters)


@main_bp.route('/send_message/<user_id>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.send_message', user_id=user_id))
    print('Poop')
    print(Message.query.filter_by(chat_id=chat.id).first())
    print('Poop')
    chat_messages = Message.query.filter_by(chat_id=chat.id)
    recipient_user = User.query.get(user_id)
    time_check_current_user.time = datetime.now()
    db.session.add(time_check_current_user)
    db.session.commit()
    return render_template('send_message.html', form=form, messages=chat_messages, recipient=recipient_user)


@main_bp.route('/view_messages')
@login_required
def view_messages():
    user_chats_1 = Chat.query.filter_by(user_1_id=current_user.id).all()
    user_chats_2 = Chat.query.filter_by(user_2_id=current_user.id).all()
    user_chats = user_chats_1 + user_chats_2
    users = []
    messages = []
    for chat in user_chats:
        last_message = Message.query.filter_by(chat_id=chat.id).order_by(desc('post_time')).first()
        id_other_user = chat.user_1_id if chat.user_1_id != current_user.id else chat.user_2_id  # Get the id of the other user involved in the chat
        other_user = User.query.get(id_other_user)  # Grab the user
        users.append(other_user)
        messages.append(last_message)

    for message in messages:
        print(message)

    return render_template('view_messages.html', users_and_messages=zip(users, messages))


@main_bp.route('/create_profile', methods=['GET', 'POST'])
@login_required
def create_profile():
    form = ProfileForm()  # This should be familiar from login and signup routes in auth
    if request.method == 'POST' and form.validate_on_submit():
        filename = None  # Set the filename for the photo to None since this is the default if the user hasn't chosen to add a profile photo
        if 'photo' in request.files:  # Let's you check the submited form contains a photo (photo is the field name we used in the ProfileForm class)
            if request.files['photo'].filename != '':  # As long as the filename isn't empty then save the photo
                filename = photos.save(request.files[
                                           'photo'])  # This saves the photo using the global variable photos to get the location to save to
        p = Profile(username=form.username.data, photo=filename, user_id=current_user.id)  # Build a new profile to be added to the database based on the fields in the form
        db.session.add(p)  # Add the new Profile to the database session
        db.session.commit()  # This saves the new Profile to the database
        return redirect(url_for('main.display_profiles', username=p.username))
    return render_template('profile.html', form=form)


@main_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    profile = Profile.query.join(User, User.id == Profile.user_id).filter_by(id=current_user.id).first()  # Find the existing profile for this user
    form = ProfileForm(
        obj=profile)  # Pre-populate the form by loading the profile using obj=. This relies on the field names in the Profile class in model matching the field names in the ProfileForm class, otherwise you have to explicitly state each field e.g. if the form used bio and the model used biography you would need to add  bio = profile.biography

    if request.method == 'POST' and form.validate_on_submit():
        if 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            profile.photo = filename  # Updates the photo field
        profile.username = form.username.data  # Updates the user field
        db.session.commit()  # Save the changes to the database
        return redirect(url_for('main.display_profiles', username=profile.username))
    return render_template('profile.html', form=form)


@main_bp.route('/display_profiles', methods=['POST', 'GET'])
@main_bp.route('/display_profiles/<username>/', methods=['POST', 'GET'])
@login_required
def display_profiles(username=None):
    results = None
    if username is None:
        if request.method == 'POST':
            term = request.form['search_term']
            if term == "":
                flash("Enter a name to search for")
                return redirect(url_for("main.index"))
            results = Profile.query.filter(Profile.username.contains(term)).all()
    else:
        results = Profile.query.filter_by(username=username).all()
    if not results:
        flash("No users found.")
        return redirect(url_for("main.index"))
    # The following iterates through the results and adds the full url to a list of urls
    urls = []
    for result in results:
        url = url_for('static', filename='img/'+result.photo)  # uses the global photos plus the photo file name to determine the full url path
        urls.append(url)
    return render_template('display_profile.html',
                           profiles=zip(results, urls))  # Note the zip to pass both lists as a parameter