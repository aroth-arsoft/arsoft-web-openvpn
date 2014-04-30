#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='arsoft-web-openvpn',
		version='0.9',
		description='shows the status of OpenVPN via web',
		author='Andreas Roth',
		author_email='aroth@arsoft-online.com',
		url='http://www.arsoft-online.com/',
		packages=['arsoft.web.openvpn'],
		scripts=[],
		data_files=[
            ('/etc/arsoft/web/openvpn/static', ['arsoft/web/openvpn/static/main.css']),
            ('/etc/arsoft/web/openvpn/templates', ['arsoft/web/openvpn/templates/home.html']),
            ]
		)
