
"""
Contains utility functions to works with learning-object delete.
"""

from manager.exceptions.learning_object import LearningObjectNotFoundError
from manager.exceptions.user import UserPermissionError

def check_user_permission(user, learning_object):
    learning_object_user_id = learning_object.get('user_id')
    user_id = user.get('_id')

    if user_id != learning_object_user_id:
        raise UserPermissionError(
            ['User is not own of this learning object.']
        )

def delete_one(db_client, learning_object_id, user):
    """Delete a learning object by _id."""

    # Check user permission.
    learning_object = db_client.learning_objects.find_one({
        '_id': learning_object_id
    })

    if not learning_object:
        raise LearningObjectNotFoundError({
            'errors': ['Learning Object _id not found.']
        })

    check_user_permission(user, learning_object)

    db_client.learning_objects.delete_one({'_id': _id})