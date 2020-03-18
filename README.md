# JSON Python Push

This program will push JSON files into a Coveo Push source.

Features:

- Is using the Coveo Python SDK
- Create Fields, will create a field definition file so you can create automatically the necessary fields.
- Supports updates. The previous JSON will be saved, based on the current changes only the changes will be pushed to the source.
- For every JSON property (including nested) a fieldname will be created.
- Is using Batch Push calls.

See the [examples](https://github.com/coveo-labs/json-python-push/tree/master/examples) on how to call the program


## Installation
** Use 64 bit Python **
** Use Python 3 **

Make sure you have [git](https://git-scm.com/downloads) installed.

Then, in your command prompt, enter the following command:

Install Program:
```
git clone https://github.com/coveo-labs/json-python-push.git
```

Install SDK (might need to use pip3 if two versions of python are installed):
```
pip install git+https://github.com/coveo-labs/SDK-Push-Python --upgrade
```

This SDK depends on the [Python Requests](http://docs.python-requests.org/en/master/user/install/#install) and [JSONPickle](https://jsonpickle.github.io/#download-install) libraries. If you do not already have them, you need to run the following commands (might need to use pip3 if two versions of python are installed):

```
pip install requests
pip install jsonpickle
```

## Prerequisites

Before pushing a document to a Coveo Cloud organization, you need to ensure that you have a Coveo Cloud organization, and that this organization has a [Push source](https://docs.coveo.com/en/94/cloud-v2-developers/creating-a-push-source).

Once you have those prerequisites, you need to get your Organization Id, Source Id, and API Key. For more information on how to do that, see [Push API Tutorial 1 - Managing Shared Content](https://docs.coveo.com/en/92/cloud-v2-developers/push-api-tutorial-1---managing-shared-content).


## JSON requirements

The JSON can contain nested objects/arrays. All will be parsed. The following JSON:
```json
[{"productCode":"35870226","masterProductCode":"35870226","productName":"prodname","shortDescription":"descr","description":[{"Type":"Brick","Length in cm":"20","Material":"Rock","Color":"Transparent"}]},
```

The output will get the following fieldnames:
```
productcode
masterproductcode
productname
shortdescription
description_type
description_length_in_cm
description_material
description_color
```

### CreateFields

Before you can start pushing, you will need to create Fields. 

1. Create a file and use appropriate file extension (.sh for mac, or .bat for windows). 
Example: Fields.sh (or Fields.bat - if on windows)

2. Inside the file paste the following parameters:
```bat
python jsonpush.py -org "orginzationId" -apikey "ApiKey" -json "test.json" -createfields "fields.json"
```

it will output all the (new) fields into the file referenced. 

The file will contain: all fieldnames, followed by the JSON for the [Fields call](https://platform.cloud.coveo.com/rest/organizations/{organizationId}/indexes/fields/batch/create).
The URI, KEY and an example of the created Quickview.


#### Now check the field definition and change it accordingly. Once a field is set, its content type cannot be changed!!!

The contents of this file can be used in: [Swagger Call](https://platform.cloud.coveo.com/docs?api=Field#!/Fields/rest_organizations_paramId_indexes_fields_batch_create_post).

### Index/Parameters

There are two index actions: Update or Initial.
Update will check for a previous JSON file and will check the current file for changes. Only changes will be processed.
Initial will push all JSON records to the new source.

Example update:
```bat
python jsonpush.py -org "ORGID" -source "SOURCEID" -apikey "xxx-aaa" -json "myjsonfile.json" -uri "https://a.b?%[productcode]"  --action "UPDATE" --key "%[productcode]%[mastercode]" --quickview "VIEW.HTML"

```

Example initial:
```bat
python jsonpush.py -org "ORGID" -source "SOURCEID" -apikey "xxx-aaa" -json "myjsonfile.json" -uri "https://a.b?%[productcode]" --action "INITIAL" --key "%[productcode]%[mastercode]" --quickview "VIEW.HTML"
```

Parameters explained:
* `-org`: The Org id of the Coveo organization
* `-source`: The Source id of the Coveo source
* `-apikey`: The API Key which was copied during the creation process of the Push source.
* `-json`: File which contains the JSON contents
* `-uri`: The uri to construct. Format: %[fieldname]
* `--action`: Action to perform (INITIAL or UPDATE)
* `--key`: The unique key to check for the updates. Format: %[fieldname]
* `--quickview`: The HTML file used for the quickview rendering.
* `--createfields`: The file to use to store all the found fieldnames. 

### Fields reference
Inside the `key` and `quickview` files you can use references to the fields inside the json. The following format is supported:
* `%[fieldname]` will output the field with HTML encoding.
* `%[!fieldname]` will output the field with HTML decode.
* `%[>fieldname]` will output the field as-is.

### Quickview file
The quickview file referred in the parameters should contain the HTML used for the rendering.
The fields can be referenced like:
`%[fieldname]`. If you simply want to include all metadata fields, use: `%[ALLFIELDS]`.

Example:
```html
<meta charset='UTF-16'>
<meta http-equiv='Content-Type' content='text/html; charset=UTF-16'>
<html>
<head>
<title>%[productname]</title>
</head>
<body>
<h1>%[productname]</h1>
%[ALLFIELDS]
</body>
</html>
```
### Changes
Oct 2019: Initial

### Dependencies
- [Python 3.x](https://www.python.org/downloads/)
- [Python Requests](http://docs.python-requests.org/en/master/user/install/#install)
- [JSONPickle](https://jsonpickle.github.io/#download-install)
- [Push SDK](https://github.com/coveo-labs/SDK-Push-Python)

### References
- [Coveo Push API](https://docs.coveo.com/en/68/cloud-v2-developers/push-api)

### Authors
- [Wim Nijmeijer](https://github.com/wnijmeijer)
