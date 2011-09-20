#!/usr/bin/python
# Copyright (c) 2011 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

'''A simple tool to update the Native Client SDK to the latest version'''

import cStringIO
import exceptions
import hashlib
import json
import optparse
import os
import shutil
import string
import subprocess
import sys
import tempfile
import urllib2
import urlparse


#------------------------------------------------------------------------------
# Constants

MAJOR_REV = 1
MINOR_REV = 0

GLOBAL_HELP = '''Usage: %prog [options] command [command_options]

sdk_update is a simple utility that updates the Native Client (NaCl)
Software Developer's Kit (SDK).

Commands:
  help [command] - Get either general or command-specific help
  delete - Deletes a given bundle (not implemented yet)
  list - Lists the available bundles
  update - Updates the SDK to the latest recommended toolchains'''

MANIFEST_FILENAME='naclsdk_manifest.json'

# The following SSL certificates are used to validate the SSL connection
# to https://commondatastorage.googleapis.com
# TODO(mball): Validate at least one of these certificates.
# http://stackoverflow.com/questions/1087227/validate-ssl-certificates-with-python

EQUIFAX_SECURE_CA_CERTIFICATE='''-----BEGIN CERTIFICATE-----
MIIDIDCCAomgAwIBAgIENd70zzANBgkqhkiG9w0BAQUFADBOMQswCQYDVQQGEwJV
UzEQMA4GA1UEChMHRXF1aWZheDEtMCsGA1UECxMkRXF1aWZheCBTZWN1cmUgQ2Vy
dGlmaWNhdGUgQXV0aG9yaXR5MB4XDTk4MDgyMjE2NDE1MVoXDTE4MDgyMjE2NDE1
MVowTjELMAkGA1UEBhMCVVMxEDAOBgNVBAoTB0VxdWlmYXgxLTArBgNVBAsTJEVx
dWlmYXggU2VjdXJlIENlcnRpZmljYXRlIEF1dGhvcml0eTCBnzANBgkqhkiG9w0B
AQEFAAOBjQAwgYkCgYEAwV2xWGcIYu6gmi0fCG2RFGiYCh7+2gRvE4RiIcPRfM6f
BeC4AfBONOziipUEZKzxa1NfBbPLZ4C/QgKO/t0BCezhABRP/PvwDN1Dulsr4R+A
cJkVV5MW8Q+XarfCaCMczE1ZMKxRHjuvK9buY0V7xdlfUNLjUA86iOe/FP3gx7kC
AwEAAaOCAQkwggEFMHAGA1UdHwRpMGcwZaBjoGGkXzBdMQswCQYDVQQGEwJVUzEQ
MA4GA1UEChMHRXF1aWZheDEtMCsGA1UECxMkRXF1aWZheCBTZWN1cmUgQ2VydGlm
aWNhdGUgQXV0aG9yaXR5MQ0wCwYDVQQDEwRDUkwxMBoGA1UdEAQTMBGBDzIwMTgw
ODIyMTY0MTUxWjALBgNVHQ8EBAMCAQYwHwYDVR0jBBgwFoAUSOZo+SvSspXXR9gj
IBBPM5iQn9QwHQYDVR0OBBYEFEjmaPkr0rKV10fYIyAQTzOYkJ/UMAwGA1UdEwQF
MAMBAf8wGgYJKoZIhvZ9B0EABA0wCxsFVjMuMGMDAgbAMA0GCSqGSIb3DQEBBQUA
A4GBAFjOKer89961zgK5F7WF0bnj4JXMJTENAKaSbn+2kmOeUJXRmm/kEd5jhW6Y
7qj/WsjTVbJmcVfewCHrPSqnI0kBBIZCe/zuf6IWUrVnZ9NA2zsmWLIodz2uFHdh
1voqZiegDfqnc1zqcPGUIWVEX/r87yloqaKHee9570+sB3c4
-----END CERTIFICATE-----'''

