'''
Created on May 16, 2017

@author: Asus-PC
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

situs_berita = [('det','Detik.com'),('kom','Kompas.com'),('lip','Liputan6.com')]
class PostForm(forms.Form):
    keyword = forms.CharField(max_length=256)
    jumlah = forms.IntegerField()
    situs = forms.ChoiceField(choices=situs_berita, widget=forms.Select(attrs={'class': 'selectpicker'}))
    date_start = forms.CharField(max_length=11)
    date_end = forms.CharField(max_length=11)

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=100)
    file = forms.FileField()
    
class FormInputBerita(forms.Form):
    judul_berita = forms.CharField()
    konten_berita = forms.CharField(widget=forms.Textarea)
    
class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
    
 