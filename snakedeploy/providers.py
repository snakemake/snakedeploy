from abc import abstractmethod, ABC
from urllib.parse import urljoin

from snakedeploy.exceptions import UserError


def get_provider(source_url):
    for provider in PROVIDERS:
        if provider.matches(source_url):
            return provider(source_url)


class Provider(ABC):
    def __init__(self, source_url):
        if not (source_url.startswith("https://") or source_url.startswith("file:")):
            raise UserError(
                "Repository source URLs must be given as https:// or file://."
            )
        self.source_url = source_url.removesuffix(".git")

    @classmethod
    @abstractmethod
    def matches(cls, source_url: str):
        pass

    @abstractmethod
    def get_raw_file(self, path: str, tag: str):
        pass

    def get_repo_name(self):
        self.source_url.split("/")[-1]


class Github(Provider):
    @classmethod
    def matches(cls, source_url: str):
        return source_url.startswith("https://github.com")

    def get_raw_file(self, path: str, tag: str):
        return urljoin(self.source_url, urljoin(urljoin("raw", tag), path))


PROVIDERS = [Github]
