from django.contrib import admin
from .models import Game, Question, StudentAttempt

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'game_type', 'min_grade', 'is_active')
    list_filter = ('game_type', 'subject', 'min_grade')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Question)
admin.site.register(StudentAttempt)