import jsons # https://jsons.readthedocs.io/en/latest/index.html
# using jsons instead of json for better nested object serialization

# helper to serialize any class
class JsonSerializable(object):
    def toJson(self):
        return jsons.dumps(self)

    def __repr__(self):
        return self.toJson()

    def __str__(self):
        return self.toJson()

    def toJSON(self):
        return self.toJson()