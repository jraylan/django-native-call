from django.db import models
from django.contrib.auth import get_user_model
import uuid


class FunctionCallCSRF(models.Model):
    function_name = models.CharField(max_length=100)
    authorization_token = models.CharField(max_length=36, unique=True)
    user = models.ForeignKey(
        get_user_model(),
        null=False,
        on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if not self.authorization_token:
            self.authorization_token = uuid.uuid4().hex
        return super(FunctionCallCSRF, self).save(*args, **kwargs)

