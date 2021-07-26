import hashlib
import re
from datetime import datetime

from elasticsearch import Elasticsearch, helpers
from scrapy.utils.project import get_project_settings

from .support import BitcoinTalkHelper


class BitcointalkCrawlerPipeline(object):
    def __init__(self):
        self.buffer = list()
        self.helper = BitcoinTalkHelper()
        self.settings = get_project_settings()
        self.date = datetime.today()
        self.server = self.settings['ELASTICSEARCH_CLIENT_SERVICE_HOST']
        self.port = self.settings['ELASTICSEARCH_CLIENT_SERVICE_PORT']
        self.port = int(self.port)
        self.username = self.settings['ELASTICSEARCH_USERNAME']
        self.password = self.settings['ELASTICSEARCH_PASSWORD']
        self.index = self.settings['ELASTICSEARCH_INDEX']
        self.buffer_size = self.settings['BUFFER_SIZE']

        if self.port:
            uri = "http://%s:%s@%s:%d" % (self.username, self.password, self.server, self.port)
        else:
            uri = "http://%s:%s@%s" % (self.username, self.password, self.server)

        self.es = Elasticsearch([uri])

    def process_item(self, item, spider):
        btc_addr_pat = re.compile(
            r"\b(1[a-km-zA-HJ-NP-Z1-9]{25,34})\b|\b(3[a-km-zA-HJ-NP-Z1-9]{25,34})\b|\b(bc1[a-zA-HJ-NP-Z0-9]{25,39})\b"
        )
        addr_list = set()
        for res in btc_addr_pat.findall(item['raw_data']):
            addr_list.update(set(res))

        addr_list = set(filter(self.helper.check_bc, addr_list))

        response = item['response']

        profile = dict()
        profile["name"] = item["name"]
        profile["posts"] = item["posts"]
        profile["activity"] = item["activity"]
        profile["merit"] = item["merit"]
        profile["position"] = item["position"]
        profile["date_registered"] = item["date_registered"]
        profile["last_active"] = item["last_active"]
        profile = {**profile, **item["optional_fields"]}
        doc_id = hashlib.sha1(item['name'].encode('utf-8')).hexdigest()

        tag = {
            "_id": doc_id,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'type': 'user',
            'source': 'bitcointalk',
            "method": "html",
            "version": 1,
            "info": {
                "domain": "bitcointalk.org",
                "url": item["link"],
                "title": "View the profile of " + item["name"],
                "external_urls": {
                    "href_urls": {
                        "web": [],
                        "tor": []
                    }
                },
                "tags": {
                    "cryptocurrency": {
                        "address": {
                            "btc": list(addr_list)
                        }
                    },
                    "profile": profile,
                }
            },
            "summary": list(addr_list)
        }
        self.buffer.append(tag)
        self.write_to_file(response, doc_id)

        if len(self.buffer) % self.buffer_size == 0:
            helpers.bulk(self.es, self.buffer, True, index=self.index)
            self.buffer.clear()

    @staticmethod
    def write_to_file(page, es_id):
        with open("/mnt/data/{id}".format(id=es_id), "w") as f:
            f.write(page)
