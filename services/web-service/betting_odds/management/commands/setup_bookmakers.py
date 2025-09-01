from django.core.management.base import BaseCommand
from betting_odds.models import BookmakerProvider

class Command(BaseCommand):
    help = 'Setup initial bookmaker providers'

    def handle(self, *args, **options):
        bookmakers = [
            {
                'name': 'The Odds API',
                'api_endpoint': 'https://api.the-odds-api.com/v4',
                'api_key_required': True,
                'rate_limit_per_minute': 500,
                'is_active': True,
                'reliability_score': 0.9
            },
            {
                'name': 'Bet365',
                'api_endpoint': 'https://api.bet365.com',
                'api_key_required': True,
                'rate_limit_per_minute': 100,
                'is_active': False,  # Would need actual API access
                'reliability_score': 0.95
            },
            {
                'name': 'Betfair',
                'api_endpoint': 'https://api.betfair.com',
                'api_key_required': True,
                'rate_limit_per_minute': 200,
                'is_active': False,  # Would need actual API access
                'reliability_score': 0.93
            },
            {
                'name': 'Pinnacle',
                'api_endpoint': 'https://api.pinnacle.com',
                'api_key_required': True,
                'rate_limit_per_minute': 120,
                'is_active': False,  # Would need actual API access
                'reliability_score': 0.91
            },
            {
                'name': 'William Hill',
                'api_endpoint': 'https://api.williamhill.com',
                'api_key_required': True,
                'rate_limit_per_minute': 60,
                'is_active': False,  # Would need actual API access
                'reliability_score': 0.87
            }
        ]

        created_count = 0
        updated_count = 0

        for bookmaker_data in bookmakers:
            bookmaker, created = BookmakerProvider.objects.get_or_create(
                name=bookmaker_data['name'],
                defaults=bookmaker_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created bookmaker: {bookmaker.name}')
                )
            else:
                # Update existing bookmaker with new data
                for key, value in bookmaker_data.items():
                    if key != 'name':  # Don't update the name
                        setattr(bookmaker, key, value)
                bookmaker.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated bookmaker: {bookmaker.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Setup completed: {created_count} created, {updated_count} updated'
            )
        )
        
        # Display current status
        self.stdout.write('\nCurrent bookmaker status:')
        for bookmaker in BookmakerProvider.objects.all():
            status = "Active" if bookmaker.is_active else "Inactive"
            self.stdout.write(f'• {bookmaker.name}: {status} (Reliability: {bookmaker.reliability_score})')
        
        self.stdout.write(
            self.style.WARNING(
                '\nNote: Only "The Odds API" is configured as active. '
                'Other bookmakers require API keys and specific integrations.'
            )
        )
