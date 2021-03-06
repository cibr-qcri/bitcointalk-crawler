import scrapy


class BitcointalkProfileItem(scrapy.Item):
    name = scrapy.Field()
    custom_title = scrapy.Field()
    posts = scrapy.Field()
    activity = scrapy.Field()
    merit = scrapy.Field()
    position = scrapy.Field()
    date_registered = scrapy.Field()
    last_active = scrapy.Field()
    icq = scrapy.Field()
    aim = scrapy.Field()
    msn = scrapy.Field()
    yim = scrapy.Field()
    email = scrapy.Field()
    website = scrapy.Field()
    link = scrapy.Field()
    skype = scrapy.Field()
    bitcoin_address = scrapy.Field()
    other_info = scrapy.Field()
    gender = scrapy.Field()
    age = scrapy.Field()
    location = scrapy.Field()
    signature = scrapy.Field()
    profile_photo = scrapy.Field()
    raw_data = scrapy.Field()
    timestamp = scrapy.Field()
    response = scrapy.Field()
    date = scrapy.Field()

    optional_fields = scrapy.Field()
