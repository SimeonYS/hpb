import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import HpbItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class HpbSpider(scrapy.Spider):
	name = 'hpb'
	start_urls = ['https://www.hpb.hr/press/novosti']

	def parse(self, response):
		post_links = response.xpath('//div[@class="image-text__link-wrap"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//li[@class="article-meta__item article-meta__item--date"]/text()').get()
		title = response.xpath('//div[@class="page-intro__content content-style content-media-style content-style--larger"]/p/text() | //h1[@class="simple-hero-section__title"]/text()').get()
		content = response.xpath('//div[contains(@class,"single-article__content content-style content-media-style")]//text() | //div[@class="info-box__content content-style content-media-style js-info-box-content-match-height"]//text()').getall()
		if content == '\n          ' or content == ['\n      ', '\n    '] or content is None:
			content = response.xpath('//div[@class="page-intro__content content-style content-media-style content-style--larger"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=HpbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
