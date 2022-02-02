import json

from django.contrib.auth.models import User
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from social.models import Follow


class FolloTestCase(GraphQLTestCase):

    def test_follow_user(self):
        username = 'danitest'
        email = 'dani@email.net'
        password = 'aTzQrDP84D'
        username2 = 'danitest2'
        email2 = 'dani2@email.net'

        User.objects.create(username=username2, email=email2)
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        user.status.verified = True
        user.status.save()

        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        follow_user_query = '''
            mutation {
                followUser(
                        email: "%s"
                    ){
                    success
                    errors
                    follow{
                        user{
                            email
                        }
                        status
                    }
                }
            }
            ''' % (
            email2,
        )

        expected_result = {'data': {'followUser': {'success': True, 'errors': 'false', 'follow': {
            'user': {'email': 'dani2@email.net'}, 'status': 'PENDING'}}}}

        response = self.query(follow_user_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_result)

        bad_follow_user_query = '''
            mutation {
                followUser(
                        email: "%s"
                    ){
                    success
                    errors
                    follow{
                        user{
                            email
                        }
                        status
                    }
                }
            }
            ''' % (
            email,
        )

        expected_error = {'data': {'followUser': {
            'success': False, 'errors': 'You cant follow yourself', 'follow': None}}}
        response = self.query(bad_follow_user_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_error)
