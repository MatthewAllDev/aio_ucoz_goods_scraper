# Example of using the uAPIscrapper module
# author Ilya Matthew Kuvarzin <luceo2011@yandex.ru>
# version 2.0 dated June 04, 2020

from uAPIscraper import Api
from uAPIscraper import Scraper

if __name__ == '__main__':
    api = Api('my-site.com', 'https',
              {
                  'oauth_consumer_key': 'Application id',
                  'oauth_consumer_secret': 'Consumer secret',
                  'oauth_token': 'OAuth token',
                  'oauth_token_secret': 'OAuth token secret'
              })

    # Scraper init arguments:
    #   api: aioUAPI.Request - object connection with uAPI
    #
    #   categories_to_scraping: list, int (category id or 0 (all categories)) or str (category url or 'all').
    #   Default = 'all'
    #
    #   template_path: str - absolute path to description template file.
    #   Default: uses the module template file
    #
    #   result_dir: str - absolute directory path for saving results.
    #   Default: './result'
    #
    #   remove_after_parse: bool - flag activation deletion goods after scrapping.
    #   Default: False
    #
    #   create_dir_tree: bool - flag activation creating directory tree.
    #   Default: True
    #
    #   delay_rate: float - coefficient responsible for the interval between getting pages. Less is faster,
    #   but the server may not have time to process the required number of requests.
    #   Delay formula: (int(num_pages / 10) / 10 + 0.01) * delay_rate

    scraper = Scraper(api, [1, 'gadgets/phones'])
    scraper.run()