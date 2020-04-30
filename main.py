# Goods parser for ucoz (with using uAPI).
# author Ilya Matthew Kuvarzin <luceo2011@yandex.ru>
# version 1.0 dated April 30, 2020

from uAPI import Request
import os
import re
from requests import get
import sys
import math
from codetiming import Timer
import config

counter = 0
goods_count = 0
remove_after_parse = True


def create_dir(dir_name: str):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        return dir_name
    else:
        return create_dir(dir_name + '(1)')


def create_description_file(file_name: str, data: dict):
    with open('template.html', 'r', encoding="utf-8") as input_file:
        with open(file_name + '.html', 'w', encoding="utf-8") as output_file:
            for template_line in input_file:
                for template in re.findall(r"{{ \S* }}", template_line):
                    keys = re.search(r"[^{\s}]+", template).group().split('.')
                    val = data
                    for key in keys:
                        val = val[key]
                    template_line = template_line.replace(template, str(val))
                output_file.write(template_line + '\n')


def download_photo(dir_path: str, data: dict):
    content = get(data['entry_photo']['def_photo']['photo']).content
    file_name = data['entry_photo']['def_photo']['photo'].split('/')[-1]
    with open(f"{dir_path}/{file_name}", 'wb') as file:
        file.write(content)
    if type(data['entry_photo']['others_photo']) != str:
        for photo in data['entry_photo']['others_photo'].values():
            file_name = photo['photo'].split('/')[-1]
            content = get(photo['photo']).content
            with open(f"{dir_path}/{file_name}", 'wb') as file:
                file.write(content)


def parse_goods(goods: dict, dir_path: str):
    global counter, goods_count, remove_after_parse
    for item in goods.values():
        folder_name = re.sub(r"[\/\:\*\?\"\<\>|]", '', item['entry_title'])
        new_path = create_dir(f"{dir_path}/{folder_name}")
        create_description_file(f"{new_path}/description", item)
        download_photo(f"{new_path}", item)
        if remove_after_parse:
            api.post('/shop/' + config.cat_uri, {'method': 'delete', 'id': item['entry_id']})
        counter += 1
        progress = counter/goods_count
        sys.stdout.write(
            '\rProgress: [' + '#' * math.floor(progress * 25) + '_' * math.floor((1 - progress) * 25) + '] '
            + str(round(progress * 10000) / 100) + '%')
        sys.stdout.flush()


def get_goods(dir_path: str, page: int = 1):
    global goods_count
    response = api.get('/shop/cat', {'cat_uri': 'arkhiv', 'pnum': page})
    try:
        response = response['success']
    except KeyError:
        print('\nError receiving goods')
    else:
        goods_count = response['goods_count']
        parse_goods(response['goods_list'], dir_path)
        if page < response['paginator']['num_pages']:
            get_goods(dir_path, page + 1)


if __name__ == '__main__':
    api = Request(config.site, config.transfer_protocol,
                  {
                      'oauth_consumer_key': config.application_id,
                      'oauth_consumer_secret': config.consumer_secret,
                      'oauth_token': config.oauth_token,
                      'oauth_token_secret': config.oauth_token_secret
                  })

    path = os.getcwd()
    timer = Timer(text=f"\nTask time: {{:.1f}}")
    timer.start()
    get_goods(path + '/test')
    timer.stop()
