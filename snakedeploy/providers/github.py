__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020, Vanessa SOchat"
__license__ = "MPL 2.0"

import re
import os
import json
import shutil
import requests
from snakedeploy.utils import run_command
from snakedeploy.logger import logger


class GitHubProvider:
    """A snakedeploy provider is a resource to retrieve a pipeline."""

    name = "github"
    matchstring = "github"
    repo_regex = re.compile("(?P<username>[a-z0-9-]+)/(?P<reponame>[a-z0-9-]+)")
    token = os.environ.get("GITHUB_TOKEN")

    def check_install(self):
        """A helper to ensure that git is installed, returns False if not."""
        cmd = ["git", "--version"]
        try:
            result = run_command(cmd, quiet=True)
            return result.get("return_code", 1) == 0
        except:
            return False

    def extract_repo_name(self, name):
        """Given some repository name, strip off any url prefix or suffix,
        and return a match object.
        """
        return "/".join(name.split("/")[-2:])

    def do_request(self, url, headers, data=None, method="GET"):
        """A general function to do a request, and handle any possible error
        codes.
        """
        response = requests.request(method, url, headers=headers, data=json.dumps(data))
        if response.status_code not in [200, 201]:
            for key, value in response.items():
                logger.error(f"{key}: {value}")
            logger.exit(f"Error with {url}: {response.status_code}, {response.reason}")
        return response.json()

    def template(self, source, name=None):
        """Given a source repository and a destination name (a org/reponame
        on GitHub), check that the user has defined a GitHub access token, and
        template the repository to their account.
        """
        if not self.token:
            logger.exit(
                "You must export a GITHUB_TOKEN to template a workflow repository."
            )
        headers = {"Authorization": "Bearer %s" % self.token}

        # Derive source repository name
        match = self.repo_regex.search(self.extract_repo_name(source))
        if not match:
            logger.exit("Repository name for source must include <org>/<repo>.")
        sourceuser, sourcerepo = match.groups()

        # If a name is provided, must be in format org/repo
        if name:
            match = self.repo_regex.search(self.extract_repo_name(name))
            if not match:
                logger.exit("Repository name must be in format <org>/<repo>.")
            username, reponame = match.groups()

        # Otherwise, use default for username and repository name
        else:
            reponame = sourcerepo
            username = self.do_request(
                "https://api.github.com/user", headers=headers
            ).get("login")

        # Formulate the request data
        headers["Accept"] = "application/vnd.github.baptiste-preview+json"
        data = {"owner": username, "name": reponame}

        # Create template repository, return to calling function
        url = f"https://api.github.com/repos/{sourceuser}/{sourcerepo}/generate"
        response = self.do_request(url, method="POST", data=data, headers=headers)
        repo = response.get("html_url")
        if not repo:
            logger.exit("There was a problem templating the repository.")
        return repo

    def clone(self, source, dest, force=False, keep_git=False):
        """Clone a repository to a destination, force overwriting if necessary."""
        if not self.repo_regex.search(source) or not source.startswith("http"):
            logger.exit(
                f"{source} does not match a regular expression for a repository."
            )
        if os.path.exists(dest) and not force:
            logger.exit(f"{dest} exists and force is set to False, will not overwrite.")
        elif os.path.exists(dest) and force:
            shutil.rmtree(dest)
        if not self.check_install():
            logger.exit("git not found on the path, install it to continue.")

        # Use simple Git command
        return_code = os.system(f"git clone {source} {dest}")
        if return_code == 0:

            # Clean up git folder if indicated
            git = os.path.join(dest, ".git")
            if not keep_git and os.path.exists(git):
                logger.debug(f"Cleaning up {git}")
                shutil.rmtree(git)
                logger.info(
                    "To create the remote repository on Github, open\n\n"
                    "https://github.com/new\n\n"
                )

            return dest
        logger.exit(f"Error cloning repository: {return_code}")
