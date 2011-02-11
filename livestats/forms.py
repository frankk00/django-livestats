# -*- coding: utf-8 -*-
'''
   Created by   prinkk
   Developer    Kristian Øllegaard
   Mail         kristian@prinkk.net
   www          http://www.prinkk.net

   Date         23 10 2010

   License      Copyright 2010 prinkk
   Filename     forms.py
'''

from models import Registration, RegistrationType
from widgets import *
from django import forms

class RegistrationForm(forms.ModelForm):
    type = forms.ModelChoiceField(widget=MultipleSubmitButton,
        label="Type",
        queryset=RegistrationType.objects.none(),
        empty_label=None)
    def __init__(self, queryset, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = queryset
        
    class Meta:
        model = Registration
        exclude = ['entity', 'date', 'unique_id']