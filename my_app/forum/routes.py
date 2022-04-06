from my_app.forum.helper_functions import *
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from my_app.forum.forms import ProposalForm
from my_app.models import User, Proposal, Character, Genre
from my_app.messaging.routes import check_if_unread


forum_bp = Blueprint('forum', __name__)


@forum_bp.route('/create_proposal', methods=['GET', 'POST'])
@login_required
def create_proposal():
    """Route to create a new proposal"""
    form = ProposalForm()
    if request.method == 'POST':
        form = modify_char_and_genre_entries(form)
        if request.form['button'] == 'Submit Proposal' and form.validate_on_submit():  # Form was completed & validated
            create_database_entries(form)
            return redirect(url_for('main.index'))
    return render_template('proposal_form.html', form=form, unread_messages=check_if_unread())


@forum_bp.route('/display_proposals')
@login_required
def view_proposals():
    """Route to view all the proposals"""
    proposals = Proposal.query.all()
    genres = Genre.query.all()
    return render_template('proposals.html', proposals=proposals, genres=genres, unread_messages=check_if_unread())


@forum_bp.route('/display_proposals/<proposal_id>')
@login_required
def view_specific_proposal(proposal_id):
    """Route to view the information about a specific proposal"""
    proposal = Proposal.query.get(proposal_id)
    if proposal is None:  # If the proposal does not exist
        flash('The proposal the user is looking for does not exist')
        return redirect(url_for('forum.view_proposals'))

    # Get the info about the wanted proposal
    proposal_genres = Genre.query.filter_by(proposal_id=proposal_id)
    proposal_characters = Character.query.filter_by(proposal_id=proposal_id)
    proposal_user = User.query.get(proposal.user_id)
    return render_template('specific_proposal.html', proposal=proposal, genres=proposal_genres,
                           characters=proposal_characters, user=proposal_user, unread_messages=check_if_unread())


@forum_bp.route('/my_proposals')
@login_required
def view_my_proposals():
    """Route to view all the current user's proposals"""
    my_proposals = Proposal.query.filter_by(user_id=current_user.id).all()
    genres = Genre.query.all()
    return render_template('my_proposals.html', proposals=my_proposals, genres=genres,
                           unread_messages=check_if_unread())


@forum_bp.route('/edit_proposal/<proposal_id>', methods=['GET', 'POST'])
@login_required
def edit_proposal(proposal_id):
    """Route to edit (modify) an existing proposal"""
    # If the proposal that user wants to edit does not exist or was created by a different user
    if Proposal.query.get(proposal_id) is None or Proposal.query.get(proposal_id).user_id != current_user.id:
        flash('The proposal that the user is trying to edit does not exist/was not posted by the current user.')
        return redirect(url_for('forum.view_my_proposals'))

    proposal, characters, genres = extract_proposal_info(proposal_id)
    form = pre_populate_proposal_form(proposal, characters, genres)
    if request.method == 'POST':
        modify_char_and_genre_entries(form)
        if request.form['button'] == 'Submit Proposal' and form.validate_on_submit():  # Form was completed & validated
            modify_and_commit_proposal(form, proposal, characters, genres)
            return redirect(url_for('forum.view_my_proposals'))

    return render_template('proposal_form.html', form=form, unread_messages=check_if_unread())
