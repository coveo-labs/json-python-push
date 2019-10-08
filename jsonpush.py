# -*- coding: utf8 -*-
#!/usr/bin/env python
# -------------------------------------------------------------------------------------
# Push json document to Coveo push source
# -------------------------------------------------------------------------------------

import os

from coveopush import CoveoPush
from coveopush import Document
from coveopush import DocumentToDelete
from coveopush import CoveoPermissions
from coveopush import CoveoConstants

import argparse
from datetime import date
import json
import re
import unicodedata
import html


def checkArgs():
  #Check all arguments
  parser = argparse.ArgumentParser(description='JsonPythonPush to Coveo')
  parser.add_argument('-org', type=str, help='Coveo Organization ID')
  parser.add_argument('-source', type=str, help='Coveo Source ID')
  parser.add_argument('-apikey', type=str, help='Coveo Push API Key')
  parser.add_argument('-json', type=str, help='JSON file to process')
  parser.add_argument('-uri', type=str, help='Uri contruction for the index')
  parser.add_argument('--action', type=str, default='INITIAL',
                      help='Action (INITIAL or UPDATE)')
  parser.add_argument('--key', type=str, help='Key for the results')
  parser.add_argument('--quickview', type=str, help='Quickview HTML file')
  parser.add_argument('--createfields', type=str,
                      help='Will create Fields in supplied Fields file.')

  return parser.parse_args()


def checkSettings(settings):
    # Check all settings
    check = True
    if (settings.action != 'INITIAL' and settings.action != 'UPDATE'):
        check = False
        print("-action should be INITIAL or UPDATE")
    if (settings.quickview != ''):
        # Check if file exists
        if (not os.path.exists(settings.quickview)):
            check = False
            print("-quickview, file: "+settings.quickview+" does not exists.")
    if (settings.json != ''):
        # Check if file exists
        if (not os.path.exists(settings.json)):
            check = False
            print("-json, file: "+settings.json+" does not exists.")

    return check


def cleanCol(colname):
  #Cleans the column, removes accents, remove bad characters
  def strip_accents(text):
      try:
          text = unicode(text, 'utf-8')
      except (TypeError, NameError):  # unicode is a default on python 3
          pass
      text = unicodedata.normalize('NFD', text)
      text = text.encode('ascii', 'ignore')
      text = text.decode("utf-8")
      return str(text)

  def text_to_id(text):
      """
      Convert input text to id.

      :param text: The input string.
      :type text: String.

      :returns: The processed String.
      :rtype: String.
      """
      text = strip_accents(text.lower())
      text = re.sub('[ ]+', '_', text)
      text = re.sub('-', '_', text)
      text = re.sub('[^0-9a-zA-Z_-]', '', text)
      text = text.lower()
      return text

  return text_to_id(colname)


def mapFields(jsond, text):
    # Maps field definitions like %[fieldname] to their actual contents
    for key in jsond.keys():
        # encode html
        text = text.replace("%["+key+"]", html.escape(str(jsond[key])))
        #! decode html
        text = text.replace("%[!"+key+"]", html.unescape(str(jsond[key])))
        # > as is
        # html.unescape(html.escape(str(jsond[key])).encode('ascii', 'xmlcharrefreplace').decode()))
        text = text.replace("%[>"+key+"]", str(jsond[key]))
    return text


def translateJson(jsond):
  #Will flatten the JSON, including nested objects
  out = {}

  def flatten(x, name=''):
      if type(x) is dict:
          for a in x:
              flatten(x[a], name + a + '_')
      elif type(x) is list:
          i = 0
          for a in x:
              # flatten(a, name + str(i) + '_')
              flatten(a, name)
              i += 1
      else:
          colname = cleanCol(name[:-1])
          if colname in out:
              out[colname] = out[colname]+';'+x
          else:
              out[colname] = x

  flatten(jsond)
  return out


def compare_json_data(source_data_a, source_data_b):
    result = True
    for key in source_data_a.keys():
        if not key in source_data_b:
            result = False
        elif not source_data_a[key] == source_data_b[key]:
            result = False
    return result


def updatedData(key, jsond, previous, settings):
  #Check if the previous data was updated/changed
  thesame = False
  found = False
  # check if key is in previous
  counter = 0
  for item in previous:
      currentkey = item['mykeyX']
      if (key == currentkey):
          found = True
          # print (item)
          # print (jsond)
          # if so check if json is the same
          if compare_json_data(jsond, item):
              thesame = True
          else:
              thesame = False

          previous[counter]['mykeyfoundX'] = currentkey
          break
      counter = counter + 1
  return thesame, found, previous


def createQuickview(content, mydoc, settings):
    # Build up the quickview/preview (HTML)
    # Add allfields and metadata
    allfields = ''
    parsedQuickview = settings.quickviewHTML
    for key in content.keys():
        if ("%[>"+key+"]" in parsedQuickview):
            value = mapFields(content, "%[>"+key+"]")
        elif ("%[!"+key+"]" in parsedQuickview):
            value = mapFields(content, "%[!"+key+"]")
        else:
            value = mapFields(content, "%["+key+"]")
        parsedQuickview = mapFields(content, parsedQuickview)
        allfields = allfields + ' '+value
        if (mydoc):
            mydoc.AddMetadata(key, mapFields(content, "%[>"+key+"]"))
    # Clean up
    parsedQuickview = parsedQuickview.replace(r"%[ALLFIELDS]", allfields)
    parsedQuickview = parsedQuickview.replace(r"%[.*]", '')
    return parsedQuickview, mydoc


def processDocument(content, settings):
    # Create new push document
    uri = mapFields(content, settings.uri)
    mydoc = Document(uri)
    print("Processing: "+uri)
    parsedQuickview, mydoc = createQuickview(content, mydoc, settings)
    # print(parsedQuickview)
    mydoc.SetContentAndZLibCompress(parsedQuickview)
    # Set the fileextension
    mydoc.FileExtension = ".html"

    return mydoc


def addFacet(name, number):
  if (not number):
    facet = {}
    facet['name'] = name
    facet['type'] = "STRING"
    facet['includeInQuery'] = True
    facet['includeInResults'] = True
    facet['mergeWithLexicon'] = True
    facet['smartDateFacet'] = False
    facet['facet'] = False
    facet['multiValueFacet'] = True
    facet['sort'] = False
    facet['ranking'] = False
    facet['stemming'] = False
    facet['multiValueFacetTokenizers'] = ";"
    facet['useCacheForNestedQuery'] = False
    facet['useCacheForSort'] = False
    facet['useCacheForNumericQuery'] = False
    facet['useCacheForComputedFacet'] = False
    facet['system'] = False
    return facet

  else:
    facet = {}
    facet['name'] = name
    facet['type'] ="DOUBLE"
    facet['includeInQuery'] = True
    facet['includeInResults'] = True
    facet['mergeWithLexicon'] = False
    facet['smartDateFacet']= False
    facet['facet']=True
    facet['multiValueFacet']= False
    facet['sort']=True
    facet['ranking']= False
    facet['stemming']=False
    facet['multiValueFacetTokenizers']=";"
    facet['useCacheForNestedQuery']=False
    facet['useCacheForSort']= False
    facet['useCacheForNumericQuery']= False
    facet['useCacheForComputedFacet']=False
    facet['system']=False
    return facet
            

def getAllFields(settings):
    allf = {}
    allFacets = []
    first = True
    print("Getting all fields.")
    print("Step 1. Reading file and checking all fields.")
    with open(settings.json, encoding='utf8') as data_file:
        currentdata = json.load(data_file)
    for content in currentdata:
        jsond = translateJson(content)
        if (first):
            allf = jsond
            first = False
        else:
            for key in jsond.keys():
              if (str(jsond[key])!=""):
                allf[key] = jsond[key]
    # Create facets
    for key in allf.keys():
        # check if number
        x = re.search(r"^[\d.,]*$", str(allf[key]))
        if (x==None):
          # Not a number
          allFacets.append(addFacet(key,False))
        else:
          # A Number
          allFacets.append(addFacet(key,True))

    print("Step 2. Creating report.")
    fieldfile = open(settings.createfields, "w")
    fieldfile.writelines(
        ["===========================================================\n"])
    fieldfile.writelines(["FIELDS: "+str(len(allf))+"\n"])
    for key in allf.keys():
        fieldfile.writelines([key+'\n'])
    fieldfile.writelines(
        ["===========================================================\n"])
    fieldfile.writelines(["JSON:\n"])
    fieldfile.writelines([json.dumps(allFacets)+'\n'])
    fieldfile.writelines(
        ["===========================================================\n"])
    for key in allf.keys():
        fieldfile.writelines([key+": "+str(allf[key])+'\n'])

    print("Step 2. Creating report Quickview.")
    fieldfile.writelines(
        ["===========================================================\n"])
    fieldfile.writelines(["KEY\n"])
    fieldfile.writelines([mapFields(allf, settings.key)+'\n'])
    fieldfile.writelines(
        ["===========================================================\n"])
    fieldfile.writelines(["URI\n"])
    fieldfile.writelines([mapFields(allf, settings.uri)+'\n'])
    fieldfile.writelines(
        ["===========================================================\n"])
    fieldfile.writelines(["QUICKVIEW\n"])
    parsedQuickview, mydoc = createQuickview(allf, '', settings)
    fieldfile.writelines([parsedQuickview+'\n'])
    fieldfile.writelines(
        ["===========================================================\n"])

    fieldfile.close()


