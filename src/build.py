
import subprocess
import os
import shutil
import glob
import re
import argparse
import sys
mistune = __import__('mistune')

# Checking for dev command

parser = argparse.ArgumentParser()
parser.add_argument(
    "-dev", "--dev", help="Prints the supplied argument.", action="store_true")
args = parser.parse_args()

print(args.dev)

buildUrl = ""
if args.dev == True:
    buildUrl = "/"
else:
    buildUrl = "https://thomasorus.github.io/Gautoz/"
    # Generates html files in the site folder, using the entries and the template.
    # Also triggers the creation of the breadcrumb and the submenu


def generateHtmlPages(siteFolder, entries, template):
    for val in entries:

        pageTemplate = re.sub('pageTitle', val['title'], template)
        pageTemplate = re.sub('pageBody', val['pageContent'], pageTemplate)
        pageTemplate = re.sub('parentLink', val['parent'], pageTemplate)
        pageTemplate = re.sub('parentString', val['folder'], pageTemplate)
        pageTemplate = re.sub('buildUrl', buildUrl, pageTemplate)

        # Create matinales folder
        folderExists = os.path.exists(siteFolder+val['parent'])
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
        tempPage['folder'] = path["folder"]
        tempPage['parent'] = path['parent']
        tempPage['date'] = path['date']
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
    pathItems["parent"] = "/" + items[0] + "/"
    pathItems["date"] = items[1]
    return pathItems

# Main function, generates the website


def generateWebsite(siteFolder, contentFolder, templateFile, assetsPath):
    print('Welcome to the builder!')
    deleteWebsite(siteFolder)
    pages = listPages(contentFolder)
    entries = createEntries(pages)
    template = getHtmlTemplate(templateFile)
    generateHtmlPages(siteFolder, entries, template)
    moveAssets(siteFolder, assetsPath)


generateWebsite('docs/', 'matinales/', 'partials/main.html', 'assets/')
