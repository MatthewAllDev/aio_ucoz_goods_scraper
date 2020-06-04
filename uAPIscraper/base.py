import os
from .aioUAPI import Request as Api
from .progress_bar import ProgressBar


class BaseScraper:
    def __init__(self,
                 api: Api,
                 categories_to_scraping: list or int or str = 'all',
                 template_path: str = f'{os.path.dirname(os.path.abspath(__file__))}/template.html',
                 result_dir: str = f'{os.getcwd()}/result',
                 remove_after_parse: bool = False,
                 create_dir_tree: bool = True,
                 delay_rate: float = 1):
        self.api: Api = api
        self.template_path: str = template_path
        self.categories_to_scraping: list or int or str = categories_to_scraping
        self.result_dir: str = result_dir
        self.remove_after_parse: bool = remove_after_parse
        self.create_dir_tree: bool = create_dir_tree
        self.delay_rate: float = delay_rate
        self.progress: ProgressBar = ProgressBar(0)
        self.categories: dict = {}

    async def get_categories(self):
        response = await self.api.get('/shop/request', {'page': 'categories'})
        try:
            response = response['success']
        except KeyError:
            print('\nError getting categories')
        else:
            for item in response:
                self.categories.update(self.categories_update(item))

    def categories_update(self, category: dict, local_path: str = '') -> dict:
        categories = {}
        cat_id = int(category['cat_id'])
        local_path = f"{local_path}/{category['cat_name']}".replace(':', ' -')
        categories.update({cat_id: {'cat_name': category['cat_name'], 'cat_url': category['cat_url'],
                                    'local_path': local_path, 'goods_count': category['goods_count']}})
        if type(category['childs']) == list:
            for child in category['childs']:
                categories.update(self.categories_update(child, local_path))
        return categories

    def find_category(self, cat: str or int) -> dict or None:
        if type(cat) == str:
            return self.find_category_by_url(cat)
        elif type(cat) == int:
            return self.find_category_by_id(cat)

    def find_category_by_id(self, cat_id: int) -> dict or None:
        return self.categories.get(cat_id)

    def find_category_by_url(self, cat_url: str) -> dict or None:
        for cat in self.categories.values():
            if cat['cat_url'] == cat_url:
                return cat
        return None
