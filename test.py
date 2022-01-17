try:
    from run import app
    import unittest
    import json
    from werkzeug.datastructures import MultiDict
    from flaskblog.users.forms import RegistrationForm
    from flask import Flask


except Exception as e:
    print("Some Modules are missing {} ".format(e))


class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.application = app.test_client()
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.form_data = {
            "username": "soumya",
            "email": "soumya@gmail.com",
            "password": "soumya",
            "confirm_password": "soumya"
        }
        self.sign_up_data = RegistrationForm(MultiDict(self.form_data))


    # check for response 200
    def test_userlist(self):
        response = self.application.get("/users/list")
        statuscode = response.status_code
        self.assertAlmostEqual(statuscode, 200)


    # check if content return is application/json
    def test_userlist_content(self):
        response = self.application.get("/users/list")
        self.assertAlmostEqual(response.content_type, "application/json")


    # check for data returned
    def test_userlist_data(self):
        response = self.application.get("/users/list")
        self.assertTrue(b'username' in response.data)


    # login test
    def test_successful_login(self):
        # Given
        username = "kruti"
        password = "kruti"
        payload = json.dumps({
            "username": username,
            "password": password
        })
        # When
        response = self.application.post('/users/login', headers={"Content-Type": "application/json"}, data=payload)

        # Then
        self.assertEqual(200, response.status_code)


    # register test
    def test_successful_registration(self):
        # Given
        with self.app_context:
            payload = self.sign_up_data
        # When
        response = self.app.post('/users/register', headers={"Content-Type": "application/json"}, data=payload)

        # Then
        self.assertEqual(200, response.status_code)
        # assert response == 200


if __name__ == '__main__':
    unittest.main()
