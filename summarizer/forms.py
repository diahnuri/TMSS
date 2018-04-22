from django import forms


class FormInputBerita(forms.Form):
    judul_berita = forms.CharField()
    konten_berita = forms.CharField(widget=forms.Textarea)