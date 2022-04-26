import settings
import os
from flask import Flask, Response, json, request
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from database import MongoAPI
from auth import current_user, authenticate
from components import unique_email, device_registration, totp_mail, is_device_registered, decryptAES, verify_totp
from model.main import password_less_register, password_less_login

app = Flask(__name__)
mail = Mail(app)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = settings.APP_KEY

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = settings.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.config['JWT_SECRET_KEY'] = settings.JWT_KEY

JWTManager(app)
CORS(app)


@app.route('/users/current-user', methods=['GET'])
@jwt_required()
def current_user_session():
    current_session = current_user()
    return Response(response=json.dumps(current_session),
                    status=200 if current_session["status"] == "success" else 400,
                    mimetype='application/json')


@app.route('/users/register', methods=['POST'])
def register():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["user_details"]["email"])
    if not email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#106"}),
            status=200,
            mimetype='application/json')

    # User data insertion
    document["user_details"]["active"] = False
    document["user_details"]["verified"] = False
    user_obj = MongoAPI({"database": "C3AM",
                         "collection": "user_details"})
    if not user_obj.write({"document": document["user_details"]})["status"] == "success":
        return Response(
            response=json.dumps({"status": "error", "code": "#109"}),
            status=400,
            mimetype='application/json')

    # Device data insertion
    if document["remember_device"]:
        result = device_registration(document["user_details"]["email"], document["device_details"])
        if not result["status"] == "success":
            return Response(
                response=json.dumps(
                    {"status": "error", "code": "#109"}),
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
                {"status": "error", "code": "#109"}),
            status=400,
            mimetype='application/json')
    mail.send(mail_msg["data"])

    return Response(response=json.dumps({"status": "success",
                                         "code": "#104"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/activate', methods=['POST'])
def account_activation():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Verify the posted TOTP
    if not verify_totp(document)["status"] == "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#110"}),
            status=400,
            mimetype='application/json')

    # Change user status to active and authenticate the user
    user_obj = MongoAPI({"database": "C3AM", "collection": "user_details"})
    update_res = user_obj.update({"email": document["email"]},
                                 {"verified": True})

    # Check if verified status has been updated
    if update_res["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#109"}),
            status=400,
            mimetype='application/json')

    return Response(response=json.dumps({"status": "success", "code": "#103"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/password_less/activation', methods=['POST'])
def password_less_activation():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#111"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["verified"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#107"}),
            status=400,
            mimetype='application/json')

    user_obj = MongoAPI({"database": "C3AM", "collection": "user_details"})
    update_res = user_obj.update({"email": document["email"]},
                                 {"active": True})
    passwordless_res = password_less_register(document)
    auth_res = authenticate(document["email"])
    # Check if active status has been updated and authentication have been executed
    if update_res["status"] != "success" or passwordless_res["status"] != "success" or auth_res["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#109"}),
            status=400,
            mimetype='application/json')

    return Response(
        response=json.dumps({"status": "success", "code": "#101", "access_token": auth_res["access_token"]}),
        status=200,
        mimetype='application/json')


@app.route('/users/password_less/login', methods=['POST'])
def password_less_authentication():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#111"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is verified
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#107"}),
            status=400,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#108"}),
            status=400,
            mimetype='application/json')

    response = password_less_login(document)
    # Check if active status update and authentication have been executed
    if response["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#105"}),
            status=400,
            mimetype='application/json')

    if is_device_registered(document["email"], document["device_details"])["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#112"}),
            status=200,
            mimetype='application/json')

    # Create the current user session
    auth_res = authenticate(document["email"])
    if auth_res["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#109"}),
            status=400,
            mimetype='application/json')
    return Response(
        response=json.dumps({"status": "success", "code": "#101", "access_token": auth_res["access_token"]}),
        status=200,
        mimetype='application/json')


@app.route('/users/resend', methods=['POST'])
def resend_totp():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#111"}),
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

    return Response(response=json.dumps({"status": "success", "code": "OTP resent successfully"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/mfa-login', methods=['POST'])
def mfa_login():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#111"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#108"}),
            status=400,
            mimetype='application/json')

    # Mail the TOTP for MFA
    mail_content = {
        "subject": "Hi from C3AM",
        "body": "To complete your login enter the provided otp: "
    }
    mail_msg = totp_mail(document["email"], mail_content)
    mail.send(mail_msg["data"])

    return Response(response=json.dumps({"status": "success", "code": "#104"}),
                    status=200,
                    mimetype='application/json')


@app.route('/users/complete-mfa', methods=['POST'])
def complete_mfa():
    document = json.loads(decryptAES(request.json["encrypted"]))

    # Email Validation
    email_validation = unique_email(document["email"])
    if email_validation["unique"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#111"}),
            status=200,
            mimetype='application/json')

    # Check if the user account is active
    if not email_validation["instance"]["active"]:
        return Response(
            response=json.dumps({"status": "failure", "code": "#108"}),
            status=400,
            mimetype='application/json')

    # Verify the posted TOTP for MFA
    if not verify_totp(document):
        return Response(
            response=json.dumps({"status": "failure", "code": "#105"}),
            status=405,
            mimetype='application/json')

    # Device data insertion
    if document["remember_device"]:
        result = device_registration(document["email"], document["device_details"])
        if not result["status"] == "success":
            return Response(
                response=json.dumps(
                    {"status": "error", "code": "#109"}),
                status=400,
                mimetype='application/json')

    # Create the current user session
    auth_res = authenticate(document["email"])
    if auth_res["status"] != "success":
        return Response(
            response=json.dumps({"status": "failure", "code": "#109"}),
            status=400,
            mimetype='application/json')

    return Response(response=json.dumps({"status": "success", "code": "101", "access_token": auth_res["access_token"]}),
                    status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run()
