
import subprocess
import os
import shutil
import glob
import re
import argparse
import sys
from datetime import datetime
mistune = __import__('mistune')

# Checking for dev command

parser = argparse.ArgumentParser()
parser.add_argument(
    "-prod", "--prod", help="Prints the supplied argument.", action="store_true")
args = parser.parse_args()

print(args.prod)

buildUrl = ""
if args.prod == False:
    buildUrl = "/"
else:
    buildUrl = "https://thomasorus.github.io/Gautoz/"


# Generates html files in the site folder, using the entries and the template.

def generateHtmlPages(siteFolder, entries, template, subPagesList):
    for val in entries:

        pageTemplate = re.sub('pageTitle', val['title'], template)

        # Checking if root file
        if val["file"] == "index":
            val["pageContent"] = val["pageContent"] + subPagesList
            pageTemplate = re.sub('pageBody', val['pageContent'], pageTemplate)
        else:
            pageTemplate = re.sub('pageBody', val['pageContent'], pageTemplate)

        # Checking if navigation has value
        if val["parentUrl"] == "":
            navHtml = "<nav><em>Revenir à <a href='" + buildUrl + \
                "'>"+val['parentText'] + "</a></em></nav>"
            pageTemplate = re.sub('pageNavigation', navHtml, pageTemplate)
        else:
            navHtml = "<nav><em>Revenir à <a href='" + \
                "/" + val['parentUrl'] + "'>" + \
                val['parentText'] + "</a></em></nav>"
            pageTemplate = re.sub('pageNavigation', navHtml, pageTemplate)

        pageTemplate = re.sub('buildUrl', buildUrl, pageTemplate)

        # Create sub folders
        folderExists = os.path.exists(siteFolder+val['folder'])
        if folderExists == False:
            os.mkdir(siteFolder+val['folder'])

        pageFile = open(siteFolder + val['slug'], "w")
        pageFile.write(pageTemplate)
        pageFile.close()
    print("All pages created!")

# Recovers the html template to be used on the website


def getHtmlTemplate(templatePath):
    template = open(templatePath, 'r')
    html = template.read()
    return html

# Parses markdown and converts it to html


def getPageContent(page):
    pageContent = open(page, 'r')
    html = mistune.markdown(pageContent.read())
    return html

# Get title by parsing and cleaning the first line of the markdown file


def getEntryTitle(page):
    pageContent = open(page, 'r')
    textContent = pageContent.read()
    textContent = textContent.splitlines()
    textContent = textContent[0]
    textContent = textContent.replace('# ', '')
    return textContent

# Get the slug from the markdown file name


def getEntrySlug(page):
    slug = page.split("/")[-1]
    slug = re.sub('\.md$', '', slug)
    if slug:
        return slug
    else:
        return ''

# From the list of files, creates the main array of entries that will be processed later


def createEntries(pages):
    fullContent = []
    for page in pages:
        tempPage = {}

        path = cleanPath(page)

        title = getEntryTitle(page)
        pageContent = getPageContent(page)

        tempPage['slug'] = path["slug"]
        tempPage['file'] = path['file']
        tempPage['folder'] = path["folder"]
        tempPage['parentUrl'] = path['parentUrl']
        tempPage['parentText'] = path['parentText']
        tempPage['date'] = path['date']
        tempPage['usDate'] = path['usDate']
        tempPage['title'] = title
        tempPage['pageContent'] = pageContent

        fullContent.append(tempPage)

    return fullContent

# Recursively gather all files locations into an array


def listPages(contentFolder):
    pages = glob.glob(contentFolder + '**/*.md', recursive=True)
    return pages

# Deletes existing dist folder and its content then recreates it
# as well as the media folder


def deleteWebsite(siteFolder):
    print("Deleting site...")
    siteExists = os.path.exists(siteFolder)
    if siteExists:
        shutil.rmtree(siteFolder)

    print("Creating folders...")
    os.mkdir(siteFolder)
    os.mkdir(siteFolder+"media")
    os.mkdir(siteFolder+"assets")


# Copies css source to dist
def moveAssets(siteFolder, path):
    assets = os.listdir(path)
    if assets:
        for asset in assets:
            asset = os.path.join(path, asset)
            if os.path.isfile(asset):
                shutil.copy(asset, siteFolder+path)
    else:
        print("No assets found!")

# Transforms the file locations to an array of strings


def cleanPath(path):
    path = re.sub('\.md$', '', path)
    items = path.split('/')
    pathItems = {}
    pathItems["slug"] = path + ".html"
    pathItems["folder"] = items[0]
    pathItems["file"] = items[1]
    if pathItems["file"] == "index":
        pathItems["parentUrl"] = ""
        pathItems["parentText"] = "l'accueil"
    else:
        pathItems["parentUrl"] = items[0]
        pathItems["parentText"] = items[0]
    pathItems["date"] = items[1]
    if pathItems["date"] != "index":
        pathItems["usDate"] = str(
            datetime.strptime(pathItems["date"], '%d-%m-%Y'))
    else:
        pathItems["usDate"] = str(datetime.strptime("01-01-2000", '%d-%m-%Y'))
    return pathItems


def generateSubPages(entries, num, folder, title):
    entries.sort(key=lambda x: x["usDate"], reverse=True)
    selectedEntries = entries[:num]
    subPageList = "<ul class='listing flow-small'>"
    for entry in selectedEntries:
        if title == True:
            linkUrl = entry["slug"]
        else:
            linkUrl = entry["file"] + ".html"

        if entry["file"] != "index":
            entryString = "<li><a href='" + \
                linkUrl + "'>" + entry["date"] + \
                " : " + entry["title"] + "</a></li>\n"
            subPageList = subPageList + entryString
    subPageList += "</ul>"

    if title == True:
        title = "<h2>" + folder.capitalize() + \
            "</h2>"
        subPageList = title + subPageList
        subPageLink = "<small><a href='" + buildUrl + folder + "'>Voir tout</a></small>"
        subPageList += subPageLink
    return subPageList


def createHomePage(template, siteFolder):
    homeFile = open("home.md", "r")
    html = mistune.markdown(homeFile.read()) + "ContentList"

    template = re.sub('pageTitle', "Accueil", template)
    template = re.sub('pageBody', html, template)
    template = re.sub('buildUrl', buildUrl, template)
    template = re.sub('pageNavigation', "", template)

    return template


# Main function, generates the website


def generateWebsite(siteFolder, contentFolder, templateFile, assetsPath):
    print('Welcome to the builder!')
    deleteWebsite(siteFolder)
    template = getHtmlTemplate(templateFile)
    homePage = createHomePage(template, siteFolder)

    for folder in contentFolder:
        pages = listPages(folder + "/")
        entries = createEntries(pages)
        subPagesList = generateSubPages(entries, len(entries), folder, False)
        homePageSubList = generateSubPages(entries, 5, folder, True)
        homePage = re.sub('ContentList', homePageSubList +
                          "ContentList", homePage)

        generateHtmlPages(siteFolder, entries, template, subPagesList)
        moveAssets(siteFolder, assetsPath)

    homePage = re.sub('ContentList', "", homePage)
    pageFile = open(siteFolder + "index.html", "w")
    pageFile.write(homePage)
    pageFile.close()


generateWebsite('docs/', ['matinales'],
                'partials/main.html', 'assets/')
