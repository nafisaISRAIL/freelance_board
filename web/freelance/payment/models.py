from django.db import models
from datetime import datetime
import time

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
    def transfer(cls, client, freelancer, amount, status):
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        log = cls.objects.create(
            amount=amount,
            client_email=client.email,
            freelancer_email=freelancer.email,
            status=status,
            transaction_type='transfer',
            transaction_code=transaction_code
        )

        if log.status == 'success':
            client.freeze_balance -= amount
            freelancer.balance += amount
            client.save(update_fields=['freeze_balance'])
            freelancer.save(update_fields=['balance'])
        return log

    @classmethod
    def deposit(cls, client, amount, status):
        transaction_code = int(time.mktime(datetime.now().timetuple()))
        log = cls.objects.create(
            amount=amount,
            client_email=client.email,
            status=status,
            transaction_type='deposit',
            transaction_code=transaction_code
        )

        if log.status == 'success':
            client.balance += amount
            client.save(update_fields=['balance'])
        return log
