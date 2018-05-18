from freelance.core.tests import APIViewTestCase
from freelance.account.models import User
from freelance.order.models import Order
from freelance.payment.models import TransactionLog
from datetime import datetime
import time


class OrderTestCase(APIViewTestCase):
    def setUp(self):
        super(OrderTestCase, self).setUp()
        self.freelancer = User.objects.create(email='test@example.com', role='freelancer', password='qwerty')
        self.user_client = User.objects.create(email='client@example.com', role='client')
        self.user_client.set_password('qwerty')
        self.user_client.balance = 100
        self.user_client.save()
        response = self.client.post('/api/v1/login', {'email': 'client@example.com', 'password': 'qwerty'})
        self.client_token = response.data['token']

    def test_create_not_status_201(self):
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 20,
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        response = self.client.post('/api/v1/orders', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'new')

    def test_create_with_status_201(self):
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 20,
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

    def test_400_low_balance(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        data = {
            'title': 'new order',
            'description': 'new order description',
            'price': 120,
        }
        response = self.client.post('/api/v1/orders', data)
        self.assertEqual(response.status_code, 400)


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


class ClientApproveTestCase(APIViewTestCase):
    def setUp(self):
        super(ClientApproveTestCase, self).setUp()
        self.freelancer = User.objects.create(email='freelancer@example.com')
        self.client_user = User.objects.create(email='client@example.com')
        self.client_user.set_password('qwerty')
        self.client_user.balance = 1000
        self.client_user.freeze_balance = 1000
        self.client_user.save()
        self.order = Order.objects.create(client=self.client_user, title='New', description='New', price=100, status='new')
        self.order2 = Order.objects.create(client=self.client_user, freelancer=self.freelancer, title='New2', description='New2', price=100, status='new')
        response = self.client.post('/api/v1/login', {
            'email': 'client@example.com',
            'password': 'qwerty'
        })
        self.client_token = response.data['token']

        self.client_2 = User.objects.create(email='client2@example.com')
        self.client_2.set_password('qwerty')
        self.client_2.save()
        response = self.client.post('/api/v1/login', {
            'email': 'client2@example.com',
            'password': 'qwerty'
        })
        self.client2_token = response.data['token']

    def test_200(self):
        old_balance = self.client_user.balance
        old_freeze_balance = self.client_user.freeze_balance
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        data = {
            'freelancer': self.freelancer.id
        }
        response = self.client.post('/api/v1/users/{}/orders/{}/approve_freelancer_request'.format(self.client_user.id, self.order.id), data)
        self.assertEqual(response.status_code, 200)
        client = User.objects.get(id=self.client_user.id)
        self.assertEqual(client.balance, old_balance - self.order.price)
        self.assertEqual(client.freeze_balance, old_freeze_balance + self.order.price)


    def test_403(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client2_token))
        data = {
            'freelancer': self.freelancer.id
        }
        response = self.client.post('/api/v1/users/{}/orders/{}/approve_freelancer_request'.format(self.client_user.id, self.order.id), data)
        self.assertEqual(response.status_code, 403)

    def test_400_low_balance(self):
        self.client_user.freeze_balance = 0
        self.client_user.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        data = {
            'freelancer': self.freelancer.id
        }
        response = self.client.post('/api/v1/users/{}/orders/{}/approve_freelancer_request'.format(self.client_user.id, self.order.id), data)
        self.assertEqual(response.status_code, 400)

    def test_400_exists_freelancer(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        data = {
            'freelancer': self.freelancer.id
        }
        response = self.client.post('/api/v1/users/{}/orders/{}/approve_freelancer_request'.format(self.client_user.id, self.order2.id), data)
        self.assertEqual(response.status_code, 400)

    def test_400_not_freelancer(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        response = self.client.post('/api/v1/users/{}/orders/{}/approve_freelancer_request'.format(self.client_user.id, self.order.id))
        self.assertEqual(response.status_code, 400)


class UpdateOrderTestCase(APIViewTestCase):
    def setUp(self):
        super(UpdateOrderTestCase, self).setUp()
        self.freelancer = User.objects.create(email='freelancer@example.com')
        self.client_user = User.objects.create(email='client@example.com')
        self.client_user.set_password('qwerty')
        self.client_user.freeze_balance = 1000
        self.client_user.save()
        self.order = Order.objects.create(client=self.client_user, freelancer=self.freelancer, title='New', description='New', price=100, status='new')
        response = self.client.post('/api/v1/login', {
            'email': 'client@example.com',
            'password': 'qwerty'
        })
        self.client_token = response.data['token']
        self.client_2 = User.objects.create(email='client2@example.com')
        self.client_2.set_password('qwerty')
        self.client_2.save()
        response = self.client.post('/api/v1/login', {
            'email': 'client2@example.com',
            'password': 'qwerty'
        })
        self.client2_token = response.data['token']

    def test_200_status_finished(self):
        data = {
            'status': 'finished'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client_token))
        response = self.client.patch('/api/v1/orders/{}'.format(self.order.id), data)
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        self.assertEqual(response.status_code, 200)
        log = TransactionLog.objects.get(transaction_code=transaction_code)
        self.assertEqual(log.amount, self.order.price)
        self.assertEqual(log.client_email, self.order.client.email)
        self.assertEqual(log.freelancer_email, self.order.freelancer.email)
        self.assertEqual(log.transaction_type, 'transfer')

        client = User.objects.get(id=self.client_user.id)
        freelancer = User.objects.get(id=self.freelancer.id)

        self.assertEqual(client.freeze_balance, self.client_user.freeze_balance - self.order.price)
        self.assertEqual(freelancer.balance, self.freelancer.balance + self.order.price)

    def test_403(self):
        data = {
            'status': 'finished'
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.client2_token))
        response = self.client.patch('/api/v1/orders/{}'.format(self.order.id), data)
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        self.assertEqual(response.status_code, 403)
