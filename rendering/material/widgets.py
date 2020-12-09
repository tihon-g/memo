# class ColorPickerWidget(forms.widgets.TextInput):
#
#     class Media:
#         css = {
#             'all': ('/static/farbtastic/farbtastic.css',)
#             }
#         js = ('/static/farbtastic/colorpicker.js',
#               '/static/farbtastic/farbtastic.js',)
#
#     def render(self, name, value, attrs=None):
#         text_input_html = super(ColorPickerWidget, self).render(name, value, attrs)
#         text_link_html = u'<a id="id_color_picker" href="#" onclick="return false;">%s</a>' % _(u'Palette')
#         return mark_safe('%s %s' % (text_input_html, text_link_html))