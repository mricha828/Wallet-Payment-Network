from flask import Blueprint, redirect, request, render_template, url_for, flash
from flask import Blueprint, render_template, flash, redirect, url_for,current_app, session
from auth.forms import LoginForm, RegisterForm , SendMoneyForm, RequestMoneyForm
from sql.db import DB
import json
from datetime import datetime, date, timedelta
from collections import defaultdict

from flask import jsonify
#import dateutil.parser
from flask_login import login_user, login_required, logout_user, current_user
from auth.models import User
from sql.db import DB


main_menu = Blueprint('main_menu', __name__, url_prefix='/main_menu')


@main_menu.route('/account_info', methods=['GET', 'POST'])
@login_required
def account_info():
    user_email = current_user.get_email()
    result1={}
    try:
        result = DB.selectOne("SELECT SSN,NAME,BALANCE FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD =%s ",user_email)
        print(result)
        result2 = DB.selectAll("SELECT HA.BANK_ID, HA.BANK_NUMBER FROM USER_ACCOUNT as UA JOIN HAS_ADDITIONAL as HA WHERE UA.SSN=HA.SSN AND UA.SSN=%s",result.row["SSN"])
        print(result2)
        if result.status:
            flash("USER DETAILS FOUND", "success")
    except Exception as e:
            # TODO make this user-friendly
        flash(f"Error! value not found {e}", "danger")
    return render_template("account_info.html", info=result.row,resp=result2)

