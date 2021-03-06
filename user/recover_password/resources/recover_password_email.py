import falcon
from utils.email_jobs import queue


class UserEmail(object):
    """Deal with user validation."""

    def __init__(self, db):
        """Init."""
        self.db_client = db

    def on_get(self, req, resp, email):
        """Send user account validation."""
        valid_langs = {
            'en_US': 'en_US',
            'es_CO': 'es_CO',
            'pt_BR': 'pt_BR'
        }
        value_lang_cookie = valid_langs.get(
            req.cookies.get('user_lang')) or 'es_CO'

        if (self.db_client.users.find_one({'email': email})):
        #if True:
            queue().enqueue('utils.email_jobs.send_email',
                            email, value_lang_cookie)

        resp.media = {'status': 'ok'}
