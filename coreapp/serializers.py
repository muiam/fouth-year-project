from django.core.serializers.json import DjangoJSONEncoder
from coreapp.models import Category,User

class CategoryJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return {'id': obj.id, 'name': obj.name}
        return super().default(obj)

class UserJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return {'id': obj.id, 'name': obj.email}
        return super().default(obj)
