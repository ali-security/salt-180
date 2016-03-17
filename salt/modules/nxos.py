from __future__ import absolute_import
import re

import salt.utils

import logging
log = logging.getLogger(__name__)

__proxyenabled__ = ['nxos']
__virtualname__ = 'nxos'


def __virtual__():
    if salt.utils.is_proxy():
        return __virtualname__
    return (False, 'The nxos execution module failed to load: '
            'only available on proxy minions.')


def _parser(block):
    return re.compile('^{block}\n(?:^[ \n].*\n)+'.format(block=block), re.MULTILINE)


def _parse_software(data):
    ret = {'software': {}}
    software = _parser('Software').findall(data)[0]
    matcher = re.compile('^  ([^:]+): *([^\n]+)', re.MULTILINE)
    for line in matcher.finditer(software):
        key, val = line.groups()
        ret['software'][key] = val
    return ret['software']


def _parse_hardware(data):
    ret = {'hardware': {}}
    hardware = _parser('Hardware').findall(data)[0]
    matcher = re.compile('^  ([^:\n]+): *([^\n]+)', re.MULTILINE)
    for line in matcher.finditer(hardware):
        key, val = line.groups()
        ret['hardware'][key] = val
    return ret['hardware']


def _parse_plugins(data):
    ret = {'plugins': []}
    plugins = _parser('plugin').findall(data)[0]
    matcher = re.compile('^  (?:([^,]+), )+([^\n]+)', re.MULTILINE)
    for line in matcher.finditer(plugins):
        ret['plugins'].extend(line.groups())
    return ret['plugins']


def system_info():
    data = __proxy__['nxos.sendline']('show ver')
    info = {
        'software': _parse_software(data),
        'hardware': _parse_hardware(data),
        'plugins': _parse_plugins(data),
    }
    return info


def cmd(command, *args, **kwargs):
    proxy_prefix = __opts__['proxy']['proxytype']
    proxy_cmd = '.'.join([proxy_prefix, command])
    if proxy_cmd not in __proxy__:
        return False
    return __proxy__[proxy_cmd](*args, **kwargs)


def ping():
    return cmd('ping')


def grains():
    return cmd('grains')
