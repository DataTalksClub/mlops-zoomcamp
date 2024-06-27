#!/usr/bin/bash
# SPDX-FileCopyrightText: 2022 Maxwell G <gotmax@e.email>
# SPDX-License-Identifier: MIT

set -euo pipefail
ruamel_yaml_version=0.16.10

rm -fv *-LICENSE.*
wget https://github.com/cdgriffith/Box/raw/master/LICENSE -O box-LICENSE.txt
wget https://github.com/uiri/toml/raw/master/LICENSE -O toml-LICENSE.txt
wget https://github.com/hukkin/tomli/raw/master/LICENSE -O tomli-LICENSE.txt
wget https://github.com/pallets/click/raw/main/LICENSE.rst -O click-LICENSE.rst
wget https://github.com/theskumar/python-dotenv/raw/main/LICENSE -O python-dotenv-LICENSE.txt
wget "https://files.pythonhosted.org/packages/source/r/ruamel.yaml/ruamel.yaml-${ruamel_yaml_version}.tar.gz" -O- | tar -xzvO "ruamel.yaml-${ruamel_yaml_version}/LICENSE" >ruamel.yaml-LICENSE.txt
