from abc import abstractmethod, ABC

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
        # TODO replace with removesuffix once Python 3.9 becomes the minimal version of snakedeploy
        if source_url.endswith(".git"):
            source_url = source_url[:-4]
        self.source_url = source_url

    @classmethod
    @abstractmethod
    def matches(cls, source_url: str):
        pass

    @abstractmethod
    def get_raw_file(self, path: str, tag: str):
        pass

    def get_repo_name(self):
        return self.source_url.split("/")[-1]


class Github(Provider):
    @classmethod
    def matches(cls, source_url: str):
        return source_url.startswith("https://github.com")

    def get_raw_file(self, path: str, tag: str):
        return f"{self.source_url}/raw/{tag}/{path}"

    def get_source_file_declaration(self, path: str, tag: str, branch: str):
        owner_repo = "/".join(self.source_url.split("/")[-2:])
        if not (tag or branch):
            raise UserError("Either tag or branch has to be specified for deployment.")
        ref_arg = f'tag="{tag}"' if tag is not None else f"branch={branch}"
        return f'github("{owner_repo}", path="{path}", {ref_arg})'


PROVIDERS = [Github]
