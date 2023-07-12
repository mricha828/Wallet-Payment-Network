from flask_login import UserMixin
from common.utils import JsonSerializable

class User(UserMixin, JsonSerializable):
    def __init__(self, id, email):
        self.id = id
        self.email = email

    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def get_id(self):
        return str(self.id)
    def get_email(self):
        return str(self.email)
    # usable in templates and views to check if user has a role
