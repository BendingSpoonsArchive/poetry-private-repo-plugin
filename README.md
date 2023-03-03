# poetry-private-repo-plugin

This plugin injects an opinionated way of managing custom `secondary` repositories until a better alternative is officially developed within Poetry (see https://github.com/python-poetry/poetry/issues/6713).

Until the plugin is published on PyPI, you can install it as:
```bash
poetry self add git+https://github.com/BendingSpoons/poetry-private-repo-plugin.git#1.1.1
```

## What do we want to solve

A typical company use case is having a private pypi repository where internal packages are hosted. There you want to make sure to fetch internal packages only while fetching public packages from PyPI. At the same time, you want to make sure that internal packages are fetched from the internal repository, avoiding dependency confusion attacks where one publishes a malicious library on PyPI with the same name of the internal one.

The way you would achieve this on Poetry is through [secondary sources](https://python-poetry.org/docs/repositories#secondary-package-sources) and [source dependencies](https://python-poetry.org/docs/dependency-specification/#source-dependencies).
```toml
[[tool.poetry.source]]
name = "acme"
secondary = true
url = "https://acme.com/pypi/simple"

[tool.poetry.dependencies]
acme-lib = { version = "^5.0.0", source = "acme" }
pypi-lib = "^4.3.4"
```

While security is ensured (`acme-lib` will be downloaded from the `acme` repository only), your dependency resolution will get much slower. This is because Poetry will look for `pypi-lib` on both repositories! As your number of dependencies grows, this will cause more and more friction.

## How does the plugin differ

The plugin performs a small monkeypatch of the internal `RepositoryPool` class of Poetry, making sure that secondary sources are not queried if the default source (pypi in this case) returned at list one valid package. This ensures a good company setup while keeping dependency resolution blazing fast 🏃

## An extra - even more opinionated - security layer

Although the plugin should satisfy your security needs, you still have to remember settings the `source` parameter for every internal package. Not only this can be tedious, but also error-prone. What happens if you forget setting the `source`? Assuming no ongoing dependency confusion attack, nothing. The dependency will be resolved with the correct checksum and source and the determinism offered by the `poetry.lock` will ensure that no future attack can affect your project. However, one could say that if you forget setting the `source` _while developing_ (aka changing dependencies with Poetry), you may still be part of an attack.

Although the chance of this happening is really one in a billion trillions, the plugin offers a set-and-forget way in case your internal dependencies follow some naming convention. That is, you can enfore that a dependency matching a given pattern will be downloaded from a given `source` even if you forget adding that in the `[tool.poetry.dependencies]` section.

```toml
# Any package that begins with "acme-" will be downloaded from the "acme" repository
[tool.poetry-private-repo-plugin.enforce-source]
"acme-*" = "acme"

# The specific dependency source has precedence over
[tool.poetry.dependencies]
# acme-lib1 will be downloaded from the "acme" repository
acme-lib1 = { version = "^5.0.0" }
# dependency-specific sources have higher priority over the project option, so
# acme-lib2 will be downloaded from the "acme-mirror" repository
acme-lib2 = { version = "^5.0.0", source = "acme-mirror" }
```
