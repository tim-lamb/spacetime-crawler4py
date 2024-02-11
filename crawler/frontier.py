import os
import shelve

from threading import Thread, RLock, Event
from queue import Queue, Empty

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid
import crawler_data

from datetime import datetime
import re
import random

PATTERN = r".*(ics\.uci\.edu\/)[^#]*|.*(cs\.uci\.edu\/)[^#]*|.*(informatics\.uci\.edu\/)[^#]*|.*(stat\.uci\.edu\/)[^#]*"
DOMAINS = ["ics.uci.edu/", "cs.uci.edu/", "informatics.uci.edu/", "stat.uci.edu/"]

def get_domain(url):
    # Get domain of a URL
    domain = re.match(PATTERN, url)
    if domain == None:
        domain = re.match(PATTERN, url+'/')
    for i in domain.groups():
        if i != None:
            return i

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        #self.to_be_downloaded = list()
        self.queue_lock = RLock()
        self.write_lock = RLock()
        self.terminate = Event()
        self.is_finished = [Event() for i in range(self.config.threads_count)]

        # Timers for each domain to enforce politeness
        self.domain_timers = {
            "ics.uci.edu/": datetime.now(),
            "cs.uci.edu/": datetime.now(),
            "informatics.uci.edu/": datetime.now(),
            "stat.uci.edu/": datetime.now()
        }

        # Separate lists for each domain
        self.to_be_downloaded = {
            "ics.uci.edu/": list(),
            "cs.uci.edu/": list(),
            "informatics.uci.edu/": list(),
            "stat.uci.edu/": list()
        }
        crawler_data.init_load_save()
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            crawler_data.LOAD_SAVE = False
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            crawler_data.LOAD_SAVE = True
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded[get_domain(url)].append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        with self.queue_lock:
            try:
                chosen = None

                # Check if all the lists are empty
                if all(map(lambda x: True if len(x) == 0 else False,self.to_be_downloaded.values())): return None

                # Choose random domain and assign it to worker, max 15 loops
                for _ in range(15):
                    chosen = self.to_be_downloaded[random.choice(DOMAINS)]
                    if chosen != None or len(chosen) > 0: break
                return chosen.pop()
            except IndexError:
                return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            with self.queue_lock:
                self.save[urlhash] = (url, False)
                self.save.sync()
                self.to_be_downloaded[get_domain(url)].append(url)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        with self.queue_lock:
            if urlhash not in self.save:
                # This should not happen.
                self.logger.error(
                    f"Completed url {url}, but have not seen it before.")

            self.save[urlhash] = (url, True)
            self.save.sync()

    def get_domain_time(self, url):
        # Get domain timer for specific url
        with self.queue_lock:
            return self.domain_timers[get_domain(url)]
        
    def set_domain_time(self, url):
        # Set domain timer for specific url
        with self.queue_lock:
            self.domain_timers[get_domain(url)] = datetime.now()

    def write_crawler(self):
        # Thread safe write data
        with self.write_lock:
            crawler_data.write_data("crawler_data.txt")
