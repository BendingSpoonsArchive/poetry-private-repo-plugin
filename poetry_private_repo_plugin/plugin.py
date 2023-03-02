from poetry.console.application import Application
from poetry.core.packages.dependency import Dependency
from poetry.core.packages.package import Package
from poetry.plugins.application_plugin import ApplicationPlugin
from poetry.repositories.repository_pool import RepositoryPool


class CustomRepositoryPool(RepositoryPool):
    def find_packages(self, dependency: Dependency) -> list[Package]:
        """
        Override the behaviour of Poetry, in particular this line:
        https://github.com/python-poetry/poetry/blob/bbb0d89f0e90babfb48d6f37318670d3a9fbb005/src/poetry/repositories/repository_pool.py#L136
        """
        # If a dependency specifies the source field, fetch it from there (and only there).
        if repository_name := dependency.source_name:
            return self.repository(repository_name).find_packages(dependency)

        # Else, fetch it from the first repository that returns a list of packages
        packages: list[Package] = []
        for repo in self.repositories:
            if packages := repo.find_packages(dependency):
                return packages

        # No package has been found in any repository
        return []


class PoetryPrivateRepoPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        assert application.event_dispatcher is not None
        assert application._io is not None

        official_pool = application.poetry.pool
        plugin_pool = CustomRepositoryPool()
        plugin_pool._repositories = official_pool._repositories
        plugin_pool._ignore_repository_names = official_pool._ignore_repository_names
        application.poetry._pool = plugin_pool