@main_menu.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    form = SendMoneyForm()
    if form.validate_on_submit():
        user_email = current_user.get_email()
        send_email = form.email.data
        amount = form.amount.data
        memo = form.memo.data
        print(user_email)
        try:
            result= DB.selectOne("SELECT * FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD = %s" ,send_email)
            if result.status:
                try:
                    res_amt = DB.selectOne("Select BALANCE,SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
                    if(res_amt.row["BALANCE"] > amount):
                        update_send= DB.update("UPDATE USER_ACCOUNT SET BALANCE = BALANCE + %s WHERE SSN= %s ",amount,result.row["SSN"])
                        update_user= DB.update("UPDATE USER_ACCOUNT SET BALANCE = BALANCE - %s WHERE SSN= %s ",amount,res_amt.row["SSN"])
                        flash("Transaction Made","success")
                        try:
                            res=DB.insertOne("INSERT INTO SEND_TRANSACTION(AMOUNT, MEMO, IDENTIFIER, SSN) values (%s,%s,%s,%s)",amount,memo,send_email,res_amt.row["SSN"])
                        except Exception as e:
                            flash(f"{e}","danger")
                    else:
                        flash("Insufficient Amount","danger")
                except Exception as e:
                    flash("User doesn't exist.","danger")
               
        except Exception as e:
            flash("User doesn't exist.","danger")

    return render_template("send_money.html",form=form)

@main_menu.route('/request_money', methods=['GET', 'POST'])
@login_required
def request_money():
    user_id = current_user.get_id()

    form = RequestMoneyForm()
    if form.validate_on_submit():
        user_email = current_user.get_email()
        request_email = form.email.data
        amount = form.amount.data
        memo = form.memo.data

        print(user_email)
        try:
            result= DB.selectOne("SELECT * FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD = %s" ,request_email)
            if(result.row != None):
                if result.status:
                    try:
                        res_amt = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
                        res=DB.insertOne("INSERT INTO REQUEST_TRANSACTION(AMOUNT, MEMO, SSN) values (%s,%s,%s)",amount,memo,res_amt.row["SSN"])
                        res_rtid=DB.selectOne("Select RT_ID FROM REQUEST_TRANSACTION ORDER BY RT_ID DESC LIMIT 1")
                        res1=DB.insertOne("INSERT INTO FROM_TRANSACTION (RT_ID, IDENTIFIER) values (%s,%s)",res_rtid.row["RT_ID"],request_email)
                        if res.status:
                            flash("Success data went into database","success")
                    except Exception as e:
                        flash(f"{e}","danger")
            else:
                flash("User doesn't exist.","danger")
        except Exception as e:
            flash("User doesn't exist.","danger")

    return render_template("request_money.html",form=form)

@main_menu.route('/pending_requests', methods=['GET', 'POST'])
@login_required
def pending_requests():
    user_id = current_user.get_id()
    user_email= current_user.get_email()
    print("---------------------------------------------")
    #flash(f"ID IS {user_id}","success")
    result= DB.selectAll("SELECT R.RT_ID,AMOUNT,MEMO, DATE_TIME FROM REQUEST_TRANSACTION R, FROM_TRANSACTION F WHERE R.RT_ID=F.RT_ID AND IDENTIFIER=%s ORDER BY DATE_TIME ASC",user_email)
    if result.status:
        flash("Working", "success")
    return render_template("pending_requests.html",resp=result)


@main_menu.route('/payment/<int:amount>/<int:rt_id>/<string:memo>')
@login_required
def payment(amount,rt_id,memo):
    user_email = current_user.get_email()
    user_balance = DB.selectOne("Select BALANCE,SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
    print(user_balance.row["BALANCE"])
    receiver_SSN = DB.selectOne("Select BALANCE,SSN FROM REQUEST_TRANSACTION NATURAL JOIN USER_ACCOUNT WHERE RT_ID=%s ",rt_id)
    print(user_email)
    print(amount)
    try:
        result= DB.selectOne("SELECT * FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE SSN = %s" ,receiver_SSN.row["SSN"])
        
        try:
            print("INSIDE TRY",user_balance.row["BALANCE"])

            if(user_balance.row["BALANCE"] > amount):
                update_send= DB.update("UPDATE USER_ACCOUNT SET BALANCE = BALANCE + %s WHERE SSN= %s ",amount,result.row["SSN"])
                update_user= DB.update("UPDATE USER_ACCOUNT SET BALANCE = BALANCE - %s WHERE SSN= %s ",amount,user_balance.row["SSN"])
                delete_request= DB.delete("DELETE FROM REQUEST_TRANSACTION WHERE RT_ID=%s",rt_id)
                res=DB.insertOne("INSERT INTO SEND_TRANSACTION(AMOUNT, MEMO, IDENTIFIER, SSN) values (%s,%s,%s,%s)",amount,memo,result.row["EMAIL_ADD"],user_balance.row["SSN"])
                flash("Transaction Made","success")
            else:
                flash("Insufficient Amount","danger")
        except Exception as e:
            flash("Insufficient Amount","danger")
    except Exception as e:
        flash("User doesn't exist.","danger")
    return pending_requests()


#def DecodeDateTime(result):
    #if 'DATE_TIME' in result:
#   result["DATE_TIME"] = dateutil.parser.parse(result["DATE_TIME"])
#   return result

""" @main_menu.route('/statements', methods=['GET', 'POST'])
@login_required
def statements():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("Select SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ",user_email)
    user_id = current_user.get_id()
    print("---------------------------------------------")
    #flash(f"ID IS {user_id}","success")
    result= DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"])
    if result.status:
        flash("Working", "success")
    return render_template("statements.html",resp=result) """

@main_menu.route('/monthly_statements', methods=['GET', 'POST'])
@login_required
def monthly_statements():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("SELECT SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ", user_email)
    user_id = current_user.get_id()
    print("---------------------------------------------")
    #flash(f"ID IS {user_id}","success")
    result = DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME, SSN FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"])
    if result.status:
        flash("Working", "success")

    # group transactions by month
    transactions_by_month = {}
    total_sent_by_month = {}
    total_received_by_month = {}

    for transaction in result.rows:
        month = transaction["DATE_TIME"].strftime("%B")
        if month not in transactions_by_month:
            transactions_by_month[month] = []
            total_sent_by_month[month] = 0
            total_received_by_month[month] = 0
        transactions_by_month[month].append(transaction)
        if transaction["SSN"] == user_ssn.row["SSN"]:
            total_sent_by_month[month] += transaction["AMOUNT"]
        elif transaction["IDENTIFIER"] == user_email:
            total_received_by_month[month] += transaction["AMOUNT"]

    return render_template("monthly_statements.html",
                           transactions_by_month=transactions_by_month,
                           total_sent_by_month=total_sent_by_month,
                           total_received_by_month=total_received_by_month)



@main_menu.route('/search_transactions', methods=['GET', 'POST'])
@login_required
def search_transactions():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("SELECT SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s", user_email)
    user_id = current_user.get_id()

    # Handle search
    search_query = request.args.get('search_query')
    if search_query:
        sql_statement = "SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME FROM SEND_TRANSACTION WHERE (IDENTIFIER=%s OR SSN=%s) AND (IDENTIFIER=%s OR STID=%s OR AMOUNT=%s OR MEMO=%s) ORDER BY DATE_TIME DESC"
        result = DB.selectAll(sql_statement, user_email, user_ssn.row["SSN"], search_query, search_query, search_query, search_query)
    else:
        sql_statement = "SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC"
        result = DB.selectAll(sql_statement, user_email, user_ssn.row["SSN"])


    if result.status:
        flash("Working", "success")

    return render_template("search_transaction.html", resp=result.rows)


@main_menu.route('/totalamount', methods=['GET', 'POST'])
@login_required
def totalamount():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("SELECT SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ", user_email)
    user_id = current_user.get_id()

    start_date = None
    end_date = None
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        result = DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME, SSN FROM SEND_TRANSACTION WHERE (IDENTIFIER=%s OR SSN=%s) AND DATE_TIME >= %s AND DATE_TIME <= %s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"], start_date, end_date)
    else:
        result = DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME, SSN FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"])
    
    if result.status:
        flash("Working", "success")

    transactions = []
    total_sent = 0
    total_received = 0

    for transaction in result.rows:
        if start_date and end_date:
            if start_date <= transaction["DATE_TIME"] <= end_date:
                transactions.append(transaction)
                if transaction["SSN"] == user_ssn.row["SSN"]:
                    total_sent += transaction["AMOUNT"]
                elif transaction["IDENTIFIER"] == user_email:
                    total_received += transaction["AMOUNT"]
        else:
            transactions.append(transaction)
            if transaction["SSN"] == user_ssn.row["SSN"]:
                total_sent += transaction["AMOUNT"]
            elif transaction["IDENTIFIER"] == user_email:
                total_received += transaction["AMOUNT"]

    return render_template("totalamount.html",
                           transactions=transactions,
                           total_sent=total_sent,
                           total_received=total_received)


@main_menu.route('/avgmoney', methods=['GET', 'POST'])
@login_required
def avgmoney():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("SELECT SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ", user_email)
    user_id = current_user.get_id()
    print("---------------------------------------------")
    #flash(f"ID IS {user_id}","success")
    result = DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME, SSN FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"])
    if result.status:
        flash("Working", "success")

    # group transactions by month
    transactions_by_month = {}
    total_sent_by_month = {}
    total_received_by_month = {}

    for transaction in result.rows:
        month = transaction["DATE_TIME"].strftime("%B")
        if month not in transactions_by_month:
            transactions_by_month[month] = []
            total_sent_by_month[month] = 0
            total_received_by_month[month] = 0
        transactions_by_month[month].append(transaction)
        if transaction["SSN"] == user_ssn.row["SSN"]:
            total_sent_by_month[month] += transaction["AMOUNT"]
        elif transaction["IDENTIFIER"] == user_email:
            total_received_by_month[month] += transaction["AMOUNT"]
    
    # calculate average money sent and received per month
    num_months = len(transactions_by_month)
    avg_sent_by_month = {month: total_sent_by_month[month]/num_months for month in total_sent_by_month}
    avg_received_by_month = {month: total_received_by_month[month]/num_months for month in total_received_by_month}

    return render_template("avgmoney.html",
                           transactions_by_month=transactions_by_month,
                           avg_sent_by_month=avg_sent_by_month,
                           avg_received_by_month=avg_received_by_month)


@main_menu.route('/maxmoney', methods=['GET', 'POST'])
@login_required
def maxmoney():
    user_email = current_user.get_email()
    user_ssn = DB.selectOne("SELECT SSN FROM EMAIL NATURAL JOIN USER_ACCOUNT WHERE EMAIL_ADD=%s ", user_email)
    user_id = current_user.get_id()
    print("---------------------------------------------")
    grant_perm=("GRANT EXECUTE ON FUNCTION DATE_TRUNC TO 'jc2494'@'%';")
    test_query=DB.selectAll("""SELECT DATE_FORMAT(DATE_TIME, '%Y-%m') AS month,
       MAX(CASE WHEN SSN = %s THEN AMOUNT ELSE 0 END) AS max_sent,
       MAX(CASE WHEN IDENTIFIER = %s THEN AMOUNT ELSE 0 END) AS max_received
FROM SEND_TRANSACTION
WHERE IDENTIFIER = %s OR SSN = %s
GROUP BY month""",user_ssn.row["SSN"],user_email,user_ssn.row["SSN"],user_email)
    print("printing test query result: ",test_query)
    #flash(f"ID IS {user_id}","success")
    result = DB.selectAll("SELECT STID, AMOUNT, MEMO, CANCEL_REASON, IDENTIFIER, DATE_TIME, SSN FROM SEND_TRANSACTION WHERE IDENTIFIER=%s OR SSN=%s ORDER BY DATE_TIME DESC", user_email, user_ssn.row["SSN"])
    if result.status:
        flash("Working", "success")

    # group transactions by month
    transactions_by_month = {}
    total_sent_by_month = {}
    total_received_by_month = {}

    for transaction in result.rows:
        month = transaction["DATE_TIME"].strftime("%B %Y")
        if month not in transactions_by_month:
            transactions_by_month[month] = []
            total_sent_by_month[month] = []
            total_received_by_month[month] = []
        transactions_by_month[month].append(transaction)
        if transaction["SSN"] == user_ssn.row["SSN"]:
            total_sent_by_month[month].append(transaction["AMOUNT"])
        elif transaction["IDENTIFIER"] == user_email:
            total_received_by_month[month].append(transaction["AMOUNT"])

    # find transactions with maximum amount sent and received per month
    max_sent_by_month = {month: max(total_sent_by_month[month]) if total_sent_by_month[month] else 0 for month in total_sent_by_month}
    max_received_by_month = {month: max(total_received_by_month[month]) if total_received_by_month[month] else 0 for month in total_received_by_month}
    max_sent_transactions = []
    max_received_transactions = []

    for month in transactions_by_month:
        for transaction in transactions_by_month[month]:
            if transaction["SSN"] == user_ssn.row["SSN"] and transaction["AMOUNT"] == max_sent_by_month[month]:
                max_sent_transactions.append(transaction)
            elif transaction["IDENTIFIER"] == user_email and transaction["AMOUNT"] == max_received_by_month[month]:
                max_received_transactions.append(transaction)

    return render_template("maxmoney.html",transactions_by_month=transactions_by_month,
                           max_sent_transactions=max_sent_transactions,
                           max_received_transactions=max_received_transactions, user_ssn=user_ssn,max_sent_by_month=max_sent_by_month)


