#!/usr/bin/env python

import json
import jenkins
import re
import datetime
from pymongo import MongoClient
import requests
import time
import configparser
import os

class JenkinsCollector():
   
   def __init__(self, cfg):
      global client
      self.client = jenkins.Jenkins(cfg['jenkins']['url'], username=cfg['jenkins']['username'], password=cfg['jenkins']['password'])

   def all_jobs(self):
      return self.client.get_jobs(folder_depth=1)

   def job_info(self, name):
      return self.client.get_job_info(name)
 
   def all_build_numbers(self, job_name):
      builds = []
      for build in self.job_info(job_name)['builds']:
         builds.append(build['number'])
      return builds
    
   def build_info(self, job_name, build_number):
      return self.client.get_build_info(job_name, int(build_number))

class JenkinsBuild():
   def __init__(self, build):
      self.build = build
   
   def building(self):
      return self.build['building']

   def number(self):
      return self.build['number']

   def buildUrl(self):
      return self.build['url']

   def buildStatus(self):
      return self.build['result']

   def startTime(self):
      return int(self.build['timestamp'])

   def jobUrl(self):
      url = self.buildUrl().split('/')
      url = url[:-2]
      return '/'.join(url)

   def instanceUrl(self):
      url = self.buildUrl().split('/')
      url = url[:-6]
      return '/'.join(url)

   def duration(self):
      return self.build['duration']

   def endTime(self):
      return int(self.build['timestamp'])+int(self.build['duration'])

   def scmRevisionNumber(self): 
      numbers = []
      if len(self.build['changeSets']) > 0:
         return self.build['changeSets'][0]['revisions'][0]['revision']
      else: 
         return "0"

   def scmCommitLogs(self):
      logs = []
      if len(self.build['changeSets']) > 0:
         for item in self.build['changeSets'][0]['items']:
            if (item['msg'] == '' or item['msg'] is None):
               logs.append('no message')
            else:
               logs.append(item['msg'])
      else:
         logs.append('none')
      return logs

   def scmAuthors(self):
      authors = []
      if len(self.build['changeSets']) > 0:
         for item in self.build['changeSets'][0]['items']:
            authors.append(item['author']['fullName'])
      else:
         authors.append('none')
      return authors

   def scmCommitTimestamp(self):
      return -1

   def scmNumberOfChanges(self):
      return 1

   def niceName(self):
      return 'Jenkins'

def loadConfig():
   global cfg
   cfg = configparser.ConfigParser()
   cfg_path = unicode(os.path.dirname(os.path.realpath(__file__)) + '/hygieia_jenkins.properties', 'utf8')
   cfg.read(cfg_path)

def main():
   loadConfig()
   mongo_client = MongoClient(cfg['db']['host'])
   db = mongo_client.dashboard
   db.authenticate(cfg['db']['username'], cfg['db']['password'])

   collector = JenkinsCollector(cfg)
   for job in collector.all_jobs():
      if re.search(cfg['jenkins']['folder'], job['fullname']):
         builds = collector.all_build_numbers(job['fullname'])
         for b in builds:
            if (isNewBuild(db, job['fullname'], b)) == True:
               build = JenkinsBuild(collector.build_info(job['fullname'], str(b)))
               if build.building() == False:
                  data = {}
                  data['number'] = build.number()
                  data['buildUrl'] = build.buildUrl()
                  data['jobName'] = job['fullname']
                  data['buildStatus'] = build.buildStatus()
                  data['startTime'] = int(build.startTime())
                  data['jobUrl'] = build.jobUrl()
                  data['instanceUrl'] = build.instanceUrl()
                  data['niceName'] = build.niceName()
                  data['endTime'] = int(build.endTime())
                  data['duration'] = int(build.duration())
                  data['sourceChangeSet'] = []
                  change_set = {}
                  if ( len(build.scmAuthors()) == 1 and build.scmAuthors()[0] == 'none'):
                     change_set['scmRevisionNumber'] = build.scmRevisionNumber()
                     change_set['scmCommitLog'] = ''.join(build.scmCommitLogs())
                     change_set['scmAuthor'] = ''.join(build.scmCommitLogs())
                     change_set['scmCommitTimestamp'] = build.scmCommitTimestamp()
                     change_set['numberOfChanges'] = build.scmNumberOfChanges()
                     data['sourceChangeSet'].append(change_set)
                  else:
                     for index, author in enumerate(build.scmAuthors()):
                        change_set['scmRevisionNumber'] = build.scmRevisionNumber()
                        change_set['scmCommitLog'] = build.scmCommitLogs()[index]
                        change_set['scmAuthor'] = author
                        change_set['scmCommitTimestamp'] = build.scmCommitTimestamp()
                        change_set['numberOfChanges'] = build.scmNumberOfChanges()
                        data['sourceChangeSet'].append(change_set)
                        change_set = {}
                  url = cfg['hygieia']['api_url'] + '/build'
                  data_json = json.dumps(data)
                  headers = {'Content-type': 'application/json'}
                  r = requests.post(url, data=data_json, headers=headers)
 
def isNewBuild(db, job, build):
   query = {'description': job}
   item = db.collector_items.find(query)
   job_id = ''
   for i in item:
      job_id = i['_id']
   query = {'collectorItemId': job_id, 'number': str(build)}
   build = db.builds.find(query)
   if build.count() == 0:
      return True
   else:
      return False

if __name__ == "__main__":
    main()