GOOGLE_INTERNET_AUTHORITY_CERTIFICATE='''-----BEGIN CERTIFICATE-----
MIICsDCCAhmgAwIBAgIDC2dxMA0GCSqGSIb3DQEBBQUAME4xCzAJBgNVBAYTAlVT
MRAwDgYDVQQKEwdFcXVpZmF4MS0wKwYDVQQLEyRFcXVpZmF4IFNlY3VyZSBDZXJ0
aWZpY2F0ZSBBdXRob3JpdHkwHhcNMDkwNjA4MjA0MzI3WhcNMTMwNjA3MTk0MzI3
WjBGMQswCQYDVQQGEwJVUzETMBEGA1UEChMKR29vZ2xlIEluYzEiMCAGA1UEAxMZ
R29vZ2xlIEludGVybmV0IEF1dGhvcml0eTCBnzANBgkqhkiG9w0BAQEFAAOBjQAw
gYkCgYEAye23pIucV+eEPkB9hPSP0XFjU5nneXQUr0SZMyCSjXvlKAy6rWxJfoNf
NFlOCnowzdDXxFdF7dWq1nMmzq0yE7jXDx07393cCDaob1FEm8rWIFJztyaHNWrb
qeXUWaUr/GcZOfqTGBhs3t0lig4zFEfC7wFQeeT9adGnwKziV28CAwEAAaOBozCB
oDAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFL/AMOv1QxE+Z7qekfv8atrjaxIk
MB8GA1UdIwQYMBaAFEjmaPkr0rKV10fYIyAQTzOYkJ/UMBIGA1UdEwEB/wQIMAYB
Af8CAQAwOgYDVR0fBDMwMTAvoC2gK4YpaHR0cDovL2NybC5nZW90cnVzdC5jb20v
Y3Jscy9zZWN1cmVjYS5jcmwwDQYJKoZIhvcNAQEFBQADgYEAuIojxkiWsRF8YHde
BZqrocb6ghwYB8TrgbCoZutJqOkM0ymt9e8kTP3kS8p/XmOrmSfLnzYhLLkQYGfN
0rTw8Ktx5YtaiScRhKqOv5nwnQkhClIZmloJ0pC3+gz4fniisIWvXEyZ2VxVKfml
UUIuOss4jHg7y/j7lYe8vJD5UDI=
-----END CERTIFICATE-----'''

GOOGLE_USER_CONTENT_CERTIFICATE='''-----BEGIN CERTIFICATE-----
MIIEPDCCA6WgAwIBAgIKUaoA4wADAAAueTANBgkqhkiG9w0BAQUFADBGMQswCQYD
VQQGEwJVUzETMBEGA1UEChMKR29vZ2xlIEluYzEiMCAGA1UEAxMZR29vZ2xlIElu
dGVybmV0IEF1dGhvcml0eTAeFw0xMTA4MTIwMzQ5MjlaFw0xMjA4MTIwMzU5Mjla
MHExCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMRYwFAYDVQQHEw1N
b3VudGFpbiBWaWV3MRMwEQYDVQQKEwpHb29nbGUgSW5jMSAwHgYDVQQDFBcqLmdv
b2dsZXVzZXJjb250ZW50LmNvbTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEA
uDmDvqlKBj6DppbENEuUmwVsHe5hpixV0bn6D+Ujy3mWUP9HtkO35/RmeFf4/y9i
nGy78uWO6tk9QY1PsPSiyZN6LgplalBdkTeODCGAieVOVJFhHQ0KM330qDy9sKNM
rwdMOfLPzkBMYPyr1C7CCm24j//aFiMCxD40bDQXRJkCAwEAAaOCAgQwggIAMB0G
A1UdDgQWBBRyHxPfv+Lnm2Kgid72ja3pOszMsjAfBgNVHSMEGDAWgBS/wDDr9UMR
Pme6npH7/Gra42sSJDBbBgNVHR8EVDBSMFCgTqBMhkpodHRwOi8vd3d3LmdzdGF0
aWMuY29tL0dvb2dsZUludGVybmV0QXV0aG9yaXR5L0dvb2dsZUludGVybmV0QXV0
aG9yaXR5LmNybDBmBggrBgEFBQcBAQRaMFgwVgYIKwYBBQUHMAKGSmh0dHA6Ly93
d3cuZ3N0YXRpYy5jb20vR29vZ2xlSW50ZXJuZXRBdXRob3JpdHkvR29vZ2xlSW50
ZXJuZXRBdXRob3JpdHkuY3J0MCEGCSsGAQQBgjcUAgQUHhIAVwBlAGIAUwBlAHIA
dgBlAHIwgdUGA1UdEQSBzTCByoIXKi5nb29nbGV1c2VyY29udGVudC5jb22CFWdv
b2dsZXVzZXJjb250ZW50LmNvbYIiKi5jb21tb25kYXRhc3RvcmFnZS5nb29nbGVh
cGlzLmNvbYIgY29tbW9uZGF0YXN0b3JhZ2UuZ29vZ2xlYXBpcy5jb22CEGF0Z2ds
c3RvcmFnZS5jb22CEiouYXRnZ2xzdG9yYWdlLmNvbYIUKi5zLmF0Z2dsc3RvcmFn
ZS5jb22CCyouZ2dwaHQuY29tgglnZ3BodC5jb20wDQYJKoZIhvcNAQEFBQADgYEA
XDvIl0/id823eokdFpLA8bL3pb7wQGaH0i3b29572aM7cDKqyxmTBbwi9mMMgbxy
E/St8DoSEQg3cJ/t2UaTXtw8wCrA6M1dS/RFpNLfV84QNcVdNhLmKEuZjpa+miUK
8OtYzFSMdfwXrbqKgkAIaqUs6m+LWKG/AQShp6DvTPo=
-----END CERTIFICATE-----'''

