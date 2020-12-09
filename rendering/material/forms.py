# from django import forms
# from . import models
# # #from dal import autocomplete
#
# class TextureForm(forms.ModelForm):
#     class Meta:
#         model = models.Finish
#         fields = ['id', 'url', 'pattern', 'w', 'h', 'dpi', 'archive'] #__all__#exclude
#         widgets = {
#             'url': forms.CharField(max_length=128),
# #            'pattern': autocomplete.ModelSelect2(url='pattern-autocomplete')
#         }
#
#         labels = {
#             'w': 'width',
#             'h': 'height',
#             'url': 'filename',
#         }
#         help_texts = {
#             'url': 'file name in filesystem'
#         }
