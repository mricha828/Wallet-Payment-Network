from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField , IntegerField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length, Optional , NumberRange

class RegisterForm(FlaskForm):
    name = StringField("name", validators=[DataRequired(), Length(2, 30)])
    ssn = IntegerField("SSN",validators=[DataRequired()])
    phone = IntegerField("phone",validators=[DataRequired()])
    email= EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[InputRequired(), EqualTo('confirm', message='Passwords must match'),Length(min=0, max=20, message="The password should be minimum 6 characters in length")])
    confirm = PasswordField("confirm", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()]) #EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[InputRequired()])
    submit = SubmitField("Login")
    
class SendMoneyForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()]) #EmailField("email", validators=[DataRequired(), Email()])
    amount =  IntegerField("amount",validators=[DataRequired()])
    memo =  StringField("memo")
    submit = SubmitField("Send")

class RequestMoneyForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()]) #EmailField("email", validators=[DataRequired(), Email()])
    amount =  IntegerField("amount",validators=[DataRequired()])
    memo =  StringField("memo")
    submit = SubmitField("Request")


class PersonalDetailsForm(FlaskForm):
    name = StringField("name")
    ssn = IntegerField("ssn")
    phone = IntegerField("phone")
    email = EmailField("email")
    current_password = PasswordField("current password", validators=[Optional()])
    password = PasswordField("password", validators=[Optional(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("confirm", validators=[Optional(), EqualTo("password")])
    submit = SubmitField("Update")

class AddEmailForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])
    submit = SubmitField("Add Email")

class AddPhoneForm(FlaskForm):
    phone = IntegerField("phone",validators=[DataRequired()])
    submit = SubmitField("Add Phone")

class AddBankForm(FlaskForm):
    bank = StringField("bank number", validators=[DataRequired()])
    bankid = StringField("bankid", validators=[DataRequired()])
    submit = SubmitField("Add Bank")