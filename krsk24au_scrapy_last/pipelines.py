# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from hashlib import md5
from scrapy import log
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from twisted.enterprise import adbapi
from twisted.internet import reactor

class Krsk24AuScrapyLastPipeline(object):
    def process_item(self, item, spider):
        return item

class MySQLPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def update_users(self, value):
        reactor.stop()

    def spider_opened(self, spider):
        spider.started_on = datetime.now()

    def spider_closed(self, spider):
        work_time = datetime.now() - spider.started_on
        spider.log("~~~~~ WORK TIME: %s" % work_time)

        # d = self.dbpool.runQuery("""UPDATE `krsk24au_info_review` SET user_id = (SELECT id FROM krsk24au_info_user WHERE name=user_name LIMIT 1)""")
        # d.addCallback(self.update_users)
        # reactor.run()

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_upsert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _do_upsert(self, conn, item, spider):
        """Perform an insert or update."""
        # item['date_time'] = datetime.strptime(item['date_time'][0], "%d.%m.%Y %H:%M:%S")
        uniq = self._generate_uniqid(item)
        item['uniq'] = uniq

        conn.execute("""SELECT EXISTS(
            SELECT 1 FROM krsk24au_last_newreview WHERE uniq = %s
        )""", (uniq, ))
        ret = conn.fetchone()[0]

        if not ret:
            conn.execute("""
                INSERT INTO krsk24au_last_newreview (uniq, good_id, title, review_id, review_link, seller_user_name, buyer_user_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (item['uniq'], item['good_id'], item['title'], item['review_id'], item['review_link'], item['seller_user_name'], item['buyer_user_name']))

        # spider.log("~~~~~~~ STORED IN DB: %s" % (uniq))

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        log.err(failure)

    def _generate_uniqid(self, item):
        """Generates an unique identifier for a given item."""
        # date_time = item['date_time'].strftime("%Y-%m-%d %H:%M:%S")
        # date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # id = item['good_id'] + date_time
        id = item['review_link']
        return md5("%s" % id).hexdigest()