#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import binascii
from datetime import datetime
import calendar, time
import hashlib
import hmac
import sys
import getopt

try:
    from datetime import timezone
    utc = timezone.utc
except:
    # python 2 variant
    from datetime import timedelta, tzinfo
    class UTC(tzinfo):
        ZERO = timedelta(0)
        """UTC"""

        def utcoffset(self, dt):
            return self.ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return self.ZERO

    utc = UTC()


def read_file(path):
    try:
        f = open(path, "r+b")
        return f.read()
    except Exception as ex:
        print("Could not read file: %s error %s  ", path, ex)
        exit(3)

def to_bytes(o):
    return str(o).encode("utf-8")

class Token:
    def __init__(self, key, appID, userName, vCardFile, expires):
        self.type    = 'provision'
        self.key     = key
        self.jid     = userName + "@" + appID
        if (vCardFile):
            self.vCard   = read_file(vCardFile).decode("utf-8").strip()
        else:
            self.vCard   = ""
        self.expires = expires

    def __str__(self):
        return "Token" + {'type'    : self.type,
                          'key'     : self.key,
                          'jid'     : self.jid,
                          'vCard'   : self.vCard[:10] + "...",
                          'expires' : self.expires}.__str__()

    def serialize(self):
        sep = b"\0" # Separator is a NULL character
        body = to_bytes(self.type) + sep + to_bytes(self.jid) + sep + to_bytes(self.expires) + sep + to_bytes(self.vCard)
        mac = hmac.new(bytearray(self.key, 'utf8'), msg=body, digestmod=hashlib.sha384).digest()
        ## Uncomment to debug
        ##sys.stderr.buffer.write( b"key : " + base64.b64encode(bytearray(self.key, 'utf8')) + b"\n" )print("bodyFull: " + self.type + "_" + self.jid + "_" + str(self.expires) + "_" + self.vCard);
        ##sys.stderr.buffer.write(b"bodyString: " + ("%s_%s_%s_%s" % (self.type, self.jid, str(self.expires), self.vCard)).encode("utf-8") + b"\n");
        ##sys.stderr.buffer.write( b"body: " + ("%s" % [b for b in body]).encode("utf-8") + b"\n" )
        ##sys.stderr.buffer.write( b"mac : " + base64.b64encode(mac) + b"\n" )
        ##sys.stderr.flush()
        ## Combine the body with the hex version of the mac
        serialized = body + sep + binascii.hexlify(mac)
        return serialized

def printHelp():
    print("\nThis script will generate a provision login token from a developer key"
      "\nOptions:"
      "\n\t--key           Developer key supplied with the developer account"
      "\n\t--appID         ApplicationID supplied with the developer account"
      "\n\t--userName      Username to generate a token for"
      "\n\t--vCardFile     Path to the XML file containing a vCard for the user"
      "\n\t--expiresInSecs Number of seconds the token will be valid can be used instead of expiresAt"
      "\n\t--expiresAt     Time at which the token will expire ex: (2055-10-27T10:54:22Z) can be used instead of expiresInSecs"
      "\n")
