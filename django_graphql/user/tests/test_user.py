import json

from django.contrib.auth.models import User
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token


class UserTestCase(GraphQLTestCase):

    def test_register_user(self):
        register_query = '''
            mutation {
                register(
                    username: "%s",
                    password1: "%s",
                    password2: "%s",
                    email: "%s",
                ){
                    success
                    errors
                    token
                }
            }
            ''' % (
            'danitest',
            'aTzQrDP84D',
            'aTzQrDP84D',
            'dani@email.net'
        )

        response = self.query(register_query)
        result = json.loads(response.content)

        self.assertEqual(result['data']['register']['success'], True)
        self.assertEqual(result['data']['register']['errors'], None)
        self.assertNotEqual(result['data']['register']['token'], None)

        expected_error = {
            'username': [{
                'message': 'A user with that username already exists.',
                'code': 'unique'
            }
            ]
        }
        response = self.query(register_query)
        result = json.loads(response.content)
        self.assertEqual(result['data']['register']['success'], False)
        self.assertEqual(result['data']['register']['errors'], expected_error)
        self.assertEqual(result['data']['register']['token'], None)

    def test_login_user(self):
        username = 'danitest'
        email = 'dani@email.net'
        password = 'aTzQrDP84D'
        bad_password = 'dc43rDP8H6'

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        login_query = '''
            mutation {
                tokenAuth(
                    password: "%s",
                    email: "%s",
                ){
                    success
                    errors
                    token
                    user{
                    id
                    verified
                    }
                }
            }
            ''' % (
            password,
            email,
        )

        response = self.query(login_query)
        result = json.loads(response.content)
        self.assertEqual(result['data']['tokenAuth']['success'], True)
        self.assertEqual(result['data']['tokenAuth']['errors'], None)
        self.assertNotEqual(result['data']['tokenAuth']['token'], None)

        bad_login_query = '''
            mutation {
                tokenAuth(
                    password: "%s",
                    email: "%s",
                ){
                    success
                    errors
                    token
                    user{
                    id
                    verified
                    }
                }
            }
            ''' % (
            bad_password,
            email,
        )

        expected_error = {
            'nonFieldErrors': [{
                'message': 'Please, enter valid credentials.',
                'code': 'invalid_credentials'
            }
            ]
        }
        response = self.query(bad_login_query)
        result = json.loads(response.content)
        self.assertEqual(result['data']['tokenAuth']['success'], False)
        self.assertEqual(result['data']['tokenAuth']['errors'], expected_error)
        self.assertEqual(result['data']['tokenAuth']['token'], None)

    def test_user_password_change(self):
        username = 'danitest'
        email = 'dani@email.net'
        password = 'aTzQrDP84D'
        bad_password = 'dc43rDP8H6'
        new_password = 'dc43rDP8H8'

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        user.status.verified = True
        user.status.save()

        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        change_password_query = '''
            mutation {
                passwordChange(
                    oldPassword: "%s",
                    newPassword1: "%s",
                    newPassword2: "%s"
                ) {
                    success,
                    errors,
                    token
                }
            }
            ''' % (
            password,
            new_password,
            new_password,
        )

        response = self.query(change_password_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result['data']['passwordChange']['success'], True)
        self.assertEqual(result['data']['passwordChange']['errors'], None)
        self.assertNotEqual(result['data']['passwordChange']['token'], None)

        expected_error = {'nonFieldErrors': [{
            'message': 'Unauthenticated.',
            'code': 'unauthenticated'
        }]
        }
        response = self.query(change_password_query)
        result = json.loads(response.content)
        self.assertEqual(result['data']['passwordChange']['success'], False)
        self.assertEqual(result['data']['passwordChange']
                         ['errors'], expected_error)
        self.assertEqual(result['data']['passwordChange']['token'], None)

    def test_search_users(self):
        partial_username = 'ni'
        password = 'aTzQrDP84D'

        User.objects.create(username='danitest', email='dani@email.net')
        User.objects.create(username='juani', email='juani@email.net')
        User.objects.create(username='juan', email='juan@email.net')
        user = User.objects.create(
            username='graphql', email='graphql@email.net')
        user.set_password(password)
        user.save()
        user.status.verified = True
        user.status.save()

        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        search_query = '''
            query {
                searchUsers(
                        username: "%s"
                    ){
                        id
                        username
                    }
                }
            ''' % (
            partial_username
        )

        expected_response = {'data': {'searchUsers': [
            {'id': '3', 'username': 'danitest'}, {'id': '4', 'username': 'juani'}]}}

        response = self.query(search_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_response)
