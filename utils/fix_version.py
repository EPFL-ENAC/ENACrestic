"""
Fix version in all files after release-please bump
"""

import json

if __name__ == "__main__":
    # Get version from .release-please-manifest.json
    with open(".release-please-manifest.json") as f:
        release_please = json.load(f)
        version = release_please["."]

    # fix .release-please-manifest.json
    release_please["src"] = version
    with open(".release-please-manifest.json", "w") as f:
        json.dump(release_please, f, indent=2)
        f.write("\n")

    # fix src/enacrestic/__init__.py
    with open("src/enacrestic/__init__.py") as f:
        lines = f.readlines()
    with open("src/enacrestic/__init__.py", "w") as f:
        for line in lines:
            if line.startswith("__version__"):
                f.write(f'__version__ = "{version}"\n')
            else:
                f.write(line)

    # fix pyproject.toml
    with open("pyproject.toml") as f:
        lines = f.readlines()
    with open("pyproject.toml", "w") as f:
        good_section = False
        for line in lines:
            if good_section and line.startswith("version"):
                f.write(f'version = "{version}"\n')
            else:
                f.write(line)
            if line.startswith("[tool.poetry]"):
                good_section = True
            elif line.startswith("["):
                good_section = False

    # fix package.json
    with open("package.json") as f:
        package = json.load(f)
    package["version"] = version
    with open("package.json", "w") as f:
        json.dump(package, f, indent=2)
        f.write("\n")

    # fix package-lock.json
    with open("package-lock.json") as f:
        package_lock = json.load(f)
    package_lock["version"] = version
    package_lock["packages"][""]["version"] = version
    with open("package-lock.json", "w") as f:
        json.dump(package_lock, f, indent=2)
        f.write("\n")
