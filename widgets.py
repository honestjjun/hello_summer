import json
from django import forms
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
try:
    # Django >=1.7
    from django.forms.utils import flatatt
except ImportError:
    # Django <1.7
    from django.forms.util import flatatt
from django_summernote.settings import summernote_config
from django.conf import settings

__all__ = ['SummernoteWidget', 'SummernoteInplaceWidget']

__summernote_options__ = [
    'airMode',
    'codemirror',
    'colors',
    'dialogsFade',
    'dialogsInBody',
    'direction',
    'disableLinkTarget',
    'focus',
    'fontNames',
    'fontNamesIgnoreCheck',
    'fontSizes',
    'lineHeights',
    'popover',
    'placeholder',
    'shortcuts',
    'styleWithSpan',
    'tableClassName',
    'tabSize',
    'toolbar',

    'width',
    'height',
]


def _get_proper_language():
    # Detect language automatically by get_language()
    if not summernote_config['lang']:
        return summernote_config['lang_matches'].get(get_language(), 'en-US')

    return summernote_config['lang']


class SummernoteWidgetBase(forms.Textarea):
    def template_contexts(self):
        contexts = {
            'lang': _get_proper_language(),
            'url': {
                'upload_attachment':
                reverse('django_summernote-upload_attachment'),
            },
        }

        for option in __summernote_options__:
            v = self.attrs.get(option, summernote_config.get(option))
            if v:
                contexts[option] = v

        return contexts

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)

        if value in summernote_config['empty']:
            return None

        return value


class SummernoteWidget(SummernoteWidgetBase):
    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        html = super(SummernoteWidget, self).render(name,
                                                    value,
                                                    attrs_for_textarea)

        final_attrs = self.build_attrs(attrs)
        del final_attrs['id']  # Use original attributes without id.

        contexts = self.template_contexts()

        url = reverse('django_summernote-editor',
                      kwargs={'id': attrs['id']})

        html += render_to_string(
            'django_summernote/widget_iframe.html',
            {
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'src': url,
                'attrs': flatatt(final_attrs),
                'width': contexts['width'],
                'height': contexts['height'],
                'settings': json.dumps(contexts),
                'STATIC_URL': settings.STATIC_URL,
            }
        )
        return mark_safe(html)


class SummernoteInplaceWidget(SummernoteWidgetBase):
    class Media:
        css = {
            'all': (
                summernote_config['default_css_for_inplace'] +
                summernote_config['css_for_inplace']
            )
        }

        js = (
            summernote_config['default_js_for_inplace'] +
            summernote_config['js_for_inplace']
        )

    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        attrs_for_textarea['id'] += '-textarea'
        html = super(SummernoteInplaceWidget, self).render(name,
                                                           value,
                                                           attrs_for_textarea)
        html += render_to_string(
            'django_summernote/widget_inplace.html',
            {
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'value': value if value else '',
                'settings': json.dumps(self.template_contexts()),
                'disable_upload': summernote_config['disable_upload'],
                'STATIC_URL': settings.STATIC_URL,
                'CSRF_COOKIE_NAME': settings.CSRF_COOKIE_NAME,
            }
        )
        return mark_safe(html)
