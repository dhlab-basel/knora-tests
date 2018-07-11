#!/usr/bin/env python3

import requests, json, urllib, sys, os, re
import xml.etree.ElementTree as ET
import traceback

def get_date_from_title(titlestr):
    # year or month precision
    # generally, imprecision is expressed with '00'
    # but there are also cases in which the day is missing (hence optional)
    m = re.match("^(\d{4})-(\d{2})(-(\d{2}))?", titlestr)

    # the expression did not match
    if m is None:
        raise Exception("invalid date: " + titlestr)

    # no date given
    if m.group(0) == "0000-00-00":
        return None

    # check for precision
    # '00' means no day or month given

    # 3 -> day precision (containing '-')
    # 4 -> day precision (without '-')
    if m.group(3) is not None and m.group(4) != '00':
        # a date with day precision
        return "GREGORIAN:" + m.group(1) + '-' + m.group(2) + '-' + m.group(4)
    # 2 -> month precision
    elif m.group(2) is not None and m.group(2) != '00':
        # a date with month precision
        return "GREGORIAN:" + m.group(1) + '-' + m.group(2)
    else:
        # year precision
        return "GREGORIAN:" + m.group(1)

def create_mapping():
    try:
        beolProjectIri = "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF"
        base_url = "http://localhost/v1/"

        beolUser = "t.schweizer@unibas.ch"

        # create mapping

        mappingParams = {
            "project_id": beolProjectIri,
            "label": "BEBB letter mapping",
            "mappingName": "BEBBLetterMapping"
        }

        mappingRequest = requests.post(base_url + "mapping",
                                    data={"json": json.dumps(mappingParams)},
                                    files={"xml": ("mappingForLetter.xml", open("mappingForLetter.xml"))},
                                    auth=(beolUser, "test"),
                                    proxies={'http': 'http://localhost:3333'})

        mappingRequest.raise_for_status()

        print("Created mapping")

    except requests.exceptions.HTTPError as e:
        sys.stderr.write("http request failed: \n")
        sys.stderr.write(str(e.response.status_code) + "\n")
        sys.stderr.write(e.response.text)

    except:
        sys.stderr.write("a non http related error occurred:")
        traceback.print_exc()


