from django.contrib import admin

from lottery.models import RoundInfo, Ticket, RoundWinners, RoundWinnerDetail


@admin.register(RoundInfo)
class RoundInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'previous_round', 'ticket_count', 'total_amount', 'burn_amount', 'is_done', 'lock_at',
                    'created_at']
    search_fields = ['number']
    list_filter = ['is_done']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'round', 'user', 'amount', 'number', 'is_active', 'created_at']
    search_fields = ['user', 'round']
    list_filter = ['is_active']


@admin.register(RoundWinnerDetail)
class RoundWinnerDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'count', 'round', 'type', 'total_amount']
    search_fields = ['round', 'type']
    list_filter = ['type']


@admin.register(RoundWinners)
class RoundWinnersAdmin(admin.ModelAdmin):
    list_display = ['id', 'winner_count', 'type', 'round', 'is_processed']
    search_fields = ['round']
    list_filter = ['is_processed', 'type']
