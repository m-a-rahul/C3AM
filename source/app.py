import settings
from flask import Flask, Response, json, request
from flask_mail import Mail
from flask_session import Session
from database import MongoAPI
from auth import current_user, authenticate, log_out
from components import unique_email, device_registration, totp_mail
from core import verify_totp

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = settings.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/users/current-user', methods=['GET'])
def current_user_session():
    current_session = current_user()

    return Response(response=json.dumps(current_session),
                    status=200 if current_session["status"] == "success" else 400,
                    mimetype='application/json')


@app.route('/users/logout', methods=['POST'])
def logout_current_session():
    # No current active sessions
    current_session = current_user()
    if not current_session["status"] == "success":
        return Response(
            response=json.dumps(current_session),
            status=400,
            mimetype='application/json')

    response = log_out()

    return Response(response=json.dumps(response),
                    status=200,
                    mimetype='application/json')


@app.route('/users/register', methods=['POST'])
def register():
    document = request.json

    # Email Validation
    email_validation = unique_email(document["user_details"]["email"])
    if not email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Provided mail id already exists"}),
            status=200,
            mimetype='application/json')

    # User data insertion
    document["user_details"]["active"] = False
    user_obj = MongoAPI({"database": "C3AM",
                         "collection": "user_details"})
    if not user_obj.write({"document": document["user_details"]})["status"] == "success":
        return Response(
            response=json.dumps({"status": "error", "message": "Connection error please try again"}),
            status=400,
            mimetype='application/json')

    # Device data insertion
    if document["remember_device"]:
        result = device_registration(document["user_details"]["email"], document["device_details"])
        if not result["status"] == "success":
            return Response(
                response=json.dumps(
                    {"status": "error", "message": "Connection error your device couldn't be registered"}),
                status=400,
                mimetype='application/json')

    # Mail TOTP for MFA
    mail_content = {
        "subject": "Welcome to C3AM",
        "body": "To complete your registration enter the provided otp: "
    }
    mail_msg = totp_mail(document["user_details"]["email"], mail_content)
    if mail_msg["status"] != "success":
        return Response(
            response=json.dumps(
                {"status": "error", "message": "Connection error your device couldn't be registered"}),
            status=400,
            mimetype='application/json')
    mail.send(mail_msg["data"])

    return Response(response=json.dumps({"status": "success",
                                         "message": "Registration completed successfully! Check your email to activate your account"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/activate', methods=['POST'])
def account_activation():
    document = request.json

    # Verify the posted TOTP
    if not verify_totp(document)["status"] == "success":
        return Response(
            response=json.dumps({"status": "failure", "message": "Account activation unsuccessful, Try Again!"}),
            status=400,
            mimetype='application/json')

    # Change user status to active and authenticate the user
    user_obj = MongoAPI({"database": "C3AM", "collection": "user_details"})
    update_res = user_obj.update({"email": document["email"]},
                                 {"active": True})
    auth_res = authenticate(document["email"])

    # Check if active status update and authentication have been executed
    if update_res["status"] != "success" or auth_res["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "message": "Connection error please try again!"}),
            status=400,
            mimetype='application/json')

    return Response(response=json.dumps({"status": "success", "message": "Account activated successfully"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/resend', methods=['POST'])
def resend_totp():
    document = request.json

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Provided mail id does not exists"}),
            status=200,
            mimetype='application/json')

    # Check whether the account is active or not
    if email_validation["instance"]["active"]:
        mail_content = {
            "subject": "Hi from C3AM",
            "body": "To complete your login enter the provided otp: "
        }
        mail_msg = totp_mail(document["email"], mail_content)
    else:
        mail_content = {
            "subject": "Welcome to C3AM",
            "body": "To complete your registration enter the provided otp: "
        }
        mail_msg = totp_mail(document["email"], mail_content)
    mail.send(mail_msg["data"])

    return Response(response=json.dumps({"status": "success", "message": "OTP resent successfully"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/mfa-login', methods=['POST'])
def mfa_login():
    document = request.json

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Provided mail id does not exists"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Activate before you access your account"}),
            status=400,
            mimetype='application/json')

    # Mail the TOTP for MFA
    mail_content = {
        "subject": "Hi from C3AM",
        "body": "To complete your login enter the provided otp: "
    }
    mail_msg = totp_mail(document["email"], mail_content)
    mail.send(mail_msg["data"])

    return Response(response=json.dumps({"status": "success", "message": "TOTP sent to " + document["email"]}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/complete-mfa', methods=['POST'])
def complete_mfa():
    document = request.json

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Provided mail id does not exists"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "message": "Activate before you access your account"}),
            status=400,
            mimetype='application/json')

    # Verify the posted TOTP for MFA
    if not verify_totp(document):
        return Response(
            response=json.dumps({"status": "failure", "message": "Authentication unsuccessful, Try Aga!in"}),
            status=405,
            mimetype='application/json')

    # Create the current user session
    if authenticate(document["email"])["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "message": "Connection error please try again!"}),
            status=400,
            mimetype='application/json')

    return Response(response=json.dumps({"status": "success", "message": "Authenticated successfully"}),
                    status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run()
