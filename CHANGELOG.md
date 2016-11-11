## 3.0.3-1 (Nov 11 2016)

Fixes

  - Issue (race condition) in lockfile. Oops.

Improvements

  - Improve pidfile name resolution/path resolution handling.

## 3.0.2-1 (Nov 10 2016)

Fixes

  - Implement proper lockfile handling

## 3.0.1-1 (Oct 31 2016)

Fixes

  - Fixed issue with the transmit function (related) to the major refactor
  - Fixed a bug on Python 2.6 where logging.handlers.SysLogHandler doesn't support socktype


## 3.0.0-1 (Oct 10 2016)

Major Feature:

  - Major change to add a new item that contains the overall health of a particular check. This will catch *any* failures or oddities by
  the application and if this value is 1 you may alert (in addition to whichever triggers you wish to make for your items)  (#23, @jonkelleyatrackspace)
  - changed final exit code to 2 for failed checks, 1 for program/network error, 0 for successful

Cleanup:
  - improved style
  - code readability
  - yaml file format examples

## 2.2.0-1 (Oct 10 2016)

Feature:

  - Add feature to skip checks based on puppet facts, shell env, or custom command output (#23, @jonkelleyatrackspace)

## 2.1.0-1 (Oct 10 2016)

Feature:

  - add pidfile for run locking (#23, @jonkelleyatrackspace)

## 2.0.1-1 (Oct 10 2016)

Cleanup:

  - pep updates (#23, @jonkelleyatrackspace)
  - code refactoring and cleanup (#23, @jonkelleyatrackspace)

## 2.0.0-1 (Sep 19 2016)

Feature:

  - Add support for using custom zabbix host name. (#20, @jonkelleyatrackspace)
  - Rename zabbix: host to zabbix: server, to make room for new feature. (#20, @jonkelleyatrackspace)

## 1.1.2-2 (Sep 16 2016)

Feature:

  - Adding an stdout message to print the worst return status code seen for a particular set of check(s). (@jonkelleyatrackspace)
  - Change output info message to only appear in debug, to limit confusion for the status code evaluation. (@jonkelleyatrackspace)

## 1.1.0-1 (Jul 27 2016)

Bugfixes:

  - Fix the --key flag for selective run. (@jonkelleyatrackspace)
  - Fix the yaml configuration file to meet YAML spec. (@jonkelleyatrackspace)

Docs:

  - Update readme to match new configs (@jonkelleyatrackspace)

## 1.0.2-1 (Jul 27 2016)

Cleanup:

  - Remove misreferenced packaging import(s) (@jonkelleyatrackspace)
  - Remove {url} from epilog output (@jonkelleyatrackspace)
  - Remove __author__ from __init__ (@jonkelleyatrackspace)

Bugfixes:

  - Make zbx_send timeouts cast into float() from configparser (@jonkelleyatrackspace)
  - Fix a missing ) in the config parser. (@jonkelleyatrackspace)

## 1.0.0-1 (Jul 18 2016)

Bugfixes:

  - Fix a bug where missing variable from packaging.py (@jonkelleyatrackspace)

## 0.9.0-1 (Jul 10 2016)

Bugfixes:

  - Added forked process for non interrupting io from zabbix. (@jonkelleyatrackspace)
  - Many other improvements (@jonkelleyatrackspace)

## 0.8.5-1 (Apr 29 2016)

Bugfixes:

  - Fixes to work better when singleton doesnt take, like on py2.6 (@jonkelleyatrackspace)
