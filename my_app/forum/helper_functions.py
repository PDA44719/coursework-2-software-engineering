from flask import request
from flask_login import current_user
from my_app.forum.forms import ProposalForm
from my_app.models import Proposal, Character, Genre
from my_app import db


def modify_char_and_genre_entries(p_form):
    """
    Modify (add or remove) the number of character and genre entries in a proposal form.

    Arguments
    ---------
    p_form : my_app.forum.forms.ProposalForm
        The proposal form (which contains entries for characters and genres).

    Returns
    -------
    The form with the modified character/genre entries.

    """
    if request.form['button'] == 'Add Character':
        p_form.characters.append_entry()
    if request.form['button'] == 'Remove Character':
        p_form.characters.pop_entry()
    if request.form['button'] == 'Add Genre':
        p_form.genres.append_entry()
    if request.form['button'] == 'Remove Genre':
        p_form.genres.pop_entry()

    return p_form


def create_database_entries(p_form):
    """
    Create and submit the Proposal, Character and Genre entries extracted from a completed form.

    Arguments
    ---------
    p_form : my_app.forum.forms.ProposalForm
        The proposal form completed by the user.

    """
    # Create the proposal and commit it
    proposal = Proposal(title=p_form.title.data, plot=p_form.plot.data, user_id=current_user.id)
    db.session.add(proposal)
    db.session.commit()

    # Go through each character and genre in the form, create them and commit them
    for element in range(len(p_form.characters.data)):
        character = Character(character_name=p_form.characters.data[element]['character_name'],
                              character_description=p_form.characters.data[element]['character_description'],
                              proposal_id=proposal.id)
        db.session.add(character)
    for element in range(len(p_form.genres.data)):
        genre = Genre(genre_name=p_form.genres.data[element]['genre'], proposal_id=proposal.id)
        db.session.add(genre)

    db.session.commit()


def edit_characters(p_form, proposal, characters):
    """
    Modify the existing characters associated with a specific proposal.

    This function will be used in the forum.edit_proposal route.

    Arguments
    ---------
    p_form : my_app.forum.forms.ProposalForm
        The form submitted by the user, which contains the changes to the proposal.
    proposal : my_app.models.Proposal
        The existing proposal, which is going to be modified.
    characters : list[my_app.models.Character]
        A list of containing the characters from the proposal.

    """
    for i in range(5):  # Maximum of 5 characters per proposal
        try:  # Try to modify the character name and description
            characters[i].character_name = p_form.characters.data[i]['character_name']
            characters[i].character_description = p_form.characters.data[i]['character_description']
        except IndexError:
            # If there are no more characters to be modified
            if i not in range(len(characters)) and i not in range(len(p_form.characters.data)):
                break
            elif i not in range(len(characters)):  # # If new characters have been added in the form
                character = Character(character_name=p_form.characters.data[i]['character_name'],
                                      character_description=p_form.characters.data[i]['character_description'],
                                      proposal_id=proposal.id)
                db.session.add(character)
            else:  # If some of the existing characters have been removed
                db.session.delete(characters[i])


def edit_genres(p_form, proposal, genres):
    """
        Modify the existing genres associated with a specific proposal.

        This function will be used in the forum.edit_proposal route.

        Arguments
        ---------
        p_form : my_app.forum.forms.ProposalForm
            The form submitted by the user, which contains the changes to the proposal.
        proposal : my_app.models.Proposal
            The existing proposal, which is going to be modified.
        genres : list[my_app.models.Genre]
            A list of containing the genres from the proposal.

        """
    for i in range(3):  # Maximum of 3 genres per proposal
        try:  # Try to modify the genre names
            genres[i].genre_name = p_form.genres.data[i]['genre']
        except IndexError:
            # If there are no more genres to be modified
            if i not in range(len(genres)) and i not in range(len(p_form.genres.data)):
                break
            elif i not in range(len(genres)):  # If some of the genres have been added in the form
                genre = Genre(genre_name=p_form.genres.data[i]['genre'], proposal_id=proposal.id)
                db.session.add(genre)
            else:  # If some of the existing genres have been removed
                db.session.delete(genres[i])


def extract_proposal_info(proposal_id):
    """
    Get the proposal, characters and genres associated with a proposal_id.

    Arguments
    ---------
    proposal_id : str
        The string containing the id of the proposal whose information is to be extracted.


    Returns
    -------
    proposal : my_app.models.Proposal
        The proposal associated with the proposal_id.
    characters : list[my_app.models.Character]
        The list of characters from the proposal.
    genres : list[my_app.models.Genre]
        The list of genres from the proposal.

    """
    proposal = Proposal.query.get(proposal_id)
    characters = Character.query.filter_by(proposal_id=proposal_id).all()
    genres = Genre.query.filter_by(proposal_id=proposal_id).all()

    return proposal, characters, genres


def pre_populate_proposal_form(proposal, characters, genres):
    """
    Create a proposal form and pre-populate it with the information from an existing proposal.

    Arguments
    ---------
    proposal : my_app.models.Proposal
        The proposal whose information will pre-populate the form.
    characters: list[my_app.models.Character]
        The list of characters from the given proposal.
    genres: list[my_app.models.Genre]
        The list of genres from the given proposal.

    Returns
    -------
    my_app.forum.forms.ProposalForm
        The pre-populated form
    """
    form = ProposalForm(title=proposal.title, plot=proposal.plot,
                        characters=[{"character_name": character.character_name,
                                     "character_description": character.character_description}
                                    for character in characters],
                        genres=[{"genre": genre.genre_name} for genre in genres])

    return form


def modify_and_commit_proposal(p_form, proposal, characters, genres):
    """
    Modify an existing proposal and commit it.

    Arguments
    ---------
    p_form : my_app.forum.forms.ProposalForm
        The submitted form with the modified information about the proposal.
    proposal : m_app.models.Proposal
        The existing proposal, whose information is to be modified.
    characters : list[my_app.models.Character]
        The list of characters from the proposal.
    genres : list[my_app.models.Genre]
        The list of genres from the proposal

    """
    proposal.title = p_form.title.data
    proposal.plot = p_form.plot.data
    edit_characters(p_form, proposal, characters)
    edit_genres(p_form, proposal, genres)
    db.session.commit()
