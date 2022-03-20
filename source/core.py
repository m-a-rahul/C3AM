import datetime
from database import MongoAPI


def verify_totp(data):
    """
    :param data: <json> JSON containing email and totp
    :return <json> JSON containing status along with the corresponding message
    """
    totp_obj = MongoAPI({"database": "C3AM", "collection": "totp"})
    documents = totp_obj.read()
    for doc in documents:
        if doc["email"] == data["email"] and doc["totp"] == data["totp"]:
            current_time = datetime.datetime.now()
            time_difference = current_time - doc["datetime"]
            time_delay = divmod(time_difference.days * (24 * 60 * 60) + time_difference.seconds, 60)
            in_secs = time_delay[0] * 60 + time_delay[1]
            if in_secs < 300:
                totp_obj.delete({"document": doc})
                return {"status": "success",
                        "message": "Authentication successful"}
    return {"status": "failure",
            "message": "Authentication unsuccessful"}
