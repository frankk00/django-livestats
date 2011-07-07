import datetime
from operator import attrgetter
from django.template.defaultfilters import floatformat
from base import LivestatsBackend
from livestats.models import MonitorBoxKPI, RegistrationType, MonitorTableKPI, Registration
from livestats.utils import DateInterval
from django.core.cache import cache
import re
from django.template import Template, Context
from decimal import Decimal
CACHE_EXPIRATION_LIVEUPDATE = 60 * 5
CACHE_EXPIRATION_HISTORYUPDATE = 60 * 60

class Stats(object):
    kpi = []

    def getColor(self, kpi, data):
        goal = kpi.kpigoal_set.filter(value__lte=data)
        if goal.count() > 0:
            return goal.order_by('-value')[0].color
        elif kpi.kpigoal_set.all().count() > 0:
            return kpi.kpigoal_set.all().order_by('-value')[0].color
        else:
            return "grey"

    def __init__(self, kpis, queryset=None, order_by=None, date=None, manual_date=False):
        """ kpis = kpi list queryset=registrations, order_by=kpi obj"""
        if not date:
            date = datetime.date.today()
        self.kpi = []
        for kpitype in kpis:
            if isinstance(kpitype, (MonitorBoxKPI, MonitorTableKPI)):
                kpi = kpitype.kpi
                if not manual_date:
                    if isinstance(kpitype, (MonitorBoxKPI, )) and kpitype.default_period == "WEEKLY":
                        qs = queryset.filter(date__range=(DateInterval(date).week()))
                    elif isinstance(kpitype, (MonitorBoxKPI, )) and kpitype.default_period == "MONTHLY":
                        qs = queryset.filter(date__range=(DateInterval(date).month()))
                    elif isinstance(kpitype, (MonitorBoxKPI, )) and kpitype.default_period == "YEARLY":
                        qs = queryset.filter(date__range=(DateInterval(date).year()))
                    else:
                        qs = queryset.filter(date__day=date.day, date__month=date.month, date__year=date.year)
                else:
                    qs = queryset
            else:
                kpi = kpitype
                qs = queryset
            data = self.calculate(kpi, qs)
            self.kpi.append({
                'id': kpitype.id,
                'data': floatformat(data[0], kpi.decimal_places),
                'data_u': data[0], # data unformatted
                'subtitle_data': data[1],
                'prefix': kpi.prefix,
                'suffix': kpi.suffix,
                'color': self.getColor(kpi, data[0]),
                'title': kpi.title,
            })
            if order_by == kpi:
                self.order_by = data

    def calculate(self, kpi, queryset):
        content = Template(kpi.template)
        subtitle_content = Template(kpi.subtitle_template)
        d = {}
        for value in kpi.registrationtypes.all():
            d[value.variable_name.lower()] = self.regvalue(value, queryset)
        number = re.compile(r"((\b|(?=\W))(\d+(\.\d*)?|\.\d+)([eE][+-]?\d{1,3})?)")
        deciexpr = lambda s: number.sub(r"Decimal('\1')", s)
        try:
            return [eval(deciexpr(content.render(Context(d)).replace(",", "."))), subtitle_content.render(Context(d))]
        except:
            #TODO: Better handling here!
            return [0, 0]

    def regvalue(self, registrationtype, queryset):
        if queryset:
            queryset = queryset.filter(type=registrationtype)
            if queryset.count() == 0:
                return 0
            if registrationtype.type == "SUM":
                v = queryset.aggregate(value=Sum('value'))
            elif registrationtype.type == "AVG":
                v = queryset.aggregate(value=Avg('value'))
            elif registrationtype.type == "COUNT":
                v = queryset.aggregate(value=Count('value'))
            elif registrationtype.type =="LATEST":
                try:
                    return queryset.order_by('-date')[0].value
                except Registration.DoesNotExist:
                    return 0

            if v.has_key("value"):
                return v["value"]
            else:
                return 0
        else:
            return 0

class DjangoOrmBackend(LivestatsBackend):

    def return_dict(self):
        # Get all entities for current monitor
        reg_entities = self.monitor.entities.all()
        # Get RegistrationType objects from monitor
        regtypes = RegistrationType.objects.filter(kpi__monitorkpi__monitor=self.monitor)
        # Get tablecolumns for monitor
        tablecolumns = MonitorTableKPI.objects.filter(monitor=self.monitor)
        # Get KPI Boxes for monitor
        boxes = MonitorBoxKPI.objects.filter(monitor=self.monitor).order_by('order')
        # Assume the date is given manually, if set to false later, it will make
        # the KPI boxes make their own date interval, based in the current date
        manual_date= True

        # Check if the page should live update and generate a Registraion queryset,
        # based on the date from the url and use it as a manual date
        day, month, year = self.day, self.month, self.year
        if day and month and year:
            live_update = False
            reg = Registration.objects.filter(date__day=day, date__month=month, date__year=year)
            serial = "%s%s%s" % (day, month, year)
        elif month and year:
            if int(month) == datetime.date.today().month and int(year) == datetime.date.today().year:
                live_update = True
            else:
                live_update = False
            reg = Registration.objects.filter(date__month=month, date__year=year)
            serial = "%s%s%s" % (0, month, year)
        else:
            date = datetime.date.today()
            serial = "%s%s%s" % (date.day, date.month, date.year)
            reg = Registration.objects.filter(date__day=date.day, date__month=date.month, date__year=date.year)
            live_update = True
            manual_date = False

        if not reg.count() > 0:
            return {}

        cache_key = "monitor-%s-%s" % (self.monitor.id, serial)
        cache_key_number = "monitor-%s-%s-id" % (self.monitor.id, serial)

        if not cache.get(cache_key) or reg.order_by('-id')[0].id != cache.get(cache_key_number):
            # Create KPI boxes
            if manual_date:
                stats = Stats(MonitorBoxKPI.objects.filter(monitor=self.monitor).order_by('-order'), reg.filter(entity__in=reg_entities), manual_date=manual_date)
            else:
                stats = Stats(MonitorBoxKPI.objects.filter(monitor=self.monitor).order_by('-order'), Registration.objects.filter(entity__in=reg_entities))
            stats.monitor = self.monitor


            # Create data for table
            entities = []
            if self.monitor.show_table:
                for entity in reg_entities:
                    entity_reg = reg.filter(entity=entity, type__in=regtypes)
                    if entity_reg:
                        agstats = Stats(tablecolumns, entity_reg, self.monitor.order_by, manual_date=manual_date)
                        agstats.entity = entity
                        entities.append(agstats)
                entities = sorted(entities, key=attrgetter('order_by'), reverse=True)

            # Provide an <html> and <body> tag if not ajax, to make compatible with django debug toolbar

            if live_update:
                cachetime = CACHE_EXPIRATION_LIVEUPDATE
            else:
                cachetime = CACHE_EXPIRATION_HISTORYUPDATE

            cache.set(cache_key, {'summary': stats, 'entities': entities, 'html': False}, cachetime)
            cache.set(cache_key_number, reg.order_by('-id')[0].id, cachetime)
            return cache.get(cache_key)
        else:
            return cache.get(cache_key)

    def