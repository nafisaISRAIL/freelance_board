from freelance.core.tests import APIViewTestCase
from freelance.account.models import User
from freelance.order.models import Order


class OrderTestCase(APIViewTestCase):
    def setUp(self):
        super(OrderTestCase, self).setUp()
        self.freelancer = User.objects.create(email='test@example.com', role='freelancer', password='qwerty')
        self.user_client = User.objects.create(email='client@example.com', role='client')
        self.user_client.set_password('qwerty')
        self.user_client.save()
        response = self.client.post('/api/v1/login', {'email': 'client@example.com', 'password':'qwerty'})
        self.client_token = response.data['token']

    def test_create_not_status_201(self):
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 120,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        response = self.client.post('/api/v1/orders', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'new')

    def test_create_with_status_201(self):
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 120,
            'status': 'new'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        response = self.client.post('/api/v1/orders', data)
        self.assertEqual(response.status_code, 201)

    def test_401(self):
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 120,
        }
        response = self.client.post('/api/v1/orders', data)
        self.assertEqual(response.status_code, 401)


class FreelancerRequestTestCase(APIViewTestCase):
    def setUp(self):
        super(FreelancerRequestTestCase, self).setUp()
        self.freelancer = User.objects.create(email='freelancer@example.com')
        self.freelancer.set_password('qwerty')
        self.freelancer.save()
        self.client_user = User.objects.create(email='client@example.com', password='qwerty')
        self.order = Order.objects.create(client=self.client_user, title='New', description='New', price=100, status='new')
        response = self.client.post('/api/v1/login', {
            'email': 'freelancer@example.com',
            'password': 'qwerty'
        })
        self.freelancer_token = response.data['token']

    def test_201_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.freelancer_token))
        response = self.client.post('/api/v1/orders/{}/freelancer_request'.format(self.order.id))
        self.assertEqual(response.status_code, 201)

    def test_401_unauthorized(self):
        response = self.client.post('/api/v1/orders/{}/freelancer_request'.format(self.order.id))
        self.assertEqual(response.status_code, 401)
