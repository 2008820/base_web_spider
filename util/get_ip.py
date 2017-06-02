#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:xd
import socket
import fcntl
import struct

def get_ip():
    """
    获取本机IP
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 0x8915 -> SIOCGIFADDR
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth1'))[20:24])
    except Exception, e:
        try:
            return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'wlan0'))[20:24])
        except Exception, e:
            try:
                return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'eth0'))[20:24])
            except Exception, e:
                return socket.gethostbyname(socket.getfqdn(socket.gethostname()))