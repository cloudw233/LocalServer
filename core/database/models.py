from tortoise.models import Model
from tortoise import fields

class User(Model):
    username = fields.CharField(max_length=50, pk=True)
    password = fields.CharField(max_length=50)
    warning = fields.BooleanField()

    def __str__(self):
        return self.username

    class Meta:
        table = "users"

    async def verify(self, password: str) -> bool:
        return self.password == password