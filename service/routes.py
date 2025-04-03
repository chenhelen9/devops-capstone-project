from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    location_url = url_for("get_accounts", account_id=account.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# LIST ALL ACCOUNTS
######################################################################

# ... place you code here to LIST accounts ...

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all Accounts
    """
    app.logger.info("Request to list all Accounts")
    accounts = Account.all()  # Fetch all accounts from DB
    results = [account.serialize() for account in accounts]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Reads an Account
    """
    app.logger.info("Request to read an Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")
    return jsonify(account.serialize()), status.HTTP_200_OK

'''
1. return account.serialize(), status.HTTP_200_OK
Here, account.serialize() is likely returning a dictionary.
Flask will automatically convert this dictionary into a JSON response when returning it.
However, if account.serialize() is not a dictionary (e.g., it returns a list or some other data structure), Flask may not handle it properly.

2. return jsonify(account.serialize()), status.HTTP_200_OK
jsonify() ensures the response is properly formatted as a JSON object.
It explicitly sets the Content-Type to application/json, making sure the response is treated as JSON.
It is recommended when returning JSON data to avoid potential issues with how Flask auto-converts responses.
Key Takeaway
Using jsonify() is the safer and more explicit way to return JSON data in a Flask app, as it ensures correct encoding and response headers.
'''
######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an Account
    This endpoint will update an Account based on the posted data
    """
    app.logger.info("Request to update an Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")
    account.deserialize(request.get_json())
    account.update()
    return account.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """
    Delete an Account
    """
    app.logger.info("Request to delete Account with id: %s", account_id)

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, description=f"Account with id [{account_id}] could not be found.")

    account.delete()
    return "", status.HTTP_204_NO_CONTENT

'''
######################################################################
# ERROR HANDLERS
######################################################################
@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """Handles 404 errors and returns a JSON response"""
    response = jsonify(message=error.description, status=status.HTTP_404_NOT_FOUND)
    response.status_code = status.HTTP_404_NOT_FOUND
    return response

'''

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {media_type}")

