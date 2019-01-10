# Atarashi Dockerfile
# Copyright (C) 2018 Gaurav Mishra, mishra.gaurav@siemens.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# Copying and distribution of this file, with or without modification,
#
# Description: Docker container image recipe

FROM python:3-alpine

LABEL maintainer="Fossology <fossology@fossology.org>"
LABEL Description="Image for Atarashi project"
COPY . .

#RUN apk add --update bash curl
#RUN apk add gcc make linux-headers musl-dev openldap-dev libxml2-dev libxslt-dev
#RUN apk add libffi-dev pcre-dev cython
RUN apk add --update py-pip gcc make git cython
RUN apk add subversion lapack-dev musl-dev

RUN python3 setup.py install

ENTRYPOINT ["atarashi"]
CMD ["-h"]