# Valid values for bundle.stability field
STABILITY_LITERALS = [
    'obsolete', 'post_stable', 'stable', 'beta', 'dev', 'canary'
]
# Valid values for the archive.host_os field
HOST_OS_LITERALS = frozenset(['mac', 'win', 'linux', 'all'])
# Valid values for bundle-recommended field.
YES_NO_LITERALS = ['yes', 'no']
# Map option keys to manifest attribute key. Option keys are used to retrieve
# option values fromcmd-line options. Manifest attribute keys label the
# corresponding value in the manifest object.
OPTION_KEY_MAP = {
  #  option key         manifest attribute key
    'bundle_desc_url': 'desc_url',
    'bundle_revision': 'revision',
    'bundle_version':  'version',
    'desc':            'description',
    'recommended':     'recommended',
    'stability':       'stability',
}
# Map options keys to platform key, as stored in the bundle.
OPTION_KEY_TO_PLATFORM_MAP = {
    'mac_arch_url':    'mac',
    'win_arch_url':    'win',
    'linux_arch_url':  'linux',
    'all_arch_url':    'all',
}
# Valid keys for various sdk objects, used for validation.
VALID_ARCHIVE_KEYS = frozenset(['host_os', 'size', 'checksum', 'url'])
VALID_BUNDLE_KEYS = frozenset([
    'name', 'version', 'revision', 'description', 'desc_url', 'stability',
    'recommended', 'archives',
])
VALID_MANIFEST_KEYS = frozenset(['manifest_version', 'bundles'])


#------------------------------------------------------------------------------
# General Utilities


_debug_mode = False
_quiet_mode = False


def DebugPrint(msg):
  '''Display a message to stderr if debug printing is enabled

  Note: This function appends a newline to the end of the string

  Args:
    msg: A string to send to stderr in debug mode'''
  if _debug_mode:
    sys.stderr.write("%s\n" % msg)
    sys.stderr.flush()


def InfoPrint(msg):
  '''Display an informational message to stdout if not in quiet mode

  Note: This function appends a newline to the end of the string

  Args:
    mgs: A string to send to stdio when not in quiet mode'''
  if not _quiet_mode:
    sys.stdout.write("%s\n" % msg)
    sys.stdout.flush()


class Error(Exception):
  '''Generic error/exception for sdk_update module'''
  pass


def GetHostOS():
  '''Returns the host_os value that corresponds to the current host OS'''
  return {
      'linux2': 'linux',
      'darwin': 'mac',
      'cygwin': 'win',
      'win32':  'win'
  }[sys.platform]


def ExtractInstaller(installer, outdir):
  '''Extract the SDK installer into a given directory

  If the outdir already exists, then this function deletes it

  Args:
    installer: full path of the SDK installer
    outdir: output directory where to extract the installer

  Raises:
    CalledProcessError - if the extract operation fails'''
  if os.path.exists(outdir):
    RemoveDir(outdir)

  if GetHostOS() == 'win':
    # Run the self-extracting installer in silent mode with a specified
    # output directory
    command = [installer, '/S', '/D=%s' % outdir]
  else:
    os.mkdir(outdir)
    command = ['tar', '-C', outdir, '--strip-components=1',
               '-xvzf', installer]

  subprocess.check_call(command)


def RemoveDir(outdir):
  '''Removes the given directory

  On Unix systems, this just runs shutil.rmtree, but on Windows, this doesn't
  work when the directory contains junctions (as does our SDK installer).
  Therefore, on Windows, it runs rmdir /S /Q as a shell command.  This always
  does the right thing on Windows.

  Args:
    outdir: The directory to delete

  Raises:
    CalledProcessError - if the delete operation fails on Windows
    OSError - if the delete operation fails on Linux
  '''

  InfoPrint('Removing %s' % outdir)
  if sys.platform == 'win32':
    subprocess.check_call(['rmdir /S /Q', outdir], shell=True)
  else:
    shutil.rmtree(outdir)


