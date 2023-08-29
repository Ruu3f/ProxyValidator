"""
ProxyValidator
The fastest and best proxy validator. Supports HTTP and SOCKS.
"""

from threading import Lock, Thread
from requests import get, RequestException


class ProxyValidator:
    """
    Class to validate the validity of proxy servers.
    """

    def __init__(self):
        """
        Initializes the ProxyValidator class.
        """
        self.validated_proxies = set()
        self.lock = Lock()

    def run(self, proxies_file, max_threads: int):
        """
        Runs the proxy validation process.

        Args:
            proxies_file (str): Path to the file containing proxy addresses.
            max_threads (int): Maximum number of threads to use.
        """
        with open(proxies_file, "r", encoding="utf-8") as file:
            proxies = file.read().splitlines()

        threads = []
        for proxy in proxies:
            thread = Thread(target=self.validate_proxy, args=(proxy,))
            threads.append(thread)
            thread.start()
            if len(threads) >= max_threads:
                for thread in threads:
                    thread.join()
                threads = []
        for thread in threads:
            thread.join()

        with open("validated_proxies.txt", "a", encoding="utf-8") as file:
            with self.lock:
                for proxy in self.validated_proxies:
                    file.write(f"{proxy}\n")

    def validate_proxy(self, proxy):
        """
        Validates if a proxy is working by sending a request to google.com

        Args:
            proxy (str): Proxy address to validate.
        """
        try:
            response = get(
                "https://google.com/",
                proxies={
                    "http": proxy,
                    "https": proxy,
                    "socks4": proxy,
                    "socks5": proxy,
                },
                timeout=5,
            )
            if response.status_code == 200:
                with self.lock:
                    print(f"\033[32mProxy {proxy} is valid. \033[0m")
                    self.validated_proxies.add(proxy)
            else:
                with self.lock:
                    print(f"\033[31mProxy {proxy} isn't valid.\033[0m")
        except RequestException:
            with self.lock:
                print(f"\033[31mProxy {proxy} isn't valid.\033[0m")
