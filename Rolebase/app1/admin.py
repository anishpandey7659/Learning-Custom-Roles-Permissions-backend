# Register your models here.
from django.contrib import admin
from .models import User
# If you want to edit staffProfile inline when editing a User

admin.site.register(User)