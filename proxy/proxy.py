import random


class Proxy:
    def __init__(self):
        self._proxies = self.load_proxy_list2()

    @staticmethod
    def load_proxy_list2():
        with open("./proxy/proxy_list.txt") as f:
            lines = [i.strip().split("\t")[:2] for i in f.readlines()]
            return [f"http://{i[0]}:{i[1]}" for i in lines]

    @staticmethod
    def load_proxy_list():
        with open("./proxy/proxy_list2.txt") as f:
            lines = [i.strip().split(" ") for i in f.readlines()]
            cleaned_lines = [[item for item in sublist if item != ''] for sublist in lines]
            return [f"http://{i[0]}:{i[1]}" for i in cleaned_lines]

    # Latest Update clean proxy over 85% up rate is 2023-11-14 22:50 EST
    @staticmethod
    def clean_proxy_list():
        with open("./proxy/clean_proxy_202311142250.txt") as f:
            lines = [f"http://{i.strip()}" for i in f.readlines()]
            return lines

    @property
    def proxy_ip(self):
        return random.choice(self._proxies)
