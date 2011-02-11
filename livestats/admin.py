# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   License      Copyright 2011 prinkk
   Filename     admin.py
'''

from django.contrib import admin
from models import *

class KPIGoalInline(admin.TabularInline):
    model = KPIGoal

class KPIAdmin(admin.ModelAdmin):
    list_display = ('title', 'template', 'order')
    inlines = [KPIGoalInline,]

class EntityAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'type', 'user')
    list_filter = ('type', )
    search_fields = ['full_name',]

admin.site.register(Entity, EntityAdmin)

class RegistrationTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'variable_name')

admin.site.register(RegistrationType, RegistrationTypeAdmin)

class RegistrationAdmin(admin.ModelAdmin):
    search_fields = ['unique_id', 'value']
    list_display = ('type', 'unique_id', 'value', 'entity', 'date')
    list_filter = ('type', 'entity')
    date_hierarchy = 'date'
    
admin.site.register(Registration, RegistrationAdmin)

class KPIHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'kpi', 'value', 'date_from', 'date_to')
    
admin.site.register(KPIHistory, KPIHistoryAdmin)
admin.site.register(KPI, KPIAdmin)

class MonitorTableKPIInline(admin.TabularInline):
    model = MonitorTableKPI
    
class MonitorBoxKPIInline(admin.TabularInline):
    model = MonitorBoxKPI
    exclude = ('date_start', 'end_date')

class MonitorAdmin(admin.ModelAdmin):
    inlines = [MonitorTableKPIInline, MonitorBoxKPIInline]
    list_display = ('title',)
    filter_horizontal = ['entities']

admin.site.register(Monitor, MonitorAdmin)

class MonitorCompetitionGoalInline(admin.TabularInline):
    model = MonitorCompetitionGoal

class MonitorCompetitionAdmin(admin.ModelAdmin):
    inlines = [MonitorCompetitionGoalInline,]
    
admin.site.register(MonitorCompetition, MonitorCompetitionAdmin)

admin.site.register(UserRegistrationAccess)
admin.site.register(Overview)
admin.site.register(EntityType)