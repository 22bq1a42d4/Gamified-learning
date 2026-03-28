from django.contrib import admin
from .models import Level, Badge, StudentXP, SubjectXP, XPLog, StudentBadge

admin.site.register(Level)
admin.site.register(Badge)
admin.site.register(StudentXP)
admin.site.register(SubjectXP)
admin.site.register(XPLog)
admin.site.register(StudentBadge)