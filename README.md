# poetry-private-repo-plugin

This plugin injects an opinionated way of managing custom `secondary` repositories until a better alternative is officially developed within Poetry (see https://github.com/python-poetry/poetry/issues/6713).

Until the plugin is published on PyPI, you can install it as:
```bash
poetry self add git+https://github.com/ralbertazzi/poetry-private-repo-plugin.git#1.0.1
```

## What do we want to solve

A typical company use case is having a private pypi repository where internal packages are hosted. There you want to make sure to fetch internal packages only while fetching public packages from PyPI. At the same time, you want to make sure that packages are fetched from the internal repository, avoiding security attacks where one publishes a library with the same name of the internal one on PyPI.

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
