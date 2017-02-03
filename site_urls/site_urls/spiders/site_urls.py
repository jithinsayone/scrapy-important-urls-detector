import re
import csv

import scrapy

from lxml import html
from scrapy.http import Request


class SiteUrls(scrapy.Spider):
    name = 'site_urls'
    main_urls = []

    def __init__(self, site_url="", *args, **kwargs):
        super(SiteUrls, self).__init__(*args, **kwargs)
        self.yielded_urls = set()
        self.site_url = "%s" % site_url

    def start_requests(self):
        yield Request(url=self.site_url)

    def parse(self, response):
        doc = html.fromstring(response.body)
        domain = self.parse_domain(response.url)
        self.parse_site_urls(doc, domain)
        print self.main_urls

    def parse_domain(self, url):
        """
        parse site domain
        :param url:
        :return: domain
        """
        domain = re.search(r'(http|https)://(.+?)$', url)
        if domain:
            return domain.group(2).strip('/')

    def parse_site_urls(self, doc, domain):
        """
        find whole urls from doc and write ito csv
        :param doc:
        :param domain:
        :return:
        """
        urls_list = doc.xpath('.//a/@href')
        for url in urls_list:
            if domain in url:
                self.parse_main_urls(url, domain, length=2)
            elif ('http' not in url) and ('www' not in url):
                self.parse_main_urls(url, domain, length=1)

        # save main urls into csv file
        with open('main_urls.csv', 'wb') as f:
            writer = csv.writer(f)
            for val in self.main_urls:
                writer.writerow([val])

    def parse_main_urls(self, url, domain, length):
        """
        split and find the main url from the given url
        :param url:
        :param domain:
        :param length:
        :return: main urls
        """
        if '/' in url:
            url_split = filter(None, url.split('/'))
            if len(url_split) == length:
                main_url = domain + '/' + url_split[0]
                if main_url not in self.yielded_urls:
                    self.yielded_urls.add(main_url)
                    self.main_urls.append(main_url)
        return self.main_urls

