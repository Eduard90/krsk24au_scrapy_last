# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Krsk24AuScrapyLastItem(Item):
    # define the fields for your item here like:
    # name = Field()
    uniq = Field()
    good_id = Field()
    seller_id = Field()
    buyer_id = Field()
    title = Field()
    review_id = Field()
    review_link = Field()
    date_time = Field()
    seller_user_name = Field()
    buyer_user_name = Field()
    pass
