from flask import session
from database import MongoAPI


def authenticate(email_id):
    """
    :param email_id: <str> Email id of the requested user
    :return: <json> Status of authentication
    """
    user_obj = MongoAPI({"database": "C3AM",
                         "collection": "user_details"})
    documents = user_obj.read()
    for doc in documents:
        if doc["email"] == email_id:
            session["username"] = doc["username"]
            session["email"] = doc["email"]
            return {"status": "success"}
    return {"status": "failure"}


def log_out():
    """
    :return: <json> Logout status
    """
    session.pop('email', None)
    return {"status": "success"}


def current_user():
    """
    :return: <json> Current user details
    """
    if 'email' in session:
        if session['email']:
            user_obj = MongoAPI({"database": "C3AM",
                                 "collection": "user_details"})
            documents = user_obj.read()
            for doc in documents:
                if doc["email"] == session['email']:
                    return {"status": "success",
                            "data": {"username": doc["username"],
                                     "email": doc["email"]}}

    return {"status": "failure"}
