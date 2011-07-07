from livestats.models import Monitor
import datetime
from django.template import Template, Context
import re

class LivestatsBackend(object):
    def __init__(self, monitor, day=None, month=None, year=None):
        self.monitor = Monitor.objects.get(pk=monitor)
        self.day = day
        self.month = month
        self.year = year

        self.kpi = [] # This must be filled with the dictionary of items
        self.entities = [] # This must be filled with the dictionary of items

    def calculate(self, values, template, subtitle_template=None):
        template = Template(template)
        if subtitle_template:
            subtitle_template = Template(subtitle_template)
        number = re.compile(r"((\b|(?=\W))(\d+(\.\d*)?|\.\d+)([eE][+-]?\d{1,3})?)")
        deciexpr = lambda s: number.sub(r"Decimal('\1')", s)
        try:
            if subtitle_template:
                return [eval(deciexpr(template.render(Context(values)).replace(",", "."))), subtitle_template.render(Context(values))]
            else:
                return [eval(deciexpr(template.render(Context(values)).replace(",", "."))), 0]
        except:
            return [0, 0]

    def return_dict(self):
        raise Exception("Subclasses of LivestatsBackend must define a return_dict function")