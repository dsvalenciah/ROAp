
"""
Contains utility functions to works with user.
"""


from datetime import datetime
from uuid import uuid4

from exceptions.user import (
    UserNotFoundError, UserSchemaError, UserUnmodifyError, UserUndeleteError,
    UserDuplicateEmailError
)

from utils.regex import only_letters

from schemas.user import is_valid_user

from passlib.hash import sha512_crypt


def new_user(name, email, password):
    """Create a user dict."""
    # TODO: add salt to file configuration
    user = {
        '_id': str(uuid4().hex),
        'name': name,
        'email': email,
        'password': sha512_crypt.hash(password, salt='dqwjfdsakuyfd'),
        'created': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'modified': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'last_activity': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'status': 'inactive',
        'role': 'unknown',
    }
    return user


class User():
    """docstring for User."""

    def __init__(self, db):
        """Init."""
        self.db = db

    def insert_one(self, user):
        """Insert user."""
        # TODO: validate password and initial schema
        user_with_similar_email = self.db.users.find_one(
            {'email': user.get('email')}
        )
        if user_with_similar_email:
            raise UserDuplicateEmailError(['Duplicate email.'])

        user = new_user(
            user.get('name'),
            user.get('email'),
            user.get('password')
        )
        errors = is_valid_user(user)
        if errors:
            raise UserSchemaError(errors)

        result = self.db.users.insert_one(user)
        return result.inserted_id

    def get_one(self, uid):
        """Get a user by uid."""
        user = self.db.users.find_one({'_id': uid})
        if not user:
            raise UserNotFoundError({
                'errors': ['User uid not found.']
            })
        return user

    def get_many(self, query):
        """Get users with query."""
        # TODO: fix it and remove find().
        if query and query.get('offset') and query.get('count'):
            try:
                offset = int(query.get('offset'))
                count = int(query.get('count'))
            except ValueError as e:
                raise ValueError(['Invalid offset or count parameters.'])
            enabled_fields = [
                'name', 'password', 'email', 'role', 'status'
            ]
            correct_fields = [
                only_letters(x) for x in query.keys()
                if x in enabled_fields
            ]
            if False not in correct_fields:
                fields_to_use = [
                    {x: {'$regex': f'.*{query.get(x)}.*'}}
                    for x in query.keys()
                    if x in enabled_fields
                ]
                query = {'$and': fields_to_use} if fields_to_use else {}
                users = self.db.users.find(query)
                return users.skip(offset).limit(count)
            else:
                raise ValueError(['Invalid parameters value.'])
        else:
            return self.db.users.find()

    def modify_one(self, uid, user):
        """Modify user."""
        # TODO: define who do modifies who
        old_user = self.db.users.find_one({'_id': uid})
        if not old_user:
            raise UserNotFoundError({
                'errors': ['User uid not found.']
            })

        user.update({
            '_id': old_user.get('_id'),
            'created': old_user.get('created'),
            'modified': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'last_activity': old_user.get('last_activity'),
            'status': user.get('status') or old_user.get('status'),
            'role': user.get('role') or old_user.get('role'),
            'name': user.get('name') or old_user.get('name'),
            'email': user.get('email') or old_user.get('email'),
            'password': user.get('password') or old_user.get('password'),
            'role': user.get('role') or old_user.get('role'),
        })

        errors = is_valid_user(user)

        if errors:
            raise UserSchemaError(errors)

        result = self.db.users.update_one(
            {'_id': uid},
            {'$set': user}
        )

        if not result.modified_count:
            raise UserUnmodifyError(['The user is not modified.'])

    def delete_one(self, uid):
        """Delete a user by uid."""
        user = self.db.users.find_one({'_id': uid})
        if not user:
            raise UserNotFoundError({
                'errors': ['User uid not found.']
            })
        result = self.db.users.delete_one({'_id': uid})
        if not result.deleted_count:
            raise UserUndeleteError(['The user is not deleted.'])
