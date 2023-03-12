import os
import sys

# Add the path to your project directory to the Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from django.core.management.base import BaseCommand
from climate.models import Colour


class Command(BaseCommand):
    help = 'Adds a new item to the database'

    def add_arguments(self, parser):
        parser.add_argument('colour_id', type=str, help='Name of the colour')
        parser.add_argument('colour_hex_val', type=str, help='Hex value of the colour')
        parser.add_argument('colour_cost', type=str, help='Cost to purchase this colour')

    def handle(self, *args, **options):
        colour = Colour(
            colour_id=options['colour_id'],
            colour_hex_val=options['colour_hex_val'],
            colour_cost=options['colour_cost']
        )
        colour.save()
        self.stdout.write(self.style.SUCCESS('Successfully added item "%s"' % colour.colour_id))
