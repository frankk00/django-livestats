from livestats.backends.input.base import LivestatsImport
import datetime
from livestats.models import Registration

class DjangoOrmLivestatsImport(LivestatsImport):

    def create_registration(self, type, value, entity, date):
            Registration.objects.create(type=type, value=value, entity=entity, date=date)