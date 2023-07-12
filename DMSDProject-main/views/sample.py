from flask import Blueprint, redirect, request, render_template, url_for, flash
from flask import Blueprint, render_template, flash, redirect, url_for,current_app, session
from auth.forms import LoginForm, RegisterForm
from sql.db import DB

from flask_login import login_user, login_required, logout_user, current_user
from sql.db import DB
sample = Blueprint('sample', __name__, url_prefix='/sample')

sample.route('/account_info', methods=['GET', 'POST'])
def account_info():
    user_id = current_user.get_id()
    flash("ID IS ","success")
    '''k = request.form.get("key", None)
    v = request.form.get("value", None)
    if k and v:
        try:
            result = DB.insertOne(
                "INSERT INTO IS601_Sample (name, val) VALUES(%s, %s)", k, v)
            if result.status:
                flash("Created Record", "success")
        except Exception as e:
            # TODO make this user-friendly
            flash("Error! Record cannot be created", "danger")'''

    return render_template("account_info.html")
@sample.route('/add', methods=['GET', 'POST'])
def add():
    k = request.form.get("key", None)
    v = request.form.get("value", None)
    if k and v:
        try:
            result = DB.insertOne(
                "INSERT INTO IS601_Sample (name, val) VALUES(%s, %s)", k, v)
            if result.status:
                flash("Created Record", "success")
        except Exception as e:
            # TODO make this user-friendly
            flash("Error! Record cannot be created", "danger")

    return render_template("add_sample.html")

@sample.route('/list', methods=['GET'])
def list():
    key = request.args.get("name")
    col = request.args.get("col")
    order = request.args.get("order")
    limit = request.args.get("limit", 10)
    args = []
    print(f"col {col} order {order}")
    # dynamically build our query and data mappings
    # use the WHERE true trick so we can easily append conditions without caring if a condition
    # already was applied (no need to check if WHERE exists)
    query = "SELECT id, name, val, created, modified from IS601_Sample WHERE 1=1"
    if key:
        query += " AND name like %s"
        args.append(f"%{key}%")
    if col and order:
        # incorrect
        # these get passed as safe strings rather than sql keywords
        # query += f" ORDER BY %s %s"
        # args.append(col)
        # args.append(order)
        # correct - validate fully that col and order are expected values
        # this will be directly injected and if not validated could
        # lead to sql injection
        if col in ["name","val","created","modified"] \
            and order in ["asc", "desc"]:
            query += f" ORDER BY {col} {order}"

    if limit and int(limit) > 0 and int(limit) <= 100:
        # technically this should follow the same rules as col/order
        # but it seems to work with the placeholder mapping with
        # this connector
        query += " LIMIT %s"
        args.append(int(limit))
    rows = []
    try:
        # convert our list to args via *
        print(query)
        resp = DB.selectAll(query, *args)
        if resp.status:
            rows = resp.rows
    except Exception as e:
        # TODO make this user-friendly
        flash("Error! Failed to list the records", "danger")
    
    return render_template("list_sample.html", resp=rows)

@sample.route("/edit", methods=["GET", "POST"])
def edit():
    id = request.args.get("id")
    row = None
    if id is None:
        flash("ID is missing", "danger")
        return redirect("sample.list")
    else:
        if request.method == "POST" and request.form.get("value"):
            val = request.form.get("value")
            try:
                result = DB.update("UPDATE IS601_Sample SET val = %s WHERE id = %s", val, id)
                if result.status:
                    flash("Updated record", "success")
            except Exception as e:
                # TODO make this user-friendly
                flash("Error! Record cannot be updated", "danger")
        try:
            result = DB.selectOne("SELECT name, val FROM IS601_Sample WHERE id = %s", id)
            if result.status:
                row = result.row
        except Exception as e:
            # TODO make this user-friendly
            flash("Error! Failed to list records", "danger")
    return render_template("edit_sample.html", row=row)

@sample.route("/delete", methods=["GET"])
def delete():
    id = request.args.get("id")
    # make a mutable dict
    args = {**request.args}
    if id:
        try:
            result = DB.delete("DELETE FROM IS601_Sample WHERE id = %s", id)
            if result.status:
                flash("Deleted record", "success")
        except Exception as e:
            # TODO make this user-friendly
            flash("Error! Failed to Delete records", "danger")
        # TODO pass along feedback

        # remove the id args since we don't need it in the list route
        # but we want to persist the other query args
        del args["id"]
    return redirect(url_for("sample.list", **args))