from django.core.management.base import BaseCommand
from vaccinations.models import VaccineTargetSpecies

class Command(BaseCommand):
    help = 'Seeds VaccineTargetSpecies with default species'

    def handle(self, *args, **kwargs):
        species_list = ['cattle', 'goat', 'sheep', 'poultry', 'other']
        for species in species_list:
            obj, created = VaccineTargetSpecies.objects.get_or_create(species=species)
            if created:
                self.stdout.write(f'Created species: {species}')
            else:
                self.stdout.write(f'Already exists: {species}')
        self.stdout.write(self.style.SUCCESS('Species seeding complete!'))