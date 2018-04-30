from freelance.core.tests import APIViewTestCase
from freelance.account.models import User


class RegistrationTestCase(APIViewTestCase):
    def setUp(self):
        super(RegistrationTestCase, self).setUp()
        self.user = User.objects.create(email='test@example.com')

    def test_201_registration(self):
        data = {
            'email': 'test2@example.com',
            'password': 'qwerty',
            'first_name': 'Monty',
            'last_name': 'Python',
            'role': 'freelancer',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('id' in response.data)

    def test_400_no_role(self):
        data = {
            'email': 'test2@example.com',
            'password': 'qwerty',
            'first_name': 'Monty',
            'last_name': 'Python',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 400)

    def test_400_exists_user(self):
        data = {
            'email': 'test@example.com',
            'password': 'qwerty',
            'first_name': 'Monty',
            'last_name': 'Python',
            'role': 'client',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 400)

    def test_400_invalid_email(self):
        data = {
            'email': 'example.com',
            'password': 'qwerty',
            'first_name': 'Monty',
            'last_name': 'Python',
            'role': 'client',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 400)

    def test_400_short_password(self):
        data = {
            'email': 'test2@example.com',
            'password': 'qwe',
            'first_name': 'Monty',
            'last_name': 'Python',
            'role': 'client',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 400)

    def test_400_invalid_role(self):
        data = {
            'email': 'test2@example.com',
            'password': 'qwe',
            'first_name': 'Monty',
            'last_name': 'Python',
            'role': 'invalid',
        }
        response = self.client.post('/api/v1/users', data)
        self.assertEqual(response.status_code, 400)


class AuthorizationTestCase(APIViewTestCase):
    def setUp(self):
        super(AuthorizationTestCase, self).setUp()
        self.user = User.objects.create(email='test1@example.com')
        self.user.set_password('qwerty')
        self.user.save()
        response = self.client.post(
            '/api/v1/login', {
                'email': 'test1@example.com',
                'password': 'qwerty'})
        self.user_token = response.data['token']

    def test_200(self):
        data = {
            'email': 'test1@example.com',
            'password': 'qwerty'
        }
        response = self.client.post('/api/v1/login', data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in response.data)

    def test_401(self):
        data = {
            'email': 'test1@example.com',
            'password': 'qwertyyy'
        }
        response = self.client.post('/api/v1/login', data)
        self.assertEqual(response.status_code, 401)

    def test_200_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.user_token))
        response = self.client.post('/api/v1/logout')
        self.assertEqual(response.status_code, 200)

    def test_400_wrong_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token 12589dfgsargre')
        response = self.client.post('/api/v1/logout')
        self.assertEqual(response.status_code, 401)
