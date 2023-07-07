from django.contrib import admin

from lottery.models import RoundInfo, Ticket, RoundWinners, RoundDetail


@admin.register(RoundInfo)
class RoundInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'previous_round', 'ticket_count', 'ticket_amount', 'total_price', 'burn_amount',
                    'is_done', 'created_at']
    search_fields = ['number', 'ticket_goal']
    list_filter = ['is_done']
    ordering = ['-number']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'round', 'user', 'number', 'is_active', 'created_at']
    search_fields = ['user', 'round__number', 'number']
    list_filter = ['is_active']
    ordering = ['-created_at']


@admin.register(RoundDetail)
class RoundDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'count', 'round', 'ratio', 'type', 'total_amount']
    search_fields = ['round__number']
    list_filter = ['type']
    ordering = ['-round__number']


@admin.register(RoundWinners)
class RoundWinnersAdmin(admin.ModelAdmin):
    list_display = ['id', 'winner_count', 'type', 'round', 'is_processed']
    search_fields = ['round__number']
    list_filter = ['is_processed', 'type']
    ordering = ['-round__number']
