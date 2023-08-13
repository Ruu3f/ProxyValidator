"""
ProxyChecker
The fastest and best proxy checker.
"""

from threading import Lock, Thread
from requests import get, RequestException


class ProxyChecker:
    """
    Class to check the validity of proxy servers.
    """

    def __init__(self):
        """
        Initializes the ProxyChecker class.
        """
        self.checked_proxies = set()
        self.lock = Lock()

    def run(self, proxies_file, max_threads: int):
        """
        Runs the proxy checking process.

        Args:
            proxies_file (str): Path to the file containing proxy addresses.
            max_threads (int): Maximum number of threads to use.
        """
        with open(proxies_file, "r", encoding="utf-8") as file:
            proxies = file.read().splitlines()

        threads = []
        for proxy in proxies:
            thread = Thread(target=self.check_proxy, args=(proxy,))
            threads.append(thread)
            thread.start()
            if len(threads) >= max_threads:
                for thread in threads:
                    thread.join()
                threads = []
        for thread in threads:
            thread.join()

        with open("working_proxies.txt", "a", encoding="utf-8") as file:
            with self.lock:
                for proxy in self.checked_proxies:
                    file.write(proxy + "\n")

    def check_proxy(self, proxy):
        """
        Checks if a proxy is working by sending a request to google.

        Args:
            proxy (str): Proxy address to check.
        """
        try:
            response = get(
                "https://google.com/",
                proxies={"http": proxy, "https": proxy},
                timeout=5,
            )
            if response.status_code == 200:
                with self.lock:
                    print(f"Proxy {proxy} works.")
                    self.checked_proxies.add(proxy)
            else:
                with self.lock:
                    print(f"Proxy {proxy} doesn't work.")
        except RequestException:
            with self.lock:
                print(f"Proxy {proxy} doesn't work.")


if __name__ == "__main__":
    ProxyChecker().run("proxies.txt", 1000)
