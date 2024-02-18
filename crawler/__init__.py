from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker
import crawler_data

class Crawler(object):
    def __init__(self, config, restart, frontier_factory=Frontier, worker_factory=Worker):
        
        self.config = config
        self.logger = get_logger("CRAWLER")
        crawler_data.init_load_save()
        
        self.frontier = frontier_factory(config, restart)
        crawler_data.init_crawler_data()
        
        self.workers = list()
        self.worker_factory = worker_factory
        
        

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        try:
            self.start_async()
            self.join()
        except KeyboardInterrupt:
            # When closing crawler, terminate threads cleanly
            self.frontier.terminate.set()

    def join(self):
        for worker in self.workers:
            worker.join()
