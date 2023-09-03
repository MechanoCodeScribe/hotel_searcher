from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField

db = SqliteDatabase('history.db')

class BaseModel(Model):
    """
    Base class
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    User table class
    """
    class Meta:
        db_table = 'users'
    command = CharField()
    date = CharField()
    user_id = IntegerField()


class Hotel(BaseModel):
    """
    Hotel table class
    """
    class Meta:
        db_table = 'hotels'
    name = CharField()
    address = CharField()
    req = ForeignKeyField(User, related_name='hotels')