def create_letters():
    try:
        beolProjectIri = "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF"
        base_url = "http://localhost/v1/"

        beolUser = "t.schweizer@unibas.ch"

        mappingIri = beolProjectIri + "/mappings/BEBBLetterMapping"

        pathToXML = "xml/1704-01-26_Bernoulli_Johann_I-Hermann_Jacob.xml"

        letterResources = {}

        print("Creating letters (without text)")

        # number of runs for the same file
        limit = 2000

        for i in range(0, limit):

            etree = ET.parse(pathToXML)

            root = etree.getroot()

            # attributes of root node letter
            attributes = root.attrib

            # include counter in title
            letter_title = attributes['title'] + "_" + str(i)

            # create a letter resource
            letterParams = {
                "restype_id": 'http://www.knora.org/ontology/0801/beol#letter',
                "label": attributes['title'],
                "properties": {"http://www.knora.org/ontology/0801/beol#title": [
                    {"richtext_value": {"utf8str": letter_title}}
                ]},
                "project_id": beolProjectIri
            }

            date = get_date_from_title(attributes["title"])

            # append date if given
            if date is not None:
                letterParams["properties"].update({
                    "http://www.knora.org/ontology/0801/beol#creationDate": [
                        {"date_value": date}
                    ]
                })

            # create letter
            letterRequest = requests.post(base_url + "resources",
                                        data=json.dumps(letterParams),
                                        auth=(beolUser, "test"),
                                        headers={'content-type': 'application/json; charset=utf8'},
                                        proxies={'http': 'http://localhost:3333'})

            letterRequest.raise_for_status()

            print(i)

            # look up table letter title to letter Iri
            letterIri = letterRequest.json()['res_id']
            letterResources.update({letter_title: letterIri})

        print("Adding texts to letters")

        path_to_capsules = "images/"

        for i in range(0, limit):

            print(i)

            etree = ET.parse(pathToXML)

            root = etree.getroot()

            # attributes of root node letter
            attributes = root.attrib

            text = root.findall("./text")
            if len(text) != 1:
                raise Exception("no element <text> found in " + pathToXML)

            letter_title = attributes['title'] + "_" + str(i)
            letterIri = letterResources[letter_title]

            facsimiles = root.findall("./images/facsimile")

            if len(facsimiles) > 0:
                # get the corresponding images
                img_dir = path_to_capsules + attributes['catalogue_id'] + "/image"

                if os.path.isdir(img_dir):
                    images = os.listdir(img_dir)
                    # check if the number of facsimiles matches the number of given files for this letter

                    # filter out all files that are not tiff image files
                    images = list(filter(lambda ele: ele.lower().endswith(".tif") or ele.lower().endswith(".tiff"), images))

                    if len(facsimiles) == len(images):
                        # translate references to tif names
                        for j, fac in enumerate(facsimiles):
                            print(fac.attrib["src"] + " -> " + img_dir + "/" + images[j])
                            # create beol:page for images[j]
                            pageParams = {
                                "restype_id": 'http://www.knora.org/ontology/0801/beol#page',
                                "label": images[j],
                                "properties": {
                                    "http://www.knora.org/ontology/0801/beol#partOf": [
                                    {"link_value": letterIri}
                                ],
                                "http://www.knora.org/ontology/0801/beol#seqnum": [
                                    {"int_value": j}
                                ],
                                "http://www.knora.org/ontology/0801/beol#pagenum": [
                                    {"richtext_value": {"utf8str": images[j]}}
                                ]},
                                "project_id": beolProjectIri
                            }

                            mimetype = 'image/tiff'

                            files = {'file': (images[j], open(img_dir + "/" + images[j], 'rb'), mimetype)}

                            pageCreationRequest = requests.post(base_url + "resources",
                                        data={'json': json.dumps(pageParams)},
                                        files=files,
                                        headers=None,
                                        auth=(beolUser, "test"),
                                        proxies={'http': 'http://localhost:3333'})


                            pageCreationRequest.raise_for_status()

                            # exchange reference to old URL in text with page Iri
                            facRefs = text[0].findall(".//*[@src='" + fac.attrib["src"] + "']")

                            for facRef in facRefs:
                                facRef.attrib["src"] = pageCreationRequest.json()['res_id']



                    else:
                        sys.stderr.write("numbers of facsimiles and images do not match for " + pathToXML + "\n")
                        sys.stderr.write("++++++++++\n")
                        # the facsimile elements have to be treated specially once their type is IRI

                else:
                    # we do not have full quality tiff images for this letter,
                    # download the linked images

                    sys.stderr.write("directory not found: " + img_dir + " for " + pathToXML + "\n")

                    img_url = ""
                    img_name = ""
                    for j, fac in enumerate(facsimiles):
                        if "http://www.e-manuscripta.ch/zuz/content/pageview/" in fac.attrib["src"]:
                            # the pagenumber is the last segment of the e-manuscripta url
                            pagenum = fac.attrib["src"].rfind("/")
                            # append the pagenumber to the url
                            img_url = "http://www.e-manuscripta.ch/zuz/image/view/" + fac.attrib["src"][(pagenum + 1):]
                            img_name = str(pagenum) + ".jpg"
                        else:
                            # get the file from UB Basel
                            img_url = fac.attrib["src"]
                            pagenum = fac.attrib["src"].rfind("/")
                            img_name = fac.attrib["src"][(pagenum + 1):]

                        print(img_url)

                        # get the image binaries and create a page resource
                        img = requests.get(img_url)

                        img.raise_for_status()

                        pageParams = {
                            "restype_id": 'http://www.knora.org/ontology/0801/beol#page',
                            "label": img_url,
                            "properties": {
                                "http://www.knora.org/ontology/0801/beol#partOf": [
                                    {"link_value": letterIri}
                                ],
                                "http://www.knora.org/ontology/0801/beol#seqnum": [
                                    {"int_value": j}
                                ],
                                "http://www.knora.org/ontology/0801/beol#pagenum": [
                                    {"richtext_value": {"utf8str": img_url}}
                                ]},
                            "project_id": beolProjectIri
                        }

                        mimetype = 'image/jpeg'

                        files = {'file': (img_name, img.content, mimetype)}

                        pageCreationRequest = requests.post(base_url + "resources",
                                                            data={'json': json.dumps(pageParams)},
                                                            files=files,
                                                            headers=None,
                                                            auth=(beolUser, "test"),
                                                            proxies={'http': 'http://localhost:3333'})

                        pageCreationRequest.raise_for_status()

                        # exchange reference to old URL in text with page Iri
                        facRefs = text[0].findall(".//*[@src='" + fac.attrib["src"] + "']")

                        for facRef in facRefs:
                            facRef.attrib["src"] = pageCreationRequest.json()['res_id']


                    sys.stderr.write("++++++++++\n")

            nonExistingEntity = False

            # transform letter titles in references to letter Iris
            entities = text[0].findall(".//entity")
            for entity in entities:
                ref = entity.attrib['ref'].strip()
                if not ref in letterResources:
                    sys.stderr.write(attributes['title'] + ": ")
                    sys.stderr.write("no Iri found for " + ref + " in entities\n")
                    # skip this letter
                    nonExistingEntity = True
                else:
                    entity.attrib['ref'] = letterResources[ref]

            if nonExistingEntity:
                # if there is a reference to a non exiting entity, skip this letter
                continue

            textParams = {
                "res_id": letterIri,
                "prop": "http://www.knora.org/ontology/0801/beol#hasText",
                "project_id": beolProjectIri,
                "richtext_value": {
                    "xml": ET.tostring(text[0], encoding="unicode", method="xml"),
                    "mapping_id": mappingIri
                }
            }

            print(textParams)

            textCreationRequest = requests.post(base_url + "values",
                                                data=json.dumps(textParams),
                                                auth=(beolUser, "test"),
                                                headers={'content-type': 'application/json; charset=utf8'},
                                                proxies={'http': 'http://localhost:3333'})

            textCreationRequest.raise_for_status()

            print("http://localhost:3333/v1/" + "values/" + urllib.parse.quote_plus(
                textCreationRequest.json()['id']))

            textGetRequest = requests.get(
                base_url + "values/" + urllib.parse.quote_plus(textCreationRequest.json()['id']),
                auth=(beolUser, "test"),
                proxies={'http': 'http://localhost:3333'})

            print(attributes['title'])
            print(textGetRequest.json()['value']['xml'])
            print("+++++++++++")


    except requests.exceptions.HTTPError as e:
        sys.stderr.write("http request failed: \n")
        if "attributes" in locals():
            sys.stderr.write(attributes['title']  + "\n")
        sys.stderr.write(str(e.response.status_code) + "\n")
        sys.stderr.write(e.response.text)

    except:
        sys.stderr.write("a non http related error occurred:")
        if "attributes" in locals():
            sys.stderr.write(attributes['title'])
        traceback.print_exc()

if __name__ == '__main__':
    create_mapping()
    create_letters()