def ShowProgress(progress):
  ''' A download-progress function used by class Archive.
      (See DownloadAndComputeHash).'''
  global count  # A divider, so we don't emit dots too often.

  if progress == 0:
    count = 0
  elif progress == 100:
    sys.stdout.write('\n')
  else:
    count = count + 1
    if count > 10:
      sys.stdout.write('.')
      sys.stdout.flush()
      count = 0


def DownloadAndComputeHash(from_stream, to_stream=None, progress_func=None):
  ''' Download the archive data from from-stream and generate sha1 and
      size info.

  Args:
    from_stream:   An input stream that supports read.
    to_stream:     [optional] the data is written to to_stream if it is
                   provided.
    progress_func: [optional] A function used to report download progress. If
                   provided, progress_func is called with progress=0 at the
                   beginning of the download, periodically with progress=1
                   during the download, and progress=100 at the end.

  Return
    A tuple (sha1, size) where sha1 is a sha1-hash for the archive data and
    size is the size of the archive data in bytes.'''
  # Use a no-op progress function if none is specified.
  def progress_no_op(progress):
    pass
  if not progress_func:
    progress_func = progress_no_op

  sha1_hash = hashlib.sha1()
  size = 0
  progress_func(progress=0)
  while(1):
    data = from_stream.read(32768)
    if not data:
      break
    sha1_hash.update(data)
    size += len(data)
    if to_stream:
      to_stream.write(data)
    progress_func(progress=1)

  progress_func(progress=100)
  return sha1_hash.hexdigest(), size


class Archive(dict):
  ''' A placeholder for sdk archive information. We derive Archive from
      dict so that it is easily serializable. '''
  def __init__(self, host_os_name):
    ''' Create a new archive for the given host-os name. '''
    self['host_os'] = host_os_name

  def CopyFrom(self, dict):
    ''' Update the content of the archive by copying values from the given
        dictionary.

    Args:
      dict: The dictionary whose values must be copied to the archive.'''
    for key, value in dict.items():
      self[key] = value

  def Validate(self):
    ''' Validate the content of the archive object. Raise an Error if
        an invalid or missing field is found. '''
    host_os = self.get('host_os', None)
    if host_os and host_os not in HOST_OS_LITERALS:
      raise Error('Invalid host-os name in archive')
    # Ensure host_os has a valid string. We'll use it for pretty printing.
    if not host_os:
      host_os = 'all (default)'
    if not self.get('url', None):
      raise Error('Archive "%s" has no URL' % host_os)
    # Verify that all key names are valid.
    for key, val in self.iteritems():
      if key not in VALID_ARCHIVE_KEYS:
        raise Error('Archive "%s" has invalid attribute "%s"' % (host_os, key))

  def _OpenURLStream(self):
    ''' Open a file-like stream for the archives's url. Raises an Error if the
        url can't be opened.

    Return:
      A file-like object from which the archive's data can be read.'''
    try:
      url_stream = urllib2.urlopen(self['url'])
    except urllib2.URLError:
      raise Error('"%s" is not a valid URL for archive %s' %
          (self['url'], self['host_os']))

    return url_stream

  def ComputeSha1AndSize(self):
    ''' Compute the sha1 hash and size of the archive's data. Raises
        an Error if the url can't be opened.

    Return:
      A tuple (sha1, size) with the sha1 hash and data size respectively.'''
    stream = None
    sha1 = None
    size = 0
    try:
      print 'Scanning archive to generate sha1 and size info:'
      stream = self._OpenURLStream()
      sha1, size = DownloadAndComputeHash(from_stream=stream,
                                          progress_func=ShowProgress)
    finally:
      if stream: stream.close()
    return sha1, size

  def DownloadToFile(self, dest_path):
    ''' Download the archive's data to a file at dest_path. As a side effect,
        computes the sha1 hash and data size, both returned as a tuple. Raises
        an Error if the url can't be opened, or an IOError exception if
        dest_path can't be opened.

    Args:
      dest_path: Path for the file that will receive the data.
    Return:
      A tuple (sha1, size) with the sha1 hash and data size respectively.'''
    sha1 = None
    size = 0
    with open(dest_path, 'wb') as to_stream:
      try:
        from_stream = self._OpenURLStream()
        sha1, size = DownloadAndComputeHash(from_stream, to_stream)
      finally:
        if from_stream: from_stream.close()
    return sha1, size

  def Update(self, url):
    ''' Update the archive with the new url. Automatically update the
        archive's size and checksum fields. Raises an Error if the url is
        is invalid. '''
    self['url'] = url
    sha1, size = self.ComputeSha1AndSize()
    self['size'] = size
    self['checksum'] = {'sha1': sha1}


class Bundle(dict):
  ''' A placeholder for sdk bundle information. We derive Bundle from
      dict so that it is easily serializable.'''
  def __init__(self, name):
    ''' Create a new bundle with the given bundle name.

    Args:
      name: A name to give to the new bundle.'''
    self['archives'] = []
    self['name'] = name

  def CopyFrom(self, dict):
    ''' Update the content of the bundle by copying values from the given
        dictionary.

    Args:
      dict: The dictionary whose values must be copied to the bundle.'''
    for key, value in dict.items():
      if key == 'archives':
        archives = []
        for a in value:
          new_archive = Archive(a['host_os'])
          new_archive.CopyFrom(a)
          archives.append(new_archive)
        self['archives'] = archives
      else:
        self[key] = value

  def Validate(self):
    ''' Validate the content of the bundle. Raise an Error if an invalid or
        missing field is found. '''
    # Check required fields.
    if not self.get('name', None):
      raise Error('Bundle has no name')
    if not self.get('revision', None):
      raise Error('Bundle "%s" is missing a revision number' %
                              self['name'])
    if not self.get('description', None):
      raise Error('Bundle "%s" is missing a description' %
                              self['name'])
    if not self.get('stability', None):
      raise Error('Bundle "%s" is missing stability info' %
                              self['name'])
    if self.get('recommended', None) == None:
      raise Error('Bundle "%s" is missing the recommended field' %
                              self['name'])
    # Check specific values
    if self['stability'] not in STABILITY_LITERALS:
      raise Error('Bundle "%s" has invalid stability field: "%s"' %
                              (self['name'], self['stability']))
    if self['recommended'] not in YES_NO_LITERALS:
      raise Error(
          'Bundle "%s" has invalid recommended field: "%s"' %
          (self['name'], self['recommended']))
    # Verify that all key names are valid.
    for key, val in self.iteritems():
      if key not in VALID_BUNDLE_KEYS:
        raise Error('Bundle "%s" has invalid attribute "%s"' %
                    (self['name'], key))
    # Validate the archives
    for archive in self['archives']:
      archive.Validate()

  def GetArchive(self, host_os_name):
    ''' Retrieve the archive for the given host os.

    Args:
      host_os_name: name of host os whose archive must be retrieved.
    Return:
      An Archive instance or None if it doesn't exist.'''
    for archive in self['archives']:
      if archive['host_os'] == host_os_name:
        return archive
    return None

  def UpdateArchive(self, host_os, url):
    ''' Update or create  the archive for host_os with the new url.
        Automatically updates the archive size and checksum info by downloading
        the data from the given archive. Raises an Error if the url is invalid.

    Args:
      host_os: name of host os whose archive must be updated or created.
      url: the new url for the archive.'''
    archive = self.GetArchive(host_os)
    if not archive:
      archive = Archive(host_os_name=host_os)
      self['archives'].append(archive)
    archive.Update(url)

  def Update(self, options):
    ''' Update the bundle per content of the options.

    Args:
      options: options data. Attributes that are used are also deleted from
               options.'''
    # Check, set and consume individual bundle options.
    for option_key, attribute_key in OPTION_KEY_MAP.iteritems():
      option_val = getattr(options, option_key, None)
      if option_val:
        self[attribute_key] = option_val
        delattr(options, option_key);
    # Validate what we have so far; we may just avoid going through a lengthy
    # download, just to realize that some other trivial stuff is missing.
    self.Validate()
    # Check and consume archive-url options.
    for option_key, host_os in OPTION_KEY_TO_PLATFORM_MAP.iteritems():
      platform_url = getattr(options, option_key, None)
      if platform_url:
        self.UpdateArchive(host_os, platform_url)
        delattr(options, option_key);


class SDKManifest(object):
  '''This class contains utilities for manipulation an SDK manifest string

  For ease of unit-testing, this class should not contain any file I/O.
  '''

  def __init__(self):
    '''Create a new SDKManifest object with default contents'''
    self.MANIFEST_VERSION = 1
    self._manifest_data = {
        "manifest_version": self.MANIFEST_VERSION,
        "bundles": []
    }


  def _ValidateManifest(self):
    '''Validate the Manifest file and raises an exception for problems'''
    # Validate the manifest top level
    if self._manifest_data["manifest_version"] > self.MANIFEST_VERSION:
      raise Error("Manifest version too high: %s" %
                              self._manifest_data["manifest_version"])
    # Verify that all key names are valid.
    for key, val in self._manifest_data.iteritems():
      if key not in VALID_MANIFEST_KEYS:
        raise Error('Manifest has invalid attribute "%s"' % key)
    # Validate each bundle
    for bundle in self._manifest_data['bundles']:
      bundle.Validate()

  def _ValidateBundleName(self, name):
    ''' Verify that name is a valid bundle.

    Args:
      name: the proposed name for the bundle.

    Return:
      True if the name is valid for a bundle, False otherwise.'''
    valid_char_set = '()-_.%s%s' % (string.ascii_letters, string.digits)
    name_len = len(name)
    return (name_len > 0 and all(c in valid_char_set for c in name))

  def _GetBundle(self, name):
    ''' Get a bundle from the array of bundles.

    Args:
      name: the name of the bundle to return.
    Return:
      The bundle with the given name, or None if it is not found.'''
    if not 'bundles' in self._manifest_data:
      return None
    bundles = self._manifest_data['bundles']
    for bundle in bundles:
      if 'name' in bundle and bundle['name'] == name:
        return bundle
    return None

  def _AddBundle(self, bundle):
    ''' Add a bundle to the manifest

    Args:
      bundle: to the bundle to add to the manifest.'''
    if not 'bundle' in self._manifest_data:
      self._manifest_data['bundles'] = []
    self._manifest_data['bundles'].append(bundle)

  def _UpdateManifestVersion(self, options):
    ''' Update the manifest version number from the options

    Args:
      options: options data containing an attribute self.manifest_version '''
    version_num = int(options.manifest_version)
    self._manifest_data['manifest_version'] = version_num
    del options.manifest_version

  def _UpdateBundle(self, options):
    ''' Update or setup a bundle from the options.

    Args:
      options: options data containing at least a valid bundle_name
               attribute. Other relevant bundle attributes will also be
               used (and consumed) by this function. '''
    # Get and validate the bundle name
    if not self._ValidateBundleName(options.bundle_name):
      raise Error('Invalid bundle name: "%s"' %
                              options.bundle_name)
    bundle_name = options.bundle_name
    del options.bundle_name
    # Get the corresponding bundle, or create it.
    bundle = self._GetBundle(bundle_name)
    if not bundle:
      bundle = Bundle(name=bundle_name)
      self._AddBundle(bundle)
    bundle.Update(options)

  def _VerifyAllOptionsConsumed(self, options, bundle_name):
    ''' Verify that all the options have been used. Raise an exception if
        any valid option has not been used. Returns True if all options have
        been consumed.

    Args:
      options: the object containg the remaining unused options attributes.
      bundl_name: The name of the bundle, or None if it's missing.'''
    # Any option left in the list should have value = None
    for key, val in options.__dict__.items():
      if val != None:
        if bundle_name:
          raise Error('Unused option "%s" for bundle "%s"' % (key, bundle_name))
        else:
          raise Error('No bundle name specified')
    return True;


  def LoadManifestString(self, json_string):
    ''' Load a JSON manifest string. Raises an exception if json_string
        is not well-formed JSON.

    Args:
      json_string: a JSON-formatted string containing the previous manifest'''
    new_manifest = json.loads(json_string)
    for key, value in new_manifest.items():
      if key == 'bundles':
        # Remap each bundle in |value| to a Bundle instance
        bundles = []
        for b in value:
          new_bundle = Bundle(b['name'])
          new_bundle.CopyFrom(b)
          bundles.append(new_bundle)
        self._manifest_data[key] = bundles
      else:
        self._manifest_data[key] = value
    self._ValidateManifest()


  def GetManifestString(self):
    '''Returns the current JSON manifest object, pretty-printed'''
    pretty_string = json.dumps(self._manifest_data, sort_keys=False, indent=2)
    # json.dumps sometimes returns trailing whitespace and does not put
    # a newline at the end.  This code fixes these problems.
    pretty_lines = pretty_string.split('\n')
    return '\n'.join([line.rstrip() for line in pretty_lines]) + '\n'

  def UpdateManifest(self, options):
    ''' Update the manifest object with value from the command-line options

    Args:
      options: options object containing attribute for the command-line options.
               Note that all the non-trivial options are consumed.
    '''
    # Go over all the options and update the manifest data accordingly.
    # Valid options are consumed as they are used. This gives us a way to
    # verify that all the options are used.
    if options.manifest_version is not None:
      self._UpdateManifestVersion(options)
    # Keep a copy of bundle_name, which will be consumed by UpdateBundle, for
    # use in _VerifyAllOptionsConsumed below.
    bundle_name = options.bundle_name
    if bundle_name is not None:
      self._UpdateBundle(options)
    self._VerifyAllOptionsConsumed(options, bundle_name)
    self._ValidateManifest()


class SDKManifestFile(object):
  ''' This class provides basic file I/O support for manifest objects.'''

  def __init__(self, json_filepath):
    '''Create a new SDKManifest object with default contents.

    Args:
      json_filepath: path to jason file to read/write, or None to write a new
      manifest file to stdout.'''
    self._json_filepath = json_filepath
    self._manifest = SDKManifest()

  def _LoadFile(self):
    '''Load the manifest from the JSON file. This function returns quietly
       if the file doesn't exit.'''
    if not os.path.exists(self._json_filepath):
      return

    with open(self._json_filepath, 'r') as f:
      json_string = f.read()
    if json_string:
      self._manifest.LoadManifestString(json_string)


  def _WriteFile(self):
    '''Write the json data to the file. If not file name was specified, the
       data is written to stdout.'''
    json_string = self._manifest.GetManifestString()
    if not self._json_filepath:
      # No file is specified; print the json data to stdout
      sys.stdout.write(json_string)
    else:
      # Write the JSON data to a temp file.
      temp_file_name = None
      with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(json_string)
        temp_file_name = f.name
      # Move the temp file to the actual file.
      if os.path.exists(self._json_filepath):
        os.remove(self._json_filepath)
      shutil.move(temp_file_name, self._json_filepath)

  def UpdateWithOptions(self, options):
    ''' Update the manifest file with the given options. Create the manifest
        if it doesn't already exists. Raises an Error if the manifest doesn't
        validate after updating.

    Args:
      options: option data'''
    if self._json_filepath:
      self._LoadFile()
    self._manifest.UpdateManifest(options)
    self._WriteFile()


class ManifestTools(object):
  '''Wrapper class for supporting the SDK manifest file'''

  def __init__(self, options):
    self._options = options
    self._manifest = SDKManifest()

  def LoadManifest(self):
    DebugPrint("Running LoadManifest")
    try:
      # TODO(mball): Add certificate validation on the server
      url_stream = urllib2.urlopen(self._options.manifest_url)
    except urllib2.URLError:
      raise Error('Unable to open %s' % self._options.manifest_url)
    manifest_stream = cStringIO.StringIO()
    sha1, size = DownloadAndComputeHash(
        url_stream, manifest_stream)
    self._manifest.LoadManifestString(manifest_stream.getvalue())

  def GetBundles(self):
    return self._manifest._manifest_data['bundles']


#------------------------------------------------------------------------------
# Commands


def List(options, argv):
  '''Usage: %prog [options] list

  Lists the available SDK bundles that are available for download.'''
  DebugPrint("Running List command with: %s, %s" %(options, argv))

  parser = optparse.OptionParser(usage=List.__doc__)
  (list_options, args) = parser.parse_args(argv)
  tools = ManifestTools(options)
  tools.LoadManifest()
  bundles = tools.GetBundles()
  InfoPrint('Available bundles:\n')
  for bundle in bundles:
    InfoPrint(bundle['name'])
    for key, value in bundle.iteritems():
      if key not in ['archives', 'name']:
        InfoPrint("  %s: %s" % (key, value))


