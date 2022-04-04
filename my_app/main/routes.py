from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from my_app.main.forms import ProfileForm, Profile, ProposalForm
from my_app.models import User, Proposal, Character, Genre, Message, Chat, LastTimeChecked
from my_app import photos, db
from sqlalchemy import or_, desc, update
from sqlalchemy.sql import select
from datetime import datetime
from my_app.messaging.routes import check_if_unread

main_bp = Blueprint('main', __name__)


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
        return render_template('profile_options.html', already_has_profile=True, unread_messages=check_if_unread())
    else:
        return render_template('profile_options.html', already_has_profile=False, unread_messages=check_if_unread())


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
    return render_template('proposal_form.html', form=form, unread_messages=check_if_unread())


@main_bp.route('/display_proposals')
@login_required
def view_proposals():
    proposals = Proposal.query.all()
    genres = Genre.query.all()
    return render_template('proposals.html', proposals=proposals, genres=genres, unread_messages=check_if_unread())


@main_bp.route('/display_proposals/<proposal_id>')
@login_required
def view_specific_proposal(proposal_id):
    proposal = Proposal.query.get(proposal_id)
    print('Hey')
    print(proposal)
    print('Hey')
    proposal_genres = Genre.query.filter_by(proposal_id=proposal_id)
    proposal_characters = Character.query.filter_by(proposal_id=proposal_id)
    proposal_user = User.query.get(proposal.user_id)
    print(proposal_genres)
    print('Hey')
    return render_template('specific_proposal.html', proposal=proposal, genres=proposal_genres,
                           characters=proposal_characters, user=proposal_user, unread_messages=check_if_unread())


@main_bp.route('/my_proposals')
@login_required
def view_my_proposals():
    my_proposals = Proposal.query.filter_by(user_id=current_user.id).all()
    print('Woo')
    print(my_proposals)
    print('Woo')
    return render_template('my_proposals.html', proposals=my_proposals, unread_messages=check_if_unread())


@main_bp.route('/edit_proposal/<proposal_id>', methods=['GET', 'POST'])
@login_required
def edit_proposal(proposal_id):
    proposal = Proposal.query.get(proposal_id)
    characters = Character.query.filter_by(proposal_id=proposal_id).all()
    genres = Genre.query.filter_by(proposal_id=proposal_id).all()
    form = ProposalForm(title=proposal.title, plot=proposal.plot,
                        characters=[{character.character_name: character.character_description} for character in\
                                    characters],
                        genres=[genre.genre_name for genre in genres])
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
            proposal.title = form.title.data
            proposal.plot = form.plot.data
            for i in range(5):  # Maximum of 5 characters per proposal
                try:
                    characters[i].character_name = form.characters.data[i]['character_name']
                    characters[i].character_description = form.characters.data[i]['character_description']
                except IndexError:
                    # i is out of range of both the form characters and the available characters
                    if i not in range(len(characters)) and i not in range(len(form.characters.data)):
                        break
                    elif i not in range(len(characters)):
                        character = Character(character_name=form.characters.data[i]['character_name'],
                                              character_description=form.characters.data[i]['character_description'],
                                              proposal_id=proposal.id)
                        db.session.add(character)
                    else:  # Less characters where input than the ones previously stored
                        db.session.delete(characters[i])

            for i in range(3):
                try:
                    genres[i].genre_name = form.genres.data[i]['genre']
                except IndexError:  # New genre must be created
                    if i not in range(len(genres)) and i not in range(len(form.genres.data)):
                        break
                    elif i not in range(len(genres)):
                        genre = Genre(genre_name=form.genres.data[i]['genre'], proposal_id=proposal.id)
                        db.session.add(genre)
                    else:
                        db.session.delete(genres[i])

            db.session.commit()

            return redirect(url_for('main.view_my_proposals'))

    return render_template('proposal_form.html', form=form, unread_messages=check_if_unread())


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
    return render_template('profile.html', form=form, unread_messages=check_if_unread())


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
    return render_template('profile.html', form=form, unread_messages=check_if_unread())


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
                           profiles=zip(results, urls), unread_messages=check_if_unread())  # Note the zip to pass both lists as a parameter