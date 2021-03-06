#!/usr/bin/env python
import os
import re
import sys
import json
import csv
import pprint

data = '../data/output'
cumm = 0

def csv_to_dict():
  csvpath = os.path.join('..', 'data', 'refs.csv')

  with open(csvpath, 'r') as csvfile:
    # CSV reader specifies delimiter and variable that holds contents
    csvreader = csv.reader(csvfile, delimiter=',')

    #  Each row is read as a row
    for row in csvreader:
      print(row)


def write_file(filename1, filename2, filename3):

  output_file = open(filename3, "wb")
  writer = csv.writer(output_file, delimiter=',')


  topics = []
  rid = 0
  topic = ''
  subtopic = ''
  notes = ''

  writer.writerow(['id','topic','subtopic','author','vol','alpha','omega','passage','notes'])
  def writeline():
    writer.writerow([rid, topic, subtopic, author, vol, alpha, omega, passage, notes])

  with open(filename1, 'r') as text:
    topics.append(text.strip())

  with open(filename2, 'r') as text:
    lines = text.split('\r')
    for line in lines:
      if line:
        if line[0]:
          if line[0].isdigit():
            num, description = line.split('\t')
            subtopic = num.rstrip('.')

            if subtopic == '1':
              topic = topics.pop(0)

          elif line[0] == '\t':
            vol, refs = line.split('\t')[1:3]

            if vol == '0' or vol == '1' or vol == '2':
              vol = vol.rstrip(':')
              refs = refs.split('/')
              author = 'Bible'

              for ref in refs:
                alpha = ''
                omega = ''
                notes = ''

                ref = ref.strip()
                if ';' in ref:
                  passages = ref.split(';')
                  book = passages[0].split(',', 1)[0]
                  for passage in passages:

                    if passage[0].isalpha() or passage[1] == " ":
                      passage = passage.split(',', 1)[1]
                    rid += 1

                    if 'passim' in passage or 'esp' in passage:
                      e = passage.find('esp')
                      e = e if e > -1 else 50

                      p = passage.find('passim')
                      p = p if p > -1 else 50

                      index = p if p < e else e

                      verses = passage[0:index]
                      notes = passage[index:]
                      passage = verses.strip()
                    passage = book + passage

                    writeline()

                else:
                  passage = ref.replace(',', '', 1)
                  rid += 1

                  writeline()

            else:
              passage = ''
              refs = refs.split(',')
              author = refs.pop(0).strip()
              if author == 'James' or author == 'Eliot':
                surname = refs.pop(0)
                author = author + surname.replace(' ', ', ')
              for ref in refs:
                rid += 1
                ref = ref.lstrip()
                alpha = ref
                omega = ''
                notes = ''
                if '-' in ref:
                  alpha, omega = ref.split("-", 1)
                  if "passim" in omega or "esp" in omega:
                    omega, notes = omega.split(" ", 1)
                else:
                  alpha = ref
                  if " " in ref:
                    alpha, notes = ref.split(" ", 1)

                writeline()

  output_file.close()

def topics_dict(filename, filename2):
  topics = []
  syntopicon = {}

  input_file = open(filename, 'r')
  for string in input_file:
    topics.append(string.strip())

  input_file2 = open(filename2, 'r')
  for string in input_file2:

    topic = ''
    subtopic = ''
    refs = ''
    author = ''

    count = 0

    lines = string.split('\r')
    for line in lines:

      if line == '':

        topic = topics.pop(0)
        count = 0

      else:

        if line[0] == '\t':

          contents = line.split('\t')

          if len(contents) < 3:
            vol, refs = contents[1].split(': ')
            refs = refs.split('/')

          else:
            vol, refs = contents[1:3]
            refs = refs.split(',')
            author = refs.pop(0)

          syntopicon[topic][subtopic]['refs'] = {vol: refs}

        elif line[0].isdigit():

          subtopic = line

          syntopicon[topic][subtopic] = line

  input_file.close()
  input_file2.close()
  return syntopicon

def print_topics(filename, filename2):
  topic_list = topics_dict(filename, filename2)
  topics = topic_list.keys()
  for topic in topics:
    print topic
    # subtopics = topic_list[topic].keys()
    # for subtopic in subtopics:
      # print '\t'
      # print topic_list[topic][subtopic].description

def make_json():
  file = open('../data/subtopics.txt', 'r')
  output = open('../data/subtopics.json', 'w')

  alltopics = {}
  alltopics['topics'] = []
  count = 1
  currTopic = ''
  currSubtopic = '0'

  for string in file:
    lines = string.split('\r')
    for line in lines:
      line = line.rstrip()
      if line[0].isalpha():
        topic = line
        currTopic = topic
        objj = {'topic': topic, 'subtopics': [], 'number': count}
        alltopics['topics'].append(objj)
        count += 1
      elif line[0] == '\t':
        num, desc = line.split('\t')[1:3]
        desc = desc.rstrip()
        subObj = {'number': num, 'subtopic': desc}

        if num[-1] == '.':
          num = num[:-1]
          currSubtopic = num
          subObj['number'] = num
        elif num[0] == '(':
          num = currSubtopic + num
          subObj['number'] = num

        alltopics['topics'][-1]['subtopics'].append(subObj)


  json.dump(alltopics, output)
  output.close()
  file.close()

def make_topics_csv(json_file, csv_file):
  jsonPath = os.path.join('..','data', json_file)
  csvPath = os.path.join('..','data',csv_file)
  output_file = open(csvPath, 'w')

  with open(jsonPath, 'r') as input_file:
    topics = json.load(input_file)['topics']
    topicwriter = csv.writer(output_file, delimiter=',')
    topicwriter.writerow(['topic','subtopic','topnum','subtopnum'])

    for topic in topics:
      for sub in topic["subtopics"]:
        row = [topic["topic"], sub["subtopic"], topic["number"], sub["number"]]
        topicwriter.writerow(row)
  output_file.close()
  print(".csv written to %s" % (csvPath))

def convert_bytes(num):
  for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
    if num < 1024.0:
      return "%3.1f %s" % (num, x)
    num /= 1024.0

def file_size(file_path):
  if os.path.isfile(file_path):
    file_info = os.stat(file_path)
    return file_info.st_size

def listFileSize(directory=data):
  o = path.Path(directory)
  for d in o.dirs():
    for f in d.files():
      with open(f, 'r') as z:
        length = str(z)
        print (length)
  #     s = file_size(f)
  #     if (s > 7000):
  #       cumm += s
  # print(convert_bytes(cumm))

def retrieve(vol, page):
  filepath = os.path.join(data, str(vol), str(page))
  with open(filepath, 'r') as output:
    for text in output:
      return text

def retrieveMany(vol, start, end):
  data = ''
  start = int(start)
  end = int(end)+1
  for i in range(start, end):
    page = retrieve(vol, i)
    data += page
  print(data)
  return data

def main():
  # if len(sys.argv) < 3:
  #   print ('usage: ./retrieve.py vol first page [last page]')
  #   sys.exit(1)

  # vol = sys.argv[1]
  # start = sys.argv[2]
  # if len(sys.argv) != 4:
  #   end = sys.argv[2]
  # else:
  #   end = sys.argv[3]

  csv_to_dict()

if __name__ == '__main__':
  main()