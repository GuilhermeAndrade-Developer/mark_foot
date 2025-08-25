from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Player
import requests
import os
import hashlib
from urllib.parse import urlparse
import time


class Command(BaseCommand):
    help = 'Optimize and cache player media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['download-images', 'validate-urls', 'cleanup-cache', 'image-stats'],
            default='image-stats',
            help='Media optimization action to perform'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of images to process'
        )

    def handle(self, *args, **options):
        action = options['action']
        
        self.stdout.write(
            self.style.SUCCESS('🖼️ Mark Foot - Media Optimizer')
        )
        self.stdout.write('=' * 50)
        
        if action == 'download-images':
            self.download_player_images(options)
        elif action == 'validate-urls':
            self.validate_image_urls(options)
        elif action == 'cleanup-cache':
            self.cleanup_image_cache()
        elif action == 'image-stats':
            self.show_image_statistics()

    def show_image_statistics(self):
        """Show statistics about player images"""
        self.stdout.write(f'\n📊 Player Image Statistics')
        self.stdout.write('-' * 40)
        
        total_players = Player.objects.count()
        
        # Image availability
        with_photo = Player.objects.exclude(photo_url__exact='').exclude(photo_url__isnull=True).count()
        with_cutout = Player.objects.exclude(cutout_url__exact='').exclude(cutout_url__isnull=True).count()
        
        self.stdout.write(f'\n📈 Image Availability:')
        self.stdout.write(f'  • Total Players: {total_players}')
        self.stdout.write(f'  • With Photo URLs: {with_photo} ({(with_photo/total_players)*100:.1f}%)')
        self.stdout.write(f'  • With Cutout URLs: {with_cutout} ({(with_cutout/total_players)*100:.1f}%)')
        
        # Show sample URLs
        sample_players = Player.objects.exclude(photo_url__exact='').exclude(photo_url__isnull=True)[:3]
        
        if sample_players.exists():
            self.stdout.write(f'\n🖼️ Sample Image URLs:')
            for player in sample_players:
                self.stdout.write(f'  • {player.name}:')
                if player.photo_url:
                    self.stdout.write(f'    📷 Photo: {player.photo_url[:60]}...')
                if player.cutout_url:
                    self.stdout.write(f'    ✂️ Cutout: {player.cutout_url[:60]}...')

    def validate_image_urls(self, options):
        """Validate that image URLs are accessible"""
        limit = options.get('limit', 10)
        
        self.stdout.write(f'\n🔍 Validating Image URLs (limit: {limit})')
        self.stdout.write('-' * 50)
        
        players_with_images = Player.objects.exclude(
            photo_url__exact=''
        ).exclude(photo_url__isnull=True)[:limit]
        
        if not players_with_images.exists():
            self.stdout.write('❌ No players with image URLs found')
            return
        
        valid_photos = 0
        valid_cutouts = 0
        total_checked = 0
        
        for player in players_with_images:
            self.stdout.write(f'\n👤 Checking: {player.name}')
            
            # Check photo URL
            if player.photo_url:
                if self._validate_url(player.photo_url):
                    self.stdout.write(f'  📷 Photo: ✅ Valid')
                    valid_photos += 1
                else:
                    self.stdout.write(f'  📷 Photo: ❌ Invalid or unreachable')
            
            # Check cutout URL
            if player.cutout_url:
                if self._validate_url(player.cutout_url):
                    self.stdout.write(f'  ✂️ Cutout: ✅ Valid')
                    valid_cutouts += 1
                else:
                    self.stdout.write(f'  ✂️ Cutout: ❌ Invalid or unreachable')
            
            total_checked += 1
            
            # Rate limiting for external requests
            time.sleep(0.5)
        
        self.stdout.write(f'\n📊 Validation Results:')
        self.stdout.write(f'  • Players Checked: {total_checked}')
        self.stdout.write(f'  • Valid Photos: {valid_photos}')
        self.stdout.write(f'  • Valid Cutouts: {valid_cutouts}')

    def download_player_images(self, options):
        """Download and cache player images locally"""
        limit = options.get('limit', 10)
        
        self.stdout.write(f'\n⬇️ Downloading Player Images (limit: {limit})')
        self.stdout.write('-' * 50)
        
        # Create cache directory
        cache_dir = '/app/storage/player_images'
        os.makedirs(cache_dir, exist_ok=True)
        
        players_with_images = Player.objects.exclude(
            photo_url__exact=''
        ).exclude(photo_url__isnull=True)[:limit]
        
        if not players_with_images.exists():
            self.stdout.write('❌ No players with image URLs found')
            return
        
        downloaded = 0
        skipped = 0
        failed = 0
        
        for player in players_with_images:
            self.stdout.write(f'\n👤 Processing: {player.name}')
            
            # Download photo
            if player.photo_url:
                result = self._download_image(player.photo_url, cache_dir, f'{player.external_id}_photo')
                if result == 'downloaded':
                    self.stdout.write(f'  📷 Photo: ✅ Downloaded')
                    downloaded += 1
                elif result == 'exists':
                    self.stdout.write(f'  📷 Photo: ⏭️ Already cached')
                    skipped += 1
                else:
                    self.stdout.write(f'  📷 Photo: ❌ Failed')
                    failed += 1
            
            # Download cutout
            if player.cutout_url:
                result = self._download_image(player.cutout_url, cache_dir, f'{player.external_id}_cutout')
                if result == 'downloaded':
                    self.stdout.write(f'  ✂️ Cutout: ✅ Downloaded')
                    downloaded += 1
                elif result == 'exists':
                    self.stdout.write(f'  ✂️ Cutout: ⏭️ Already cached')
                    skipped += 1
                else:
                    self.stdout.write(f'  ✂️ Cutout: ❌ Failed')
                    failed += 1
            
            # Rate limiting
            time.sleep(1)
        
        self.stdout.write(f'\n📊 Download Results:')
        self.stdout.write(f'  • Downloaded: {downloaded}')
        self.stdout.write(f'  • Skipped (cached): {skipped}')
        self.stdout.write(f'  • Failed: {failed}')

    def cleanup_image_cache(self):
        """Clean up cached images for players no longer in database"""
        self.stdout.write(f'\n🧹 Cleaning Image Cache')
        self.stdout.write('-' * 30)
        
        cache_dir = '/app/storage/player_images'
        
        if not os.path.exists(cache_dir):
            self.stdout.write('❌ Cache directory does not exist')
            return
        
        # Get all external IDs from database
        existing_ids = set(Player.objects.values_list('external_id', flat=True))
        
        # Check cached files
        cached_files = os.listdir(cache_dir)
        removed_count = 0
        
        for filename in cached_files:
            # Extract player ID from filename
            if '_' in filename:
                player_id = filename.split('_')[0]
                
                if player_id not in existing_ids:
                    file_path = os.path.join(cache_dir, filename)
                    os.remove(file_path)
                    self.stdout.write(f'🗑️ Removed: {filename}')
                    removed_count += 1
        
        self.stdout.write(f'\n📊 Cleanup Results:')
        self.stdout.write(f'  • Files Removed: {removed_count}')
        self.stdout.write(f'  • Cache Directory: {cache_dir}')

    def _validate_url(self, url: str) -> bool:
        """Validate that a URL is accessible"""
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False

    def _download_image(self, url: str, cache_dir: str, filename_base: str) -> str:
        """
        Download image from URL and cache locally
        
        Returns:
            'downloaded', 'exists', or 'failed'
        """
        try:
            # Get file extension from URL
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
            
            # Generate filename
            filename = f"{filename_base}{ext}"
            file_path = os.path.join(cache_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                return 'exists'
            
            # Download image
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save to cache
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return 'downloaded'
            
        except Exception as e:
            return 'failed'
