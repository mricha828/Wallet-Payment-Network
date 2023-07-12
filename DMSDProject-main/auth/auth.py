from flask import Blueprint, render_template, flash, redirect, url_for,current_app, session
from auth.forms import LoginForm, RegisterForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user, current_user
from auth.models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

from flask_principal import Identity, AnonymousIdentity, identity_changed
from email_validator import validate_email

auth = Blueprint('auth', __name__, url_prefix='/',template_folder='templates')


@auth.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    # wtform validators are both client-side and server-side
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        name = form.name.data
        phone = form.phone.data
        ssn = form.ssn.data
        try:
            #hash = bcrypt.generate_password_hash(password)
            # save the hash, not the plaintext password
            result_phone= DB.insertOne("INSERT INTO ELEC_ADDRESS(identifier,type_eorp) VALUES (%s,'phone')",phone)
            result_email= DB.insertOne("INSERT INTO ELEC_ADDRESS(identifier,type_eorp) VALUES (%s,'email')",email)
            result = DB.insertOne("INSERT INTO USER_ACCOUNT(ssn,name,phone_number) VALUES (%s, %s, %s)",ssn,name,phone)
            result_login = DB.insertOne("INSERT INTO USER_LOGIN(email,password) VALUES (%s, %s)",email,password)
            result_email_add= DB.insertOne("INSERT INTO EMAIL(email_add,ssn) VALUES (%s,%s)",email,ssn)
            
            if result.status:
                flash("Successfully registered","success")
            if result_phone.status:
                flash("Successfully registered_phone","success")
            if result_email.status:
                flash("Successfully registered email","success")
            if result_login.status:
                flash("Successfully entered in login","success")
        except Exception as e:
            flash(f"Error! Registration Failed {e}", "danger")
    return render_template("register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        is_valid = True
        email = form.email.data # email or username
        if "@" in email:
            try:
                validate_email(email)
            except:
                is_valid = False
                flash("Invalid email address", "danger")
        else:
            import re
            r = re.fullmatch("/^[a-z0-9_-]{2,30}$/", email)
            if r:
                is_valid = False
                flash("Invalid username", "danger")
        password = form.password.data
        if is_valid:
            try:
                result = DB.selectOne("SELECT id,email, password FROM USER_LOGIN where email= %s and password =%s", email,password)
                if result.status and result.row:
                    
                    
                        del result.row["password"] # don't carry password/hash beyond here
                        user = User(**result.row)
                        success = login_user(user) # login the user via flask_login
                        
                        if success:
                            # Tell Flask-Principal the identity changed
                            identity_changed.send(current_app._get_current_object(),
                                    identity=Identity(user.id))
                            # store user object in session as json
                            session["user"] = user.toJson()
                            flash("Log in successful", "success")
                            return redirect(url_for("auth.landing_page"))
                        else:
                            flash("Error logging in", "danger")
                    
                else:
                    # invalid user and invalid password together is too much info for a potential attacker
                    # normally we return a single message for both "invalid username or password" so an attacker doens't know which part was correct
                    flash("Invalid user", "warning")

            except Exception as e:
                flash(f"Login failed {e}", "danger")
    return render_template("login.html", form=form)

@auth.route("/landing-page", methods=["GET"])
@login_required
def landing_page():
    
    return render_template("landing_page.html")


@auth.route("/logout", methods=["GET"])
def logout():
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),identity=AnonymousIdentity())
    flash("Successfully logged out", "success")
    return redirect(url_for("auth.login"))
'''
@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = current_user.get_id()
    form = ProfileForm()
    if form.validate_on_submit():
        is_valid = True
        email = form.email.data
        username = form.username.data
        import re
        r = re.fullmatch("/^[a-z0-9_-]{2,30}$/", username)
        if r:
            is_valid = False
            flash("Invalid username", "danger")
        current_password = form.current_password.data
        password = form.password.data
        confirm = form.confirm.data
        # handle password change only if all 3 are provided
        if current_password and password and confirm:
            try:
                result = DB.selectOne("SELECT password FROM IS601_Users where id = %s", user_id)
                if result.status and result.row:
                    # verify current password
                    if bcrypt.check_password_hash(result.row["password"], current_password):
                        # update new password
                        hash = bcrypt.generate_password_hash(password)
                        try:
                            result = DB.update("UPDATE IS601_Users SET password = %s WHERE id = %s", hash, user_id)
                            if result.status:
                                flash("Updated password", "success")
                        except Exception as ue:
                            flash(f"Failed to update password : {ue}", "danger")
                    else:
                        flash("Invalid password","danger")
            except Exception as se:
                flash(f"Password could not be retrieved : {se}", "danger")
        
        if is_valid:
            try: # update email, username (this will trigger if nothing changed but it's fine)
                result = DB.update("UPDATE IS601_Users SET email = %s, username = %s WHERE id = %s", email, username, user_id)
                if result.status:
                    flash("Saved profile", "success")
            except Exception as e:
                flash(f"Error! Failed to update the profile because {e}", "danger")
    try:
        # get latest info if anything changed
        result = DB.selectOne("SELECT id, email, username FROM IS601_Users where id = %s", user_id)
        if result.status and result.row:
            user = User(**result.row)
            form = ProfileForm(obj=user)
            # TODO update session
            current_user.email = user.email
            current_user.username = user.username
            session["user"] = current_user.toJson()
    except Exception as e:
        flash("Failed to retrieve updated info", "danger")
    return render_template("profile.html", form=form)
'''