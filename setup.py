## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service
#
# Copyright (C) 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
# Copyright (C) 2025 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "GMH-Meresco"
#
# "GMH-Meresco" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "GMH-Meresco" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "GMH-Meresco"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from distutils.core import setup

version = "$Version: 12.0.0$"[9:-1].strip()

from os import walk
from os.path import join

data_files = []
for path, dirs, files in walk("doc"):
    data_files.append(
        (
            path.replace("doc", "/usr/share/doc/gmh-meresco", 1),
            [join(path, f) for f in files],
        )
    )
scripts = []
for path, dirs, files in walk("bin"):
    scripts.extend(join(path, f) for f in files)
packages = []
for path, dirs, files in walk("gmh_meresco"):
    if "__init__.py" in files:
        packages.append(path.replace("/", "."))
package_data = {}
for path, dirs, files in walk("gmh_meresco"):
    for suffix in [".txt", ".sf", ".xsd", ".png"]:
        if any(f.endswith(suffix) for f in files):
            segments = path.split("/")
            package = ".".join(segments[:2])
            filepath = join(*(segments[2:] + ["*" + suffix]))
            package_data.setdefault(package, []).append(filepath)

setup(
    name="GMH-Meresco",
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    data_files=data_files,
    version=version,
    url="https://github.com/seecr/gmh-meresco",
    author="Seecr",
    author_email="info@seecr.nl",
    maintainer="Seecr",
    maintainer_email="info@seecr.nl",
    description="Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service",
    long_description="Gemeenschappelijke Metadata Harvester (GMH) data extractie en OAI service",
    license="GNU Public License",
    platforms="all",
)
