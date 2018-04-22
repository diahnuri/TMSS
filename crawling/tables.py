'''
Created on Jul 27, 2017

@author: Asus-PC
'''
import django_tables2 as tables

from .models import Tabel_Berita

class CheckBoxColumnWithName(tables.CheckBoxColumn):
    @property
    def header(self):
        return self.verbose_name

class Berita_Tabel(tables.Table):
    amend = CheckBoxColumnWithName(verbose_name=('ceklist'), accessor='pk')
    class Meta:
        model = Tabel_Berita
        attrs = {'class': 'paleblue'}

   

