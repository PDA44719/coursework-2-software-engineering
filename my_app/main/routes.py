from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from my_app.main.forms import ProfileForm, Profile, ProposalForm
from my_app.models import User, Proposal
from my_app import photos, db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    if not current_user.is_anonymous:
        name = current_user.first_name
        flash(f'Hello {name}. ')
    return render_template('main_page.html')


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
    if request.method == 'POST' and form.validate_on_submit():
        proposal = Proposal(title=form.title.data, plot=form.plot.data, user_id=current_user.id)
        db.session.add(proposal)
        db.session.commit()
        return redirect('main.index')
    return render_template('proposal_form.html', form=form)


@main_bp.route('/display_proposals')
@login_required
def view_proposals():
    proposals = Proposal.query.all()
    return render_template('proposals.html', proposals=proposals)


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