from django.db import models
from django.db.models import F
from django.conf import settings
from freelance.account.models import User

STATUS = (
    ('new', 'New'),
    ('active', 'Active'),
    ('finished', 'Finished'),
    ('canceled', 'Canceled'),
)


class Order(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='client', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(
        max_length=50, choices=STATUS, default=STATUS[0][0])
    price = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='order_freelancer', on_delete=models.CASCADE, null=True)
    approved = models.BooleanField(default=False)

    def activate(self, freelancer):
        self.freelancer = freelancer
        self.status = 'active'
        User.objects.select_for_update().filter(
            id=self.client.id).update(
            balance=F('balance') - self.price, freeze_balance=F('freeze_balance') + self.price)
        self.save(update_fields=['status', 'freelancer'])


class FreelancerRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='request')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='freelancer',
                                   on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
