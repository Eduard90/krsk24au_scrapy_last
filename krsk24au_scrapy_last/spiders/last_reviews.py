from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import Spider, BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.http import Request
from scrapy.contrib.loader import XPathItemLoader, ItemLoader
from scrapy.selector import HtmlXPathSelector, Selector
from krsk24au_scrapy_last.items import Krsk24AuScrapyLastItem
from datetime import datetime
from krsk24au_scrapy_last import settings
import re
import MySQLdb

BASE_URL = 'http://24au.ru/lastreviews/'

class Krsk24AuScrapyLastLoader(ItemLoader):
    default_output_processor = TakeFirst()

class LastReviewsSpider(Spider):
    name = "last_reviews"
    allowed_domains = ["krsk.24au.ru"]
    start_urls = [BASE_URL]

    # def __init__(self, category=None, *args, **kwargs):
        # super(ReviewsSpider, self).__init__(*args, **kwargs)
        # urls = []
        # for url in self.start_urls:
        #     for page in range(settings.PAGES_FROM, settings.PAGES_TO+1):
        #         urls.append(url + PAGE_URL % page)
        #
        # connect = MySQLdb.connect(host=settings.MYSQL_HOST,
        #                       user=settings.MYSQL_USER,
        #                       passwd=settings.MYSQL_PASSWD,
        #                       db=settings.MYSQL_DBNAME
        #                     )
        #
        # for user in settings.USERS:
        #     curs = connect.cursor()
        #     curs.execute("""SELECT COUNT(id) as cnt from krsk24au_info_user WHERE name = %s""", (user, ))
        #     user_id = curs.fetchone()[0]
        #     if not user_id:
        #         curs.execute("""INSERT INTO krsk24au_info_user (name) VALUES (%s)""", (user, ))
        #         connect.commit()
        #
        #     # if user_id:
        #     #     print "USER %s EXIST" % user
        #     # else:
        #     #     print "USER %s NOT_EXIST" % user
        #
        # self.start_urls = urls

    def parse(self, response):
        hxs = Selector(response)
        reviews = hxs.xpath('//table[@id="items"]/tr')
        items = []
        for review in reviews:
            good_id = review.xpath('./td[5]/a/@href').re('\/([0-9]+)\/')
            if good_id:
                item = Krsk24AuScrapyLastItem()
                item['good_id'] = good_id[0]
                user_1_role = review.xpath('./td[3]').re('\((.*)\)<br>')
                user_2_role = review.xpath('./td[4]').re('\((.*)\)\\r\\n')
                user_1_name = review.xpath('./td[3]/span/span/span/a/text()').extract()
                user_2_name = review.xpath('./td[4]/span/span/span/a/text()').extract()

                item['title'] = review.xpath('./td[5]/a/text()').extract()
                item['review_id'] = review.xpath('./td[6]/a/@href').re('ID=([0-9]+)')
                item['review_link'] = review.xpath('./td[6]/a/@href').extract()

                user_1_role = user_1_role.pop(0)
                user_2_role = user_2_role.pop(0)

                if user_1_role.__len__() == 8:
                    user_1_role = 'SELLER'
                    item['seller_user_name'] = user_1_name
                else:
                    user_1_role = 'BUYER'
                    item['buyer_user_name'] = user_1_name

                if user_2_role.__len__() == 8:
                    user_2_role = 'SELLER'
                    item['seller_user_name'] = user_2_name
                else:
                    user_2_role = 'BUYER'
                    item['buyer_user_name'] = user_2_name

                items.append(item)

        return items