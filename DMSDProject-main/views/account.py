from flask import Blueprint, redirect, request, render_template, url_for, flash
from flask import Blueprint, render_template, flash, redirect, url_for,current_app, session
from auth.forms import PersonalDetailsForm, AddEmailForm, AddPhoneForm, AddBankForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user, current_user
from auth.models import User
from sql.db import DB
account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/modify', methods=['GET', 'POST'])
@login_required
def modify():
    user_id = current_user.get_id()
    user_email = current_user.get_email()

    form = PersonalDetailsForm()
    print("ssnnnnnnn")
    if request.method == "POST":
        data = {} # use this as needed, can convert to tuple if necessary
            # TODO edit-1 retrieve form data for name, address, city, state, country, zip, website
        name = request.form.get("name")
        email = request.form.get("email")
        ssn= request.form.get("ssn")
        phone = request.form.get("phone")
        password = request.form.get("password")
        result= DB.selectOne("SELECT * FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD = %s" ,user_email)
        try:
            
            if(ssn):
                upssn= DB.update("UPDATE USER_ACCOUNT SET SSN=%s WHERE SSN= %s",ssn, result.row["SSN"])
                flash("Updation Successful", "success")
        except Exception as e :
            flash(f"Error updating value {e}","danger")
        # handle password change only if all 3 are provided
        if password:
            try:
                result = DB.selectOne("SELECT password FROM USER_LOGIN where id = %s", user_id)
                print(result)
                if result.status and result.row:
                    # verify current password
                    if (result.row["password"]):
                        # update new password
                        hash = password
                        try:
                            result = DB.update("UPDATE USER_LOGIN SET password = %s WHERE id = %s", hash, user_id)
                            if result.status:
                                flash("Updated password", "success")
                        except Exception as ue:
                            flash(f"Failed to update password : {ue}", "danger")
                    else:
                        flash("Invalid password","danger")
            except Exception as se:
                flash(f"Password could not be retrieved : {se}", "danger")
        
        if email:
            try: # update email, username (this will trigger if nothing changed but it's fine)
                result0 = DB.update("UPDATE ELEC_ADDRESS SET IDENTIFIER = %s WHERE IDENTIFIER = %s", email, user_email)
                #result = DB.update("UPDATE USER_LOGIN SET EMAIL = %s WHERE id = %s", email, user_id)
                if result0.status:
                    flash("Saved profile", "success")
            except Exception as e:
                flash(f"Error! Failed to update the profile because {e}", "danger")
                
        if name:
            try: # update email, username (this will trigger if nothing changed but it's fine)
                result0 = DB.update("UPDATE USER_ACCOUNT SET NAME = %s WHERE SSN = %s", name, result.row["SSN"])
                #result = DB.update("UPDATE USER_LOGIN SET EMAIL = %s WHERE id = %s", email, user_id)
                if result0.status:
                    flash("Saved profile", "success")
            except Exception as e:
                flash(f"Error! Failed to update the profile because {e}", "danger")
                
    try:
        # get latest info if anything changed
        res_amt = DB.selectAll("Select * FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
        #result_1= DB.selectAll("SELECT * FROM USER_ACCOUNT WHERE SSN = %s", res_amt.row["SSN"])
        print("------------------")
        print(res_amt.row)
        if res_amt.status and res_amt.row:
            print("------------------")
            print(res_amt.row)
            user = res_amt.row
            form = PersonalDetailsForm(obj=user)
            # TODO update session
            current_user.email = user.email
            #current_user.name = user.name
            session["user"] = current_user.toJson()
    except Exception as e:
        flash("Failed to retrieve updated info", "danger")
    
    row = {}
    try:
        # TODO edit-11 fetch the updated data
        print(user_email)
        res_amt = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
        print(res_amt.row)
        result = DB.selectOne("SELECT SSN, NAME, PHONE_NUMBER FROM USER_ACCOUNT WHERE SSN=%s", res_amt.row["SSN"])
        if result.status:
            row = result.row
            flash("Successfully Updated","success")
    except Exception as e:
        # TODO edit-12 make this user-friendly
        flash("Error occured! The data cannot be retrived", "danger")
# TODO edit-13 pass the company data to the render template
    return render_template("personal_details.html", account=row)


    
@account.route('/email', methods=['GET', 'POST'])
@login_required
def email():
    user_id = current_user.get_id()
    user_email = current_user.get_email()

    res_amt = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
    #flash(f"ID IS {user_id}","success")
    form = AddEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            try:
                result=DB.insertOne("INSERT INTO ELEC_ADDRESS(IDENTIFIER,type_eorp) VALUES (%s,'email')",email)
                add_email= DB.insertOne("INSERT INTO EMAIL(EMAIL_ADD, SSN) VALUES (%s,%s)",email,res_amt.row["SSN"])
                if add_email.status:
                    flash("Successfully inserted new email", "success")
            except Exception as e:
                    flash(f"Error! Failed to add email because {e}", "danger")
        except Exception as e:
                flash(f"Error! Failed to get email data {e}", "danger")
    try:
        res=DB.selectAll("SELECT EMAIL_ADD FROM EMAIL WHERE SSN=%s",res_amt.row["SSN"])
    except Exception as e:
        flash(f"Error collecting emails {e}","danger")

    return render_template("add_email.html",form=form,resp=res)

@account.route("/delete_email", methods=["GET"])
def delete_email():
    user_email = current_user.get_email()
    email = request.args.get("ids")
    # make a mutable dict
    args = {**request.args}
    print(user_email)
    print(email)
    if(user_email!=email):
        try:
            result = DB.delete("DELETE FROM ELEC_ADDRESS WHERE IDENTIFIER = %s", email)
            if result.status:
                flash("Deleted record", "success")
        except Exception as e:
            # TODO make this user-friendly
            flash("Error! Failed to Delete records", "danger")
        # TODO pass along feedback

        # remove the id args since we don't need it in the list route
        # but we want to persist the other query args
        del args["ids"]
    return redirect(url_for("account.email", **args))

@account.route("/delete_phone", methods=["GET"])
def delete_phone():
    user_email=current_user.email
    phone = request.args.get("ids")
    # make a mutable dict
    args = {**request.args}
    print(phone)
    try:
        result = DB.delete("DELETE FROM ELEC_ADDRESS WHERE IDENTIFIER = %s", phone)
        if result.status:
            flash("Deleted record", "success")
    except Exception as e:
        # TODO make this user-friendly
        flash("Error! Failed to Delete records", "danger")
    # TODO pass along feedback

    # remove the id args since we don't need it in the list route
    # but we want to persist the other query args
    del args["ids"]
    return redirect(url_for("account.phone", **args))

@account.route('/phone', methods=['GET', 'POST'])
@login_required
def phone():
    user_email = current_user.get_email()
    form = AddPhoneForm()
    res={}
    res_amt = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
    if form.validate_on_submit():
        phone = form.phone.data
        #res_amt = DB.selectOne("Select SSN, NAME, BALANCE FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
        try:
            result=DB.insertOne("INSERT INTO ELEC_ADDRESS(IDENTIFIER,type_eorp) VALUES (%s,'phone')",phone)
            add_phone= DB.insertOne("INSERT INTO PHONE(PHONE_NO, SSN) VALUES (%s,%s)",phone,res_amt.row["SSN"])
            #add_phone= DB.insertOne("INSERT INTO USER_ACCOUNT(SSN, NAME, PHONE_NUMBER, BALANCE) VALUES (%s,%s,%s,%s)",res_amt.row["SSN"],res_amt.row["NAME"],phone,res_amt.row["BALANCE"])
                
            if result.status:
                flash("Successfully inserted new phone", "success")
        except Exception as e:
                flash(f"Error! Failed to add the phone because {e}", "danger")
    try:
        res=DB.selectAll("SELECT PHONE_NO FROM PHONE WHERE SSN=%s ",res_amt.row["SSN"])
    except Exception as e:
        flash(f"Error collecting phone {e}","danger")
    return render_template("add_phone.html",form=form,resp=res)


@account.route('/bank', methods=['GET', 'POST'])
@login_required
def bank():
    user_id = current_user.get_id()
    user_email = current_user.get_email()
    form = AddBankForm()

    res_amt = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
    if form.validate_on_submit():
        bankid = form.bankid.data
        bank = form.bank.data
        try:
            try:
                result=DB.insertOne("INSERT INTO BANK_ACCOUNT(BANK_ID,BANK_NUMBER) VALUES (%s,%s)",bankid,bank)
                result=DB.insertOne("INSERT INTO HAS_ADDITIONAL(SSN,BANK_ID,BANK_NUMBER) VALUES (%s,%s,%s)",res_amt.row["SSN"],bankid,bank)
                result=DB.update("UPDATE USER_ACCOUNT SET BANK_ID = %s, BANK_NUMBER = %s WHERE SSN = %s AND BANK_ID IS NULL",bankid,bank,res_amt.row["SSN"])
                #add_email= DB.insertOne("INSERT INTO EMAIL(EMAIL_ADD, SSN) VALUES (%s,%s)",email,res_amt.row["SSN"])
                if result.status:
                    flash("Successfully inserted new bank account", "success")
            except Exception as e:
                    flash(f"Error! Failed to add bank account because {e}", "danger")
        except Exception as e:
                flash(f"Error! Failed to get bank data {e}", "danger")
    try:
        res=DB.selectAll("SELECT BANK_ID,BANK_NUMBER FROM HAS_ADDITIONAL WHERE SSN=%s ",res_amt.row["SSN"])
    except Exception as e:
        flash(f"Error collecting bank details {e}","danger")
    return render_template("add_bank.html",form=form,resp=res)



@account.route("/delete_bank", methods=["GET"])
def delete_bank():
    user_email=current_user.email
    bank_number = request.args.get("ids")
    bank_id=request.args.get("num")
    # make a mutable dict
    args = {**request.args}
    print(args)
    try:
        result = DB.delete("DELETE FROM BANK_ACCOUNT WHERE BANK_NUMBER = %s and BANK_ID=%s", bank_number,bank_id)
        if result.status:
            flash("Deleted record", "success")
    except Exception as e:
        # TODO make this user-friendly
        flash("Error! Failed to Delete records", "danger")
    # TODO pass along feedback

    # remove the id args since we don't need it in the list route
    # but we want to persist the other query args
    del args["ids"]
    return redirect(url_for("account.bank", **args))