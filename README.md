# COMP0034 Coursework 2 Document
## Repository link
Here is the [link to my repository](https://github.com/ucl-comp0035/comp0034-cw2-i-PDA44719.git). GitHub has been used
consistently throughout the duration of the coursework. Furthermore, **weekly reports** have been posted on Moodle.
Please, check them if you see it fit.

## Requirements
The requirements have been specified on [requirements.txt](requirements.txt). They can all be installed using the
```pip install ...``` command.

## Application Details
Two different functionalities have been included in the app, which go beyond what was taught in the course:

- A **messaging system**, which allows the different users in the app to message each other. Through a combination of
different db.Models, information about the time that messages were sent and the time each chat was last checked, the
system will display a notification symbol (red dot) if the current user has any unread messages. Furthermore, the chats
will be ordered depending on how recent its last messages are.

- A **proposals forum**, which gives users the opportunity to post proposals about new movie projects so that they can
be contacted by other interested users (i.e., who may want to collaborate). The forum section uses Forms that have
customized validations and the users can modify existing proposals (i.e., change, add or remove details about the
proposal).

The **charts have been effectively incorporated** into the app by creating the same navigation bar that will be
displayed the rest of the app, which allows users to easily navigate between the flask and dash apps. Furthermore, a
new callback has been introduced (**unread_messages_notification**) which will also display the notification symbol if
the current has unread messages.

In terms of design, **blueprints** have been used. Each blueprint is defined in a different python package
([authorization](my_app/auth), [proposal forum](my_app/forum), [main](my_app/main) and [messaging](my_app/messaging)).
All these package (except for main) have a routes file in which the different app routes are defined, a helper_functions
file containing the functions that will be used inside routes and a forms file, which contains the different forms that
have been used.

Error handling has been applied in multiple ways: form checks, database checking to ensure the password input by the
user is correct, redirecting the user and displaying an alert if they try to: modify a non-existent proposal or one
that was not posted by them, starting a chat with a non-existing user or with themselves (which is not allowed).

The PyCharm IDE has been used, with an integrated linter to ensure that the code is largely free of issues. Docstrings
and comments have been included to help with readability and improve code quality.

List of user emails and passwords that can be used to check the app:
- pepe@gmail.com -> pepemola
- tom@gmail.com -> tommola
- james@gmail.com -> jamesmola
- julian@gmail.com -> julianmola
- opu@gmail.com -> opumola
- ursula@hotmail.com -> ursulamola
- uma@gmail.com -> umamola
- jim@gmail.com -> jimmola
- john@gmail.com -> johnmola
- pam@gmail.com -> pammola
