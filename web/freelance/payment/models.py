from django.db import models
from django.db.models import F
from datetime import datetime
import time
from freelance.account.models import User

STATUS = (
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('pending', 'Pending')
)

TRANSACTION_TYPE = (
    ('transfer', 'Transfer'),
    ('deposit', 'Deposit'),
)


class TransactionLog(models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    client_email = models.CharField(max_length=50)
    freelancer_email = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, choices=STATUS)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    transaction_code = models.CharField(max_length=50, unique=True)

    @classmethod
    def transfer(cls, client_email, freelancer_email, amount, status):
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        log = cls.objects.create(
            amount=amount,
            client_email=client_email,
            freelancer_email=freelancer_email,
            status=status,
            transaction_type='transfer',
            transaction_code=transaction_code
        )
        client = User.objects.select_for_update().filter(email=client_email)
        freelancer = User.objects.select_for_update().filter(email=freelancer_email)
        if log.status == 'success' and client and freelancer:
            client.update(freeze_balance=F('freeze_balance') - amount)
            freelancer.update(balance=F('balance') + amount)
        return log

    @classmethod
    def deposit(cls, client_email, amount, status):
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        log = cls.objects.create(
            amount=amount,
            client_email=client_email,
            status=status,
            transaction_type='deposit',
            transaction_code=transaction_code
        )

        client = User.objects.select_for_update().filter(email=email).first()
        if log.status == 'success' and client:
            client.update(balance=F('balance') + amount)
        return log
