from collections import namedtuple
import os
import re
from typing import Optional
from reretry import retry
from urllib3.util.retry import Retry

import github
from github import Github, GithubException

from snakedeploy.exceptions import UserError
from snakedeploy.logger import logger


def get_repo():
    g = Github(
        os.environ["GITHUB_TOKEN"],
        retry=Retry(total=10, status_forcelist=(500, 502, 504), backoff_factor=0.3),
    )
    return g.get_repo(os.environ["GITHUB_REPOSITORY"])


File = namedtuple("File", "path, content, is_updated, msg")


class PR:
    def __init__(
        self,
        title,
        body,
        branch,
        repo,
        entity: Optional[str] = None,
        label_entity_regex: Optional[str] = None,
    ):
        self.title = title
        self.body = body
        self.files = []
        self.branch = branch
        self.repo = repo
        self.base_ref = (
            os.environ.get("GITHUB_BASE_REF") or os.environ["GITHUB_REF_NAME"]
        )
        self.label = None

        if label_entity_regex is not None:
            if entity is None:
                raise ValueError("entity must be given if label_entity_regex is set")
            m = re.match(label_entity_regex, entity)
            if m is None:
                raise UserError(f"Given --entity-regex did not match any {entity}.")
            try:
                self.label = m.group("entity")
            except IndexError:
                raise UserError("No group 'entity' found in given --entity-regex.")

    def add_file(self, filepath, content, is_updated, msg):
        self.files.append(File(str(filepath), content, is_updated, msg))

    @retry(tries=2, delay=60)
    def create(self):
        if not self.files:
            logger.info("No files to commit.")
            return

        branch_exists = False
        try:
            b = self.repo.get_branch(self.branch)
            logger.info(f"Branch {b} already exists.")
            branch_exists = True
        except GithubException as e:
            if e.status != 404:
                raise e
            logger.info(f"Creating branch {self.branch}...")
            self.repo.create_git_ref(
                ref=f"refs/heads/{self.branch}",
                sha=self.repo.get_branch(self.base_ref).commit.sha,
            )
        for file in self.files:
            sha = None
            if branch_exists:
                logger.info(f"Obtaining sha of {file.path} on branch {self.branch}...")
                try:
                    # try to get sha if file exists
                    sha = self.repo.get_contents(file.path, self.branch).sha
                except github.GithubException.UnknownObjectException as e:
                    if e.status != 404:
                        raise e
            elif file.is_updated:
                logger.info(
                    f"Obtaining sha of {file.path} on branch {self.base_ref}..."
                )
                sha = self.repo.get_contents(file.path, self.base_ref).sha

            if sha is not None:
                self.repo.update_file(
                    file.path,
                    file.msg,
                    file.content,
                    sha,
                    branch=self.branch,
                )
            else:
                self.repo.create_file(
                    file.path, file.msg, file.content, branch=self.branch
                )

        pr_exists = any(
            pr.head.label.split(":", 1)[1] == self.branch
            for pr in self.repo.get_pulls(state="open", base=self.base_ref)
        )
        if pr_exists:
            logger.info("PR already exists.")
        else:
            pr = self.repo.create_pull(
                title=self.title,
                body=self.body,
                head=self.branch,
                base=self.base_ref,
            )
            if self.label is not None:
                pr.add_to_labels(self.label)
            logger.info(f"Created PR: {pr.html_url}")
