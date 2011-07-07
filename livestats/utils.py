# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     utils.py
'''

import datetime
import calendar
from django.template import Template, Context
import re
from decimal import Decimal
from models import MonitorBoxKPI, MonitorTableKPI, Registration

from django.template.defaultfilters import floatformat
from django.db.models import Avg, Max, Min, Count, Sum

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
                except Reigstration.DoesNotExist:
                    return 0

            if v.has_key("value"):
                return v["value"]
            else:
                return 0
        else:
            return 0


class DateInterval(object):
    
    def __init__(self, date=None):
        if not date:
            date = datetime.date.today()
        self.date = date
        
    def lastweek(self):
        return (datetime.datetime(year=self.date.year,
            month=self.date.month, day=self.date.day) - datetime.timedelta(days=5),
            datetime.datetime(year=self.date.year,
                month=self.date.month, day=self.date.day))
    
    def week(self):
        monday = self.date - datetime.timedelta(days=(calendar.weekday(self.date.year, self.date.month ,self.date.day)))
        sunday = monday + datetime.timedelta(days=6)
        return (monday, sunday)
        
    def month(self):
        return (self.date.replace(day=1), self.date.replace(day=calendar.monthrange(self.date.year, self.date.month)[1]))
        
    def year(self):
        return (self.date.replace(day=1, month=1), self.date.replace(day=31, month=12))