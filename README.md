# BitcoinTalkCrawler

A basic scrapper made in python with [scrapy framework](https://scrapy.org/) supports to -
* Scrape profiles & associated BTC addresses from [BitcoinTalk](https://bitcointalk.org/).
* Push the output to ElasticSearch.

At the moment crawler only outputs to the ElasticSearch.
### Kubernetese Deployment
***Prerequisites***
1. Kubernetese cluster
2. ElasticSearch cluster

***Install BitcoinTalk Crawler***
Install bitcointalk crawler with the release name ```bitcointalk-crawler```
```sh
helm install bitcointalk-crawler https://toshi-qcri.github.io/helm-charts-test/bitcointalk-crawler-0.0.0.tgz
```
### Output Format
BitcoinTalk crawler outputs crawled profiles to elasticsearch in following format
```
{
"timestamp": timestamp,
"type": "user",
"source": "bitcointalk",
"info": {
  "domain": domain,
  "url": crawled_url,
  "title": title,
  "external_links: {
    "href_urls": {
        "web": [www_urls],
        "onion": [onion_urls]
    }
  },
  "tags": {
    "cryptocurrency": {
      "address": {
        "btc": [btc_addrs]
      }
    },
    "profile": {
        "name": name,
        "num_posts": num_posts,
        "num_activities": num_activities,
        "merit": merit,
        ...
    }
  },
  "raw_data": raw_data
}
```
---

This project is part of [CIBR](https://github.com/qcri/cibr).
