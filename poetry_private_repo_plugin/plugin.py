import fnmatch
from typing import Dict, List, Optional

from poetry.console.application import Application
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.repositories.repository_pool import RepositoryPool


class PluginConfig:
    def __init__(self, config: PyProjectTOML) -> None:
        self._config = config.data.get("tool", {}).get("poetry-private-repo-plugin", {})

    @property
    def enfore_source(self) -> Dict[str, str]:
        return self._config.get("enforce-source", {})


class CustomRepositoryPool(RepositoryPool):
    def __init__(self, enfore_source: Optional[Dict[str, str]] = None) -> None:
        super().__init__()
        self._enforce_source = enfore_source

    def find_packages(self, dependency: Dependency) -> List[Package]:
        """
        Override the behaviour of Poetry, in particular this line:
        https://github.com/python-poetry/poetry/blob/bbb0d89f0e90babfb48d6f37318670d3a9fbb005/src/poetry/repositories/repository_pool.py#L136
        """
        # If the enforce-source option is enabled and the dependency doesn't override
        # the source repository, look for a match and, if found, return packages from there.
        if self._enforce_source and not dependency.source_name:
            for match, source in self._enforce_source.items():
                if dependency.name and fnmatch.fnmatch(dependency.name, match):
                    return self.repository(source).find_packages(dependency)

        # If a dependency specifies the source field, fetch it from there (and only there).
        if repository_name := dependency.source_name:
            return self.repository(repository_name).find_packages(dependency)

        # Else, fetch it from the first repository that returns a list of packages
        packages: List[Package] = []
        for repo in self.repositories:
            if packages := repo.find_packages(dependency):
                return packages

        # No package has been found in any repository
        return []


class PoetryPrivateRepoPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        assert application.event_dispatcher is not None
        assert application._io is not None

        config = PluginConfig(application.poetry.pyproject)
        official_pool = application.poetry.pool
        plugin_pool = CustomRepositoryPool(config.enfore_source)
        plugin_pool._repositories = official_pool._repositories
        plugin_pool._ignore_repository_names = official_pool._ignore_repository_names
        application.poetry._pool = plugin_pool
