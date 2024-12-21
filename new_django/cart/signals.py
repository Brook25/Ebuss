from django.contrib.sessions.backends.base import SessionBase  # Import for SessionBase
from django.dispatch import reveiver
from .signals import persist_data_to_db_from_sessions



def get_user_carts(user):
    """Retrieves session data for the given user, handling potential errors."""

    session_key = user.get_session_key()
    if session_key:
        try:
            session_store_class = SessionBase.get_session_store_class()
            session = session_store_class[session_key]  # Concise syntax
            carts = session.get('carts', {})
            session['carts'] = []
            return carts

        except (KeyError, SessionBase.DoesNotExist):
            # Handle cases where session key is invalid or session doesn't exist
            return {}
    else:
        return {}  # Return empty data if no session key found



@receiver(user_logged_out)
def copy_data_from_sessions_to_db(sender, user, **kwargs):
    carts =  get_user_carts(user)
    if session:
        persist_data_to_db_from_sessions(user=user, carts=carts)
