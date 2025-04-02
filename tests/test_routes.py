"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...

    def test_get_account(self):
        """It should Read a single Account"""
        account = self._create_accounts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{account.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_list_accounts(self):
        """It should List all Accounts"""
        self._create_accounts(3)  # Create 3 accounts
        resp = self.client.get(BASE_URL)  # Fetch all accounts
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)  # Ensure we get 3 accounts

#######################################################
    def test_update_existing_account(self):
        """It should successfully update an existing account"""
        test_account = Account(name="Old Name", email="old@example.com")
        test_account.create()

        updated_data = {"name": "Updated Name", "email": "updated@example.com"}

        # Send the PUT request
        resp = self.client.put(f"{BASE_URL}/{test_account.id}", json=updated_data)

        # Check if the response is successful
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Ensure update() executed and data changed
        updated_account = Account.find(test_account.id)
        self.assertIsNotNone(updated_account)
        self.assertEqual(updated_account.name, "Updated Name")
        self.assertEqual(updated_account.email, "updated@example.com")

        # Ensure serialize() executed correctly by checking the response JSON
        response_data = resp.get_json()
        self.assertEqual(response_data["name"], "Updated Name")
        self.assertEqual(response_data["email"], "updated@example.com")

    
    def test_update_nonexistent_account(self):
        """It should return 404 when trying to update a non-existent account"""
        updated_data = {"name": "Updated Name", "email": "updated@example.com"}

        # Send PUT request to a non-existent account ID
        resp = self.client.put(f"{BASE_URL}/99999", json=updated_data)

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_account_not_found(self):
        """It should return 404 when deleting a non-existent account"""
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_delete_existing_account(self):
        """It should successfully delete an existing account"""
        test_account = Account(name="Delete Me", email="delete@example.com")
        test_account.create()

        # Ensure account exists before deletion
        self.assertIsNotNone(Account.find(test_account.id))

        # Send DELETE request
        resp = self.client.delete(f"{BASE_URL}/{test_account.id}")

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        
        # Ensure the account no longer exists
        deleted_account = Account.find(test_account.id)
        self.assertIsNone(deleted_account)
