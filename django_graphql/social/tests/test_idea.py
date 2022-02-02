import json

from django.contrib.auth.models import User
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from social.models import Idea


class IdeaTestCase(GraphQLTestCase):

    def test_create_idea(self):
        username = 'danitest'
        email = 'dani@email.net'
        password = 'aTzQrDP84D'
        text = 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'
        text_too_long = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged."
        visibility = 'protected'

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        user.status.verified = True
        user.status.save()

        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        create_idea_query = '''
            mutation {
                createIdea(
                        text: "%s",
                        visibility: "%s",
                    ){
                    success
                    errors
                    idea{
                        id
                    }
                }
            }
            ''' % (
            text,
            visibility
        )

        expected_result = {'data': {'createIdea': {
            'success': True, 'errors': 'false', 'idea': {'id': '1'}}}}

        response = self.query(create_idea_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_result)

        bad_create_idea_query = '''
            mutation {
                createIdea(
                        text: "%s",
                        visibility: "%s",
                    ){
                    success
                    errors
                    idea{
                        id
                    }
                }
            }
            ''' % (
            text_too_long,
            visibility
        )

        expected_error = {'data': {'createIdea': {
            'success': False, 'errors': 'The text is too long, the maximum length is 140 characters', 'idea': None}}}
        response = self.query(bad_create_idea_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_error)

    def test_update_idea_visibility(self):
        username = 'danitest'
        email = 'dani@email.net'
        password = 'aTzQrDP84D'
        text = 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.'
        visibility = 'public'

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        user.status.verified = True
        user.status.save()

        idea = Idea.objects.create(user=user, text=text)

        token = get_token(user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}

        update_idea_query = '''
            mutation {
                updateIdeaVisibility(
                        id: %s,
                        visibility: "%s",
                    ){
                    success
                    errors
                    idea{
                        id
                        visibility
                    }
                }
            }
            ''' % (
            idea.id,
            visibility
        )

        expected_result = {'data': {'updateIdeaVisibility': {
            'success': True, 'errors': 'false', 'idea': {'id': '2', 'visibility': 'PUBLIC'}}}}

        response = self.query(update_idea_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_result)

        bad_update_idea_query = '''
            mutation {
                createIdea(
                        text: "%s",
                        visibility: "",
                    ){
                    success
                    errors
                    idea{
                        id
                    }
                }
            }
            ''' % (
            text,
        )

        expected_error = {'data': {'createIdea': {
            'success': False, 'errors': 'Visibility is required', 'idea': None}}}
        response = self.query(bad_update_idea_query, headers=headers)
        result = json.loads(response.content)
        self.assertEqual(result, expected_error)
