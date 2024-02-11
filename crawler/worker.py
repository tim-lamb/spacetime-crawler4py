from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from datetime import datetime

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.worker_id = worker_id
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=False)
        
    def run(self):
        while not self.frontier.terminate.is_set():
            tbd_url = self.frontier.get_tbd_url()

            if not tbd_url:
                self.logger.info("Frontier is empty. Waiting...")
                # Mark worker as finished
                self.frontier.is_finished[self.worker_id].set()
                # If all workers are finished, terminate all
                if all(map(lambda x: x.is_set(), self.frontier.is_finished)):
                    self.frontier.terminate.set()
                time.sleep(self.config.time_delay)
                continue

            # If last crawl was less than the specified delay
            if self.get_time_difference(tbd_url) <= self.config.time_delay:
                time.sleep(self.config.time_delay)
            
            resp = download(tbd_url, self.config, self.logger)

            # Update the domain timers on the frontier
            self.frontier.set_domain_time(tbd_url)

            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = None
            while scraped_urls == None:
                try:
                    scraped_urls = scraper.scraper(tbd_url, resp)
                except RuntimeError:
                    continue
            self.frontier.write_crawler()
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            # Set worker to active
            self.frontier.is_finished[self.worker_id].clear()
        self.logger.info("Terminating...")
    
    def get_time_difference(self, url):
        # Get the difference between current time and last time domain was crawled
        cur_time = datetime.now()
        last_time = self.frontier.get_domain_time(url)
        return (cur_time-last_time).total_seconds()
    
