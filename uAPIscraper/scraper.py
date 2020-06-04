from codetiming import Timer
import asyncio
from .product import ProductScraper
from .progress_bar import ProgressBar


class Scraper(ProductScraper):
    def run(self):
        self.progress = ProgressBar(0)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_goods())

    async def get_goods(self):
        timer = Timer(text=f'Scraping time: {{:.1f}}s')
        timer.start()
        await self.get_categories()
        if not self.categories:
            return
        list_to_scraping = self.create_list_to_scraping()
        for item in list_to_scraping:
            await self.get_goods_in_category(item)
        await self.api.close_session()
        print(f'\nScraped {self.progress.counter} goods.')
        timer.stop()

    def create_list_to_scraping(self) -> list:
        list_to_scraping = []
        if type(self.categories_to_scraping) == list:
            for category in self.categories_to_scraping:
                cat = self.find_category(category)
                if cat is not None:
                    list_to_scraping.append(cat['cat_url'])
                    self.progress.update_max_count(int(cat['goods_count']))
                else:
                    print(f'Category "{category}" not found')
        elif (self.categories_to_scraping == 0) \
                or ((type(self.categories_to_scraping) == str)
                    and (self.categories_to_scraping.lower() == 'all')):
            for category in self.categories.values():
                list_to_scraping.append(category['cat_url'])
                self.progress.update_max_count(int(category['goods_count']))
        else:
            cat = self.find_category(self.categories_to_scraping)
            if cat is not None:
                list_to_scraping.append(cat['cat_url'])
                self.progress.update_max_count(int(cat['goods_count']))
            else:
                print(f'Category "{self.categories_to_scraping}" not found')
        return list_to_scraping

    async def get_goods_in_category(self, category: str):
        num_pages = await self.get_num_pages(category)
        if num_pages is None:
            return
        delay = (int(num_pages / 10) / 10 + 0.01) * self.delay_rate
        await asyncio.gather(*(self.get_goods_page(category, page, delay) for page in range(1, num_pages + 1)))

    async def get_num_pages(self, category: str) -> int or None:
        response = await self.api.get('/shop/cat', {'cat_uri': category, 'pnum': 1})
        try:
            response = response['success']
        except KeyError:
            print('\nError getting page count')
            return None
        else:
            return response['paginator']['num_pages']

    async def get_goods_page(self, category: str, page: int, delay: float):
        await asyncio.sleep(page * delay)
        response = await self.api.get('/shop/cat', {'cat_uri': category, 'pnum': page})
        try:
            response = response['success']
        except KeyError:
            print(f'\nError receiving page {page}')
        else:
            await self.scraping_goods(response['goods_list'])

    async def scraping_goods(self, goods: dict):
        await asyncio.gather(*(self.scraping_product(item) for item in goods.values()))
