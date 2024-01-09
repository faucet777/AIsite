import math
import requests
from .models import *
from AIwebApp.settings import GPT_TOKEN


header = [  # {'title': 'Home', 'url_name': 'home'},
    {'title': 'OctoCHAT', 'url_name': 'chat'}, ]

usr_sect = [
    {'title': 'Login', 'url_name': 'login'},
    {'title': 'Register', 'url_name': 'register'},
]
instructions = [
    {}
]

class DataMixin:
    def make_svg_ico(self, svg_size: tuple, params: dict):
        dY = -1
        match params['figure']:

            case 'logo':
                hex_size = params['size']
                x_line = svg_size[0] * 0.95 * 0.5
                y_line = svg_size[1] * 0.618
                h = params['size'] / 2 * 3 / math.sqrt(3)
                coefs = [0.382, 0.618, 0.786, 1, 1.272]
                svg_data = {'width': svg_size[0],
                            'height': svg_size[1],
                            'elements': [{
                                'line': {'x1': 0, 'x2': x_line * c, 'y1': y_line * c + dY, 'y2': y_line * c + dY},
                                'polygon': f"{x_line * c},{y_line * c + dY} {x_line * c + hex_size / 2},{y_line * c - h + dY} {x_line * c + hex_size * 1.5},{y_line * c - h + dY} {x_line * c + 2 * hex_size},{y_line * c + dY} {x_line * c + hex_size * 1.5},{y_line * c + h + dY} {x_line * c + hex_size / 2},{y_line * c + h + dY}"
                            } for c in coefs]
                            }
                return svg_data

            case 'send_btn':
                triangle_h = svg_size[1] / 2 - 2
                triangle_w = svg_size[0] - 2
                svg_data = {'width': svg_size[0],
                            'height': svg_size[1],
                            'elements': [{'polygon': f"{0},{0} {0},{triangle_h} {triangle_w},{triangle_h}"},
                                         {
                                             'polygon': f"{0},{triangle_h * 2 + 3} {0},{triangle_h + 3} {triangle_w},{triangle_h + 3}"}
                                         ]
                            }
                return svg_data

    def get_user_context(self, **kwargs):
        ip = self.get_ip()
        context = kwargs
        if self.request.user.is_authenticated:
            udata, isnew = UserData.objects.get_or_create(data_user=self.request.user)
            udata.is_guest = False

            if ip not in udata.user_ips:
                udata.user_ips += [ip]
            udata.save()

        else:
            udata_q = UserData.objects.filter(user_ips__icontains=ip)
            if udata_q:
                udata = udata_q[0]
                udata.is_guest = True
                udata.save()
            else:
                udata = UserData.objects.create(user_ips=[ip], subscription=Product.objects.get(product_tag='GUEST'))
        self.request.session['user_pk'] = udata.pk

        context['data_user'] = udata
        context['header'] = header
        context['svg_data'] = self.make_svg_ico((150, 57.3), {'figure': 'logo', 'size': 5})
        return context
    
    def get_ip(self):
        return self.request.META['REMOTE_ADDR']

def gpt_answer(messages: list):
    headers = {
        'Authorization': f'Bearer {GPT_TOKEN}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messages': messages,
        'model': 'gpt-3.5-turbo',
    }
    with requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
    ) as resp:
        gpt_data = resp.json()
        token_usage = gpt_data['usage']['total_tokens']
        print('utls token usage:', token_usage)
    return (gpt_data['choices'][0]['message']['content'], token_usage)


