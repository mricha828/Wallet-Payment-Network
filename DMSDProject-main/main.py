# from https://towardsdatascience.com/deploy-to-google-cloud-run-using-github-actions-590ecf957af0
import os
import sys
from flask import Flask, session, render_template
from dotenv import load_dotenv
load_dotenv()
import flask_login
from flask_login import current_user
from flask_principal import identity_loaded, RoleNeed, UserNeed, Principal
# added so modules can be found between the two different lookup states:
# from tests and from regular running of the app
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
print(CURR_DIR)
sys.path.append(CURR_DIR)

# custom error pages
def page_not_found(e):
    return render_template('404.html'), 404

def permission_denied(e):
    return render_template("403.html"), 403


login_manager = flask_login.LoginManager()
# app = Flask(__name__)
def create_app(config_filename=''):
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, permission_denied)
    app.secret_key = os.environ.get("SECRET_KEY", "missing_secret")
    login_manager.init_app(app)
    # app.config.from_pyfile(config_filename)
    with app.app_context():
        from views.hello import hello
        app.register_blueprint(hello)
        from views.sample import sample
        app.register_blueprint(sample)
        from views.main_menu import main_menu
        app.register_blueprint(main_menu)
        from views.account import account
        app.register_blueprint(account)
        #from views.account_functions import account_functions
        #app.register_blueprint(account_functions)
        from auth.auth import auth
        app.register_blueprint(auth)
        from roles.roles import roles
        app.register_blueprint(roles)

        # load the extension
        principals = Principal(app) # must be defined/initialized for identity to work (flask_principal)
        @login_manager.user_loader
        def load_user(user_id):
            if user_id is None:
                return None
            print("login_manager loading user") # happens each request
            from auth.models import User
            if session["_user_id"] == user_id and "user" in session.keys():
                print("loading user from session")
                # load user from session (convert json to User)
                # see User object for convering json of roles to [Roles]
                import jsons
                return jsons.loads(session["user"], User)
            # failsafe if we don't have a "user" key in session
            from sql.db import DB
            print("loading user from DB") # note: we'd lose roles here since it makes a new user object without a roles query
            try:
                result = DB.selectOne("SELECT id, email FROM IS601_Users WHERE id = %s", user_id)
                if result.status:
                    return User(**result.row)
            except Exception as e:
                print(e)
            return None

        @identity_loaded.connect_via(app)
        def on_identity_loaded(sender, identity):
            # Set the identity user object
            identity.user = current_user

            # Add the UserNeed to the identity
            if hasattr(current_user, 'id'):
                identity.provides.add(UserNeed(current_user.id))

            # Assuming the User model has a list of roles, update the
            # identity with the roles that the user provides
            if hasattr(current_user, 'roles'):
                for role in current_user.roles:
                    pass
                    #identity.provides.add(RoleNeed(role.name))
        return app




app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
