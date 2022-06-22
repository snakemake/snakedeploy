from abc import abstractmethod, ABC
from distutils.dir_util import copy_tree
from snakedeploy.exceptions import UserError
import subprocess as sp
import os


def get_provider(source_url):
    for provider in PROVIDERS:
        if provider.matches(source_url):
            return provider(source_url)

    raise UserError("No matching provider for source url %s" % source_url)


class Provider(ABC):
    def __init__(self, source_url):
        if not (
            source_url.startswith("https://")
            or source_url.startswith("file:")
            or os.path.exists(source_url)
        ):
            raise UserError(
                "Repository source URLs must be given as https:// or file://, or exist."
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
    def clone(self, path: str):
        pass

    @abstractmethod
    def get_raw_file(self, path: str, tag: str):
        pass

    def get_repo_name(self):
        return self.source_url.split("/")[-1]


class Local(Provider):
    @classmethod
    def matches(cls, source_url: str):
        return os.path.exists(source_url)

    def clone(self, tmpdir: str):
        """
        A local "clone" means moving files.
        """
        copy_tree(self.source_url, tmpdir)

    def get_raw_file(self, path: str, tag: str):
        if tag:
            print(
                "Warning: tag is not supported for a local repository - check out the branch you need."
            )
        return f"{self.source_url}/{path}"

    def get_source_file_declaration(self, path: str, tag: str, branch: str):
        relative_path = path.replace(self.source_url, "").strip(os.sep)
        return f'"{relative_path}"'


class Github(Provider):
    @classmethod
    def matches(cls, source_url: str):
        return cls.__name__.lower() in source_url

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def clone(self, tmpdir: str):
        """
        Clone the known source URL to a temporary directory
        """
        try:
            sp.run(["git", "clone", self.source_url, "."], cwd=tmpdir, check=True)
        except sp.CalledProcessError as e:
            raise UserError("Failed to clone repository {}:\n{}", self.source_url, e)

    def get_raw_file(self, path: str, tag: str):
        return f"{self.source_url}/raw/{tag}/{path}"

    def get_source_file_declaration(self, path: str, tag: str, branch: str):
        owner_repo = "/".join(self.source_url.split("/")[-2:])
        if not (tag or branch):
            raise UserError("Either tag or branch has to be specified for deployment.")
        ref_arg = f'tag="{tag}"' if tag is not None else f'branch="{branch}"'
        return f'{self.name}("{owner_repo}", path="{path}", {ref_arg})'


class Gitlab(Github):
    @classmethod
    def get_raw_file(self, path: str, tag: str):
        return f"{self.source_url}/-/raw/{tag}/{path}"


PROVIDERS = [Github, Gitlab, Local]
