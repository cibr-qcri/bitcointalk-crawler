import logging
import re
from datetime import datetime
from hashlib import sha256

import scrapy
from dateutil import parser
from scrapy.http import Request
from w3lib.html import remove_tags

from ..items import BitcointalkProfileItem


class BitcointalkSpider(scrapy.Spider):
    PROFILE_NOT_EXIST = "profile you are trying to view does not exist"
    name = "bitcointalk"
    allowed_domains = ["bitcointalk.org"]
    start_urls = ["https://bitcointalk.org"]
    start_index = 1
    current_profile = 1
    end_index = 2

    def parse(self, response):
        self.end_index = int(response.xpath('/html//div[@id = "upshrinkHeaderIC"]//table//tr//td//span')
                             .re('[\\d]+')[2])
        base_url = 'https://bitcointalk.org/index.php?action=profile;u={}'

        while True:
            if self.start_index >= self.end_index:
                yield Request(self.start_urls[0])
                break
            for profile_id in range(self.start_index, self.end_index + 1):
                self.current_profile = profile_id
                yield Request(base_url.format(profile_id), callback=self.parse_profile)
            self.start_index = self.end_index + 1
            break

    def parse_profile(self, response):
        if len(response.xpath("//*[contains(text(), '%s')]" % self.PROFILE_NOT_EXIST)):
            return
        profile_photo_url = BitcointalkSpider.extract_profile_image(response.xpath('//*[@class="windowbg"]//img/@src'))
        blocks = response.xpath('//*[@class="windowbg"]//td')

        profile = BitcointalkProfileItem()
        profile['link'] = response.url

        optional_fields = dict()

        index = 1
        profile['name'] = BitcointalkSpider.process_token(blocks[index])
        if 'Custom' in BitcointalkSpider.process_token(blocks[index + 1]):
            optional_fields['custom_title'] = BitcointalkSpider.process_token(blocks[index + 2])
            index = index + 2

        profile['date'] = datetime.today()
        profile['response'] = response.text
        profile['posts'] = BitcointalkSpider.to_int('posts', BitcointalkSpider.process_token(blocks[index + 2]))
        profile['activity'] = BitcointalkSpider.to_int('activity', BitcointalkSpider.process_token(blocks[index + 4]))
        profile['merit'] = BitcointalkSpider.to_int('merit', BitcointalkSpider.process_token(blocks[index + 6]))
        profile['position'] = BitcointalkSpider.process_token(blocks[index + 8])
        profile['date_registered'] = BitcointalkSpider.to_datetime(BitcointalkSpider.process_token(blocks[index + 10]))
        profile['last_active'] = BitcointalkSpider.to_datetime(BitcointalkSpider.process_token(blocks[index + 12]))
        optional_fields['icq'] = BitcointalkSpider.process_token(blocks[index + 15])
        optional_fields['aim'] = BitcointalkSpider.process_token(blocks[index + 17])
        optional_fields['msn'] = BitcointalkSpider.process_token(blocks[index + 19])
        optional_fields['yim'] = BitcointalkSpider.process_token(blocks[index + 21])
        optional_fields['email'] = BitcointalkSpider.validate_email(blocks[index + 23])
        optional_fields['website'] = BitcointalkSpider.process_token(blocks[index + 25])

        index = index + 28
        while 'Gender' not in BitcointalkSpider.process_token(blocks[index]):
            key = BitcointalkSpider.process_token(blocks[index])
            value = self.process_token(blocks[index + 1])
            if not key:
                break
            if 'Skype' in key:
                optional_fields['skype'] = value
            if 'Bitcoin address' in key:
                btc_address = BitcointalkSpider.validate_address(value)
                optional_fields['bitcoin_address'] = btc_address
            if 'Other' in key:
                optional_fields['other_info'] = value
            index = index + 2

        index = index + 2
        optional_fields['gender'] = self.process_token(blocks[index])
        optional_fields['age'] = BitcointalkSpider.to_int('age', self.process_token(blocks[index + 2]))
        optional_fields['location'] = self.process_token(blocks[index + 4])
        optional_fields['signature'] = self.process_token(blocks[index + 10])

        if profile_photo_url:
            optional_fields['profile_photo'] = 'https://bitcointalk.org' + profile_photo_url

        profile['optional_fields'] = optional_fields
        profile["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        profile['raw_data'] = response.text

        if self.end_index == self.current_profile:
            yield Request(self.start_urls[0])

        yield profile

    @staticmethod
    def to_int(key, value):
        try:
            return int(value)
        except ValueError:
            logging.warning("Cannot cast value:%s to integer. Expected an integer for key:%s" % (value, key))
            return ""

    @staticmethod
    def to_datetime(value):
        try:
            return parser.parse(value).timestamp() * 1000
        except ValueError:
            logging.warning("Cannot cast value:%s to datetime." % value)
            return ""

    @staticmethod
    def validate_email(email):
        email = BitcointalkSpider.process_token(email)
        if email == 'hidden':
            return ''
        return email

    @staticmethod
    def process_token(value):
        return remove_tags(value.extract()).strip('\r\t\n')

    @staticmethod
    def extract_profile_image(value):
        images = value.extract()
        if len(images) > 1:
            return remove_tags(images[1])
        return ''

    def validate_address(self, btc_address):
        pattern1 = re.compile('[1,3][a-km-zA-HJ-NP-Z1-9]{25,34}')
        pattern2 = re.compile('bc1[a-zA-HJ-NP-Z0-9]{25,39}')
        if (pattern1.match(btc_address) or pattern2.match(btc_address)) and self.check_bc(btc_address):
            return btc_address
        logging.warning("Invalid bitcoin address:%s", btc_address)
        return ''

    @staticmethod
    def decode_base58(bc, length):
        digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        n = 0
        for char in bc:
            n = n * 58 + digits58.index(char)
        return n.to_bytes(length, 'big')

    def check_bc(self, bc):
        try:
            bcbytes = self.decode_base58(bc, 25)
            return bcbytes[-4:] == sha256(sha256(
                bcbytes[:-4]).digest()).digest()[:4]
        except:
            return False
