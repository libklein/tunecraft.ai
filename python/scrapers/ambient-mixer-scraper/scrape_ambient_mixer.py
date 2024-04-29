import scrapy
import re
from scrapy.http import Response, Request
from bs4 import BeautifulSoup

# from rich.progress import Progress, MofNCompleteColumn, TextColumn
import xmltodict
import time
import requests
from collections import defaultdict


class AmbientMixerSpider(scrapy.Spider):
    name = "ambient-mixer.com"
    base_url = "https://www.ambient-mixer.com/"

    handle_httpstatus_list = [404]

    def parse_audio_listing(self, response: Response, **metadata):
        if response.status != 200:
            return

        if (page_match := re.match(".*?page=(\\d+).*", response.url)) is not None:
            page = int(page_match.group(1))
        else:
            return

        print(f"Parsing page {page}")

        # Collect links
        audio_mixes = response.css('div[class^="select_dash_ambient"]').css("a")[:1]

        yield from response.follow_all(
            response.xpath("//div[@class='pages']//a"),
            callback=self.parse_audio_listing,
        )
        yield from response.follow_all(audio_mixes, callback=self.parse_audio_mix)

    def parse_audio_mix(self, response: Response, **metadata):
        title = (
            response.css('div[id="home_description_top"]').css("h1::text").get().strip()
        )
        description = (
            response.css('div[id="home_description_audio_text"]')
            .css("p::text")
            .get()
            .strip()
        )
        # Parse breadcrumbs
        categories = [
            x.strip()
            for x in response.css('div[id="bread_crumbs"] a span::text').getall()
        ]
        # get audio id for audio mix request
        audio_id = int(
            response.css('div[id="mixer_details"] .keep_left:last-child a')
            .attrib["href"]
            .split("/")[-1]
        )
        yield Request(
            url=f"https://xml.ambient-mixer.com/audio-template?player=html5&id_template={audio_id}",
            callback=self.parse_audio_mix_xml,
            cb_kwargs={
                "title": title,
                "description": description,
                "categories": categories,
                "audio_id": audio_id,
            },
        )

    def parse_audio_mix_xml(self, response: Response, **metadata):
        print(f"Parsing audio mix {metadata['audio_id']}")
        template_mix = xmltodict.parse(response.text)
        yield dict(
            mix={
                value["id_audio"]: value
                for key, value in template_mix["audio_template"].items()
                if key.startswith("channel")
            },
            **metadata,
        )

    def start_requests(self):
        # self.task = self.progress_display.add_task(description="Downloading offers", total=self.max_scraped_offers)
        yield Request(
            url=self.base_url + "most-rated-audio?page=1",
            callback=self.parse_audio_listing,
        )


def main():
    # Set up logging
    from scrapy.crawler import CrawlerProcess

    crawler = CrawlerProcess(
        settings={
            "FEEDS": {"mixes.json": {"format": "json"}},
            "LOG_FILE": "ambient_mixer_scraper.log",
            "LOG_FILE_APPEND": False,
            "LOG_LEVEL": "INFO",
            "LOG_STDOUT": True,
            "JOBDIR": "./persistency",
            "CONCURRENT_REQUESTS_PER_DOMAIN": 24,
            "AUTOTHROTTLE_ENABLED": True,
            "AUTOTHROTTLE_MAX_DELAY": 30.0,
            "AUTOTHROTTLE_START_DELAY": 0.2,
            "AUTOTHROTTLE_TARGET_CONCURRENCY": 24.0,
            "USER_AGENT": "Dalvik/2.1.0 (Linux; U; Android 9; Standard PC (i440FX + PIIX, 1996) Build/PI [Android Fronteir 6.3.2)",
            #        "DOWNLOAD_DELAY": 0.1
        }
    )
    crawler.crawl(AmbientMixerSpider)
    # with Progress(*Progress.get_default_columns(), TextColumn("| Retrieved"), MofNCompleteColumn(" of "), TextColumn("vouchers"), refresh_per_second=1) as progress:
    # AmbientMixerSpider.progress_display = progress
    crawler.start()


if __name__ == "__main__":
    main()