if __name__ == '__main__':
    settings = checkArgs()
    if (checkSettings(settings)):
        if (settings.createfields != ''):
            # load quickview html
            if (settings.quickview != ''):
                with open(settings.quickview, encoding='utf8') as data_HTML:
                    settings.quickviewHTML = data_HTML.read()
            getAllFields(settings)
        else:
            settings.quickviewHTML = ''
            fulldata = []
            today = date.today()
            push = CoveoPush.Push(
                settings.source, settings.org, settings.apikey)
            push.SetSizeMaxRequest(50*1024*1024)
            removeOld = True
            if (settings.action == 'UPDATE'):
                removeOld = False

            push.Start(True, removeOld)

            print("----------------------------------------------------------")
            print("Run       : "+str(today))
            print("Org       : "+settings.org)
            print("Source    : "+settings.source)
            print("JSON File : "+settings.json)
            print("Action    : "+settings.action)
            print("Uri format: "+settings.uri)
            print("----------------------------------------------------------")

            # load quickview html
            if (settings.quickview != ''):
                with open(settings.quickview, encoding='utf8') as data_HTML:
                    settings.quickviewHTML = data_HTML.read()

            first = True
            executePush = False
            updatefile = open(settings.json+"NEW_PREV.json", "w")
            # updatefile.write("[".encode('utf-8'))
            updatefile.write("[")
            with open(settings.json, encoding='utf8') as data_file:
                currentdata = json.load(data_file)
                previousdata = []
                if (settings.action == 'UPDATE'):
                    if (os.path.exists(settings.json+'PREV')):
                        with open(settings.json+'PREV', encoding='utf8') as data_prev:
                            previousdata = json.loads(
                                data_prev.read(), encoding='utf-8')
                            counter = 0
                            for item in previousdata:
                                previousdata[counter]['mykeyX'] = mapFields(
                                    item, settings.key)
                                counter = counter + 1
                # process currentdata
                for content in currentdata:
                    jsond = translateJson(content)
                    if (first):
                        first = False
                        # print(jsond)
                        # print(previousdata[0])
                    else:
                        updatefile.write(",")  # .encode('utf-8'))
                    updatefile.write(json.dumps(jsond))  # .encode('utf-8'))
                    processDoc = False
                    if (settings.action == 'INITIAL'):
                        processDoc = True

                    if (settings.action == 'UPDATE'):
                        key = mapFields(jsond, settings.key)

                        print("Key="+key)
                        theSame = False
                        found = False
                        theSame, found, previousdata = updatedData(
                            key, jsond, previousdata, settings)
                        if (found and not theSame):
                            print("Found, changed, update")
                            processDoc = True
                        if (found and theSame):
                            print("Found, NOT changed, skip")
                            processDoc = False
                        if (not found):
                            print("not Found, add")
                            processDoc = True

                    if (processDoc):
                        doctoadd = processDocument(jsond, settings)
                        push.Add(doctoadd)
                        executePush = True
            updatefile.write("]")  # .encode('utf-8'))
            updatefile.close()
            # Remove old previous file
            if (os.path.exists(settings.json+'PREV')):
                os.remove(settings.json+'PREV')
            # Rename updatefile
            os.rename(settings.json+"NEW_PREV.json", settings.json+'PREV')
            # Add deleted to push
            for content in previousdata:
                if (not 'mykeyfoundX' in content):
                    currentkey = mapFields(content, settings.uri)
                    print("To delete: "+currentkey)
                    todel_document = DocumentToDelete(currentkey)
                    push.Add(todel_document)
                    executePush = True
            if (executePush):
                push.End(True, removeOld)
            else:
                push.UpdateSourceStatus(
                    CoveoConstants.Constants.SourceStatusType.Idle)
