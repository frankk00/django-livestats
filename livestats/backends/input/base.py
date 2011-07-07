from livestats.models import RegistrationType, Entity
import datetime

class LivestatsImport(object):

    entity_type = None
    aggregation_type = "COUNT"

    def __init__(self):
        pass

    def bulk_import(self, lst):
        for entity, type, value in lst:
            e, created = Entity.objects.get_or_create(type=self.entity_type, name=entity)
            if isinstance(type, list):
                variable_name = "_".join(type)
            else:
                variable_name = type
            rt = RegistrationType.objects.filter(variable_name=variable_name)
            if rt.count() > 0:
                    rt = rt[0]
            else:
                    rt = RegistrationType.objects.create(variable_name=variable_name,\
                                                         title=variable_name,\
                                                         type=self.aggregation_type)
            self.create_registration(rt, value, e, datetime.datetime.now())

    def create_registration(self, type, value, entity, date):
        raise Exception("Please implement a create_registration function on the custom backend you are using")