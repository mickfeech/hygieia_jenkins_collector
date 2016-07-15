# Hygieia Jenkins Build Collector

Jenkins build collector for the Hygieia DevOps Dashboard.  Supports the use of Jenkins 2.0 pipeline and the Jenkins Folders plugin.

## Python Requirements

* json
* jenkins
* re
* datetime
* pymongo
* requests
* time
* configparser
* os

## Configuration

*hygieia_jenkins.properties*
```
[jenkins]
url=http://servername:port
username=jenkins_user_name
password=jenkins_password
folder=jenkins_folder_to_search

[db]
host=localhost
username=db
password=dbpass

[hygieia]
api_url=http://servername:port/api
```

## Uses

*Setup a cronjob to regularly gather jenkins build data*

```
*/15 * * * * /home/hygieia/hygieia_jenkins_collector.py >/dev/null 2>&1
```
