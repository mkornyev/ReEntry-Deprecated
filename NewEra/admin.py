from django.contrib import admin

# Import models
from .models import User, CaseLoadUser, Referral, Resource, Tag

# Register models
admin.site.register(User)
admin.site.register(CaseLoadUser)
admin.site.register(Referral)
admin.site.register(Resource)
admin.site.register(Tag)