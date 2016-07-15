# Hygieia Jenkins Build Collector

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