def Update(options, argv):
  '''Usage: %prog [options] update [target]

  Updates the Native Client SDK to a specified version.  By default, this
  command updates all the recommended components

  Targets:
    recommended: (default) Install/Update all recommended components
    all:         Install/Update all available components'''
  DebugPrint("Running Update command with: %s, %s" % (options, argv))

  parser = optparse.OptionParser(usage=Update.__doc__)
  parser.add_option(
      '-F', '--force', dest='force',
      default=False, action='store_true',
      help='Force updating existing components that already exist')
  (update_options, args) = parser.parse_args(argv)
  tools = ManifestTools(options)
  tools.LoadManifest()
  bundles = tools.GetBundles()
  for bundle in bundles:
    bundle_name = bundle['name']
    bundle_path = os.path.join(options.sdk_root_dir, bundle_name)
    if not update_options.force and os.path.exists(bundle_path):
      InfoPrint('Skipping bundle %s because directory already exists and is '
                'up-to-date.' % bundle_name)
      InfoPrint('Use --force option to force overwriting existing directory')
      continue
    archive = bundle.GetArchive(GetHostOS())
    (scheme, host, path, _, _, _) = urlparse.urlparse(archive['url'])
    dest_filename = os.path.join(options.user_data_dir, path.split('/')[-1])
    InfoPrint('Downloading %s archive to %s' % (bundle_name, dest_filename))
    sha1, size = archive.DownloadToFile(os.path.join(options.user_data_dir,
                                                     dest_filename))
    if sha1 != archive['checksum']['sha1']:
      raise Error("SHA1 checksum mismatch.  Expected %s but got %s" %
                  (archive['checksum']['sha1'], sha1))
    if size != archive['size']:
      raise Error("Size mismatch on Archive.  Expected %s but got %s bytes" %
                  (archive['size'], size))
    InfoPrint('Extracting %s' % bundle_name)
    ExtractInstaller(dest_filename, bundle_path)
    os.remove(dest_filename)


#------------------------------------------------------------------------------
# Command-line interface


def main(argv):
  '''Main entry for the sdk_update utility'''
  parser = optparse.OptionParser(usage=GLOBAL_HELP)

  parser.add_option(
      '-U', '--manifest-url', dest='manifest_url',
      default='https://commondatastorage.googleapis.com/nativeclient-mirror/'
              'nacl/nacl_sdk/%s' % MANIFEST_FILENAME,
      help='override the default URL for the NaCl manifest file')
  parser.add_option(
      '-d', '--debug', dest='debug',
      default=False, action='store_true',
      help='enable displaying debug information to stderr')
  parser.add_option(
      '-q', '--quiet', dest='quiet',
      default=False, action='store_true',
      help='suppress displaying informational prints to stdout')
  parser.add_option(
      '-u', '--user-data-dir', dest='user_data_dir',
      # TODO(mball): the default should probably be in something like
      # ~/.naclsdk (linux), or ~/Library/Application Support/NaClSDK (mac),
      # or %HOMEPATH%\Application Data\NaClSDK (i.e., %APPDATA% on windows)
      default=os.path.dirname(os.path.abspath(__file__)),
      help="specify location of NaCl SDK's data directory")
  parser.add_option(
      '-s', '--sdk-root-dir', dest='sdk_root_dir',
      default=os.path.dirname(os.path.abspath(__file__)),
      help="location where the SDK bundles are installed")
  parser.add_option(
      '-v', '--version', dest='show_version',
      action='store_true',
      help='show version information and exit')

  COMMANDS = {
      'list': List,
      'update': Update,
  }

  # Separate global options from command-specific options
  global_argv = argv
  command_argv = []
  for index, arg in enumerate(argv):
    if arg in COMMANDS:
      global_argv = argv[:index]
      command_argv = argv[index:]
      break

  (options, args) = parser.parse_args(global_argv)
  args += command_argv

  global _debug_mode, _quiet_mode
  _debug_mode = options.debug
  _quiet_mode = options.quiet

  def PrintHelpAndExit(unused_options=None, unused_args=None):
    parser.print_help()
    exit(1)

  if options.show_version:
    print "Native Client SDK Updater, version %s.%s" % (MAJOR_REV, MINOR_REV)
    exit(0)

  if not args:
    print "Need to supply a command"
    PrintHelpAndExit()

  def DefaultHandler(unused_options=None, unused_args=None):
    print "Unknown Command: %s" % args[0]
    PrintHelpAndExit()

  def InvokeCommand(args):
    command = COMMANDS.get(args[0], DefaultHandler)
    command(options, args[1:])

  if args[0] == 'help':
    if len(args) == 1:
      PrintHelpAndExit()
    else:
      InvokeCommand([args[1], '-h'])
  else:
    InvokeCommand(args)

  return 0  # Success


if __name__ == '__main__':
  return_value = 1
  try:
    return_value = main(sys.argv[1:])
  except exceptions.SystemExit:
    raise
  except Error as error:
    print "Error: %s" % error
  except:
    if not _debug_mode:
      print "Abnormal program termination: %s" % sys.exc_info()[1]
      print "Run again in debug mode (-d option) for stack trace."
    else:
      raise

  sys.exit(return_value)
