import re
import os
import asyncio
from .base import BaseScraper


def create_dir(dir_path: str, create_if_exist: bool = True) -> str:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        return dir_path
    elif create_if_exist:
        return create_dir(dir_path + '(1)')


class ProductScraper(BaseScraper):
    async def scraping_product(self, product: dict):
        folder_name = re.sub(r"[/:*?\"<>|]", '', product['entry_title'])
        if self.create_dir_tree:
            category = self.find_category_by_id(int(product['entry_cat']['id']))
            dir_path = f"{self.result_dir}/{category['local_path']}"
        else:
            dir_path = self.result_dir
        new_path = create_dir(f"{dir_path}/{folder_name}")
        self.create_description_file(f"{new_path}/description", product)
        await self.get_photos(f"{new_path}", product)
        if self.remove_after_parse:
            await self.api.post('/shop/editgoods', {'method': 'delete', 'id': product['entry_id']})
        self.progress.inc(1)
        self.progress.show()

    def create_description_file(self, file_name: str, data: dict):
        with open(self.template_path, 'r', encoding="utf-8") as input_file:
            with open(file_name + '.html', 'w', encoding="utf-8") as output_file:
                for template_line in input_file:
                    for template in re.findall(r"{{ \S* }}", template_line):
                        keys = re.search(r"[^{\s}]+", template).group().split('.')
                        val = data
                        for key in keys:
                            val = val[key]
                        template_line = template_line.replace(template, str(val))
                    output_file.write(template_line + '\n')

    async def get_photos(self, dir_path: str, data: dict):
        urls = [data['entry_photo']['def_photo']['photo']]
        if type(data['entry_photo']['others_photo']) != str:
            for photo in data['entry_photo']['others_photo'].values():
                urls.append(photo['photo'])
        if len(urls) > 1:
            await asyncio.gather(*(self.download_photo(dir_path, url) for url in urls))
        else:
            await self.download_photo(dir_path, urls[0])

    async def download_photo(self, dir_path: str, url: str):
        response = await self.api.session.get(url)
        file_name = url.split('/')[-1]
        with open(f"{dir_path}/{file_name}", 'wb') as file:
            file.write(await response.content.read())
