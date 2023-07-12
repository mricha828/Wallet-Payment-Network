from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, InputRequired

class RoleForm(FlaskForm):
    name = StringField("Role Name", validators=[DataRequired(),Length(1,20)])
    description = TextAreaField ("Description", validators=[InputRequired()])
    is_active = BooleanField("Is Active")
    submit = SubmitField("Save")