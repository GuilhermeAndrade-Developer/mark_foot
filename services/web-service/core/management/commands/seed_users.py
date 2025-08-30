"""
Seeder for test users in development environment.
Creates realistic test users with different profiles and relationships.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
import string


class Command(BaseCommand):
    help = 'Create test users for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of users to create (default: 20)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing test users first',
        )

    def handle(self, *args, **options):
        if options['reset']:
            # Delete test users (keep admin users)
            User.objects.filter(
                username__startswith='user_',
                is_superuser=False
            ).delete()
            self.stdout.write('🧹 Cleared existing test users')

        count = options['count']
        created_count = 0

        # Predefined user data for more realistic profiles
        user_profiles = [
            ('João', 'Silva', 'joao.silva'),
            ('Maria', 'Santos', 'maria.santos'),
            ('Pedro', 'Oliveira', 'pedro.oliveira'),
            ('Ana', 'Costa', 'ana.costa'),
            ('Carlos', 'Ferreira', 'carlos.ferreira'),
            ('Lucia', 'Rodrigues', 'lucia.rodrigues'),
            ('Rafael', 'Almeida', 'rafael.almeida'),
            ('Patricia', 'Lima', 'patricia.lima'),
            ('Fernando', 'Pereira', 'fernando.pereira'),
            ('Juliana', 'Carvalho', 'juliana.carvalho'),
            ('Roberto', 'Machado', 'roberto.machado'),
            ('Sandra', 'Barbosa', 'sandra.barbosa'),
            ('Thiago', 'Ribeiro', 'thiago.ribeiro'),
            ('Camila', 'Martins', 'camila.martins'),
            ('Diego', 'Araújo', 'diego.araujo'),
            ('Renata', 'Fernandes', 'renata.fernandes'),
            ('Gabriel', 'Moura', 'gabriel.moura'),
            ('Beatriz', 'Nascimento', 'beatriz.nascimento'),
            ('Lucas', 'Cardoso', 'lucas.cardoso'),
            ('Priscila', 'Ramos', 'priscila.ramos'),
        ]

        # Extend the list if we need more users
        while len(user_profiles) < count:
            first_names = [
                'Alexandre', 'André', 'Antonio', 'Bruno', 'César', 'Daniel', 'Eduardo', 'Fabio',
                'Guilherme', 'Henrique', 'Igor', 'José', 'Leonardo', 'Marcos', 'Mateus', 'Ricardo',
                'Adriana', 'Amanda', 'Carolina', 'Cristina', 'Daniela', 'Fernanda', 'Giovana',
                'Isabella', 'Jessica', 'Kelly', 'Larissa', 'Monica', 'Natalia', 'Roberta'
            ]
            last_names = [
                'Alves', 'Azevedo', 'Batista', 'Campos', 'Dias', 'Freitas', 'Gomes', 'Lopes',
                'Medeiros', 'Neves', 'Pinto', 'Rocha', 'Sousa', 'Teixeira', 'Vieira'
            ]
            
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}.{last.lower()}"
            user_profiles.append((first, last, username))

        for i in range(count):
            first_name, last_name, base_username = user_profiles[i]
            
            # Ensure unique username
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            email = f"{username}@markfoot.dev"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password='test123',  # Standard test password
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_staff=False,
            )
            
            # Set random join date (last 6 months)
            user.date_joined = timezone.now() - timedelta(
                days=random.randint(1, 180)
            )
            user.save()
            
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Created {created_count} test users\n'
                f'   Username pattern: firstname.lastname\n'
                f'   Password: test123\n'
                f'   Email: username@markfoot.dev'
            )
        )

        # Show some examples
        if created_count > 0:
            sample_users = User.objects.filter(
                username__contains='.',
                is_superuser=False
            ).order_by('?')[:3]
            
            self.stdout.write('\n📋 Sample users created:')
            for user in sample_users:
                self.stdout.write(f'   👤 {user.username} ({user.get_full_name()})')
