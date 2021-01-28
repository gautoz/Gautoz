
import subprocess
import os
import shutil
import glob
import re
import argparse
import sys
from datetime import datetime
mistune = __import__('mistune')
renderer = mistune.Renderer()
markdown = mistune.Markdown(renderer=renderer)
config = __import__('config')


# Checking for dev command
parser = argparse.ArgumentParser()
parser.add_argument(
    "-prod", "--prod", help="Prints the supplied argument.", action="store_true")
args = parser.parse_args()

# Declaring build url that will be used in several parts of the app
buildUrl = ""
if args.prod == False:
    buildUrl = config.relativeBuildUrl
else:
    buildUrl = config.absoluteBuildUrl


# Generates html files in the site folder, using the entries and the template.
def generateHtmlPages(siteFolder, entries, template, subPagesList):
    for val in entries:
        pageTemplate = re.sub('pageTitle', val['title'], template)

        # Checking if the page is root of a folder
        if val["file"] == "index":

            # If root page
            # Concatenate the content of the index page with the listing of sub-pages
            # Remove "pageDate" from template
            # Replaces "pageBody" with the page content in the template
            val["pageContent"] = val["pageContent"] + subPagesList
            pageTemplate = re.sub('pageDate', "", pageTemplate)
            pageTemplate = re.sub('pageBody', val['pageContent'], pageTemplate)
        else:
            # If content page
            # Replaces "pageBody" with the page content in the template
            # Replaces "pageDate" with the page date in the template
            pageTemplate = re.sub('pageBody', val['pageContent'], pageTemplate)
            pageTemplate = re.sub('pageDate', "<date>" +
                                  val['date'] + "</date>", pageTemplate)

        # Creating navigation
        if val["parentUrl"] == "":
            # If index page, return to the home
            navHtml = "<nav><em>Revenir à <a href='" + buildUrl + \
                "'>"+val['parentText'] + "</a></em></nav>"
            pageTemplate = re.sub('pageNavigation', navHtml, pageTemplate)
        else:
            # If content page, return to parent page
            navHtml = "<nav><em>Revenir à <a href='" + buildUrl + val['parentUrl'] + "'>" + \
                val['parentText'] + "</a></em></nav>"
            pageTemplate = re.sub('pageNavigation', navHtml, pageTemplate)

        # Replaces all occurrences of buildUrl in the template files (assets, urls, etc)
        pageTemplate = re.sub('buildUrl', buildUrl, pageTemplate)

        pageTemplate = re.sub('siteName', config.siteName, pageTemplate)
        pageTemplate = re.sub('siteMetaDescription',
                              config.siteMetaDescription, pageTemplate)
        pageTemplate = re.sub('twitterName', config.twitterName, pageTemplate)

        # Checking if content folder exists
        folderExists = os.path.exists(siteFolder+val['folder'])
        # If not, create it
        if folderExists == False:
            os.mkdir(siteFolder+val['folder'])

        # Write the HTML file
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
    html = markdown(pageContent.read())
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

        # Process the page with dedicated functions
        path = cleanPath(page)
        title = getEntryTitle(page)
        pageContent = getPageContent(page)

        # Create the page object with all the informations we need
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


# Deletes existing production folder and its content then recreates it
# Same for the assets folder
def deleteWebsite(siteFolder, assetsPath):
    print("Deleting site...")
    # Checks if production folder exists
    siteExists = os.path.exists(siteFolder)
    if siteExists:
        shutil.rmtree(siteFolder)

    print("Creating folders...")
    os.mkdir(siteFolder)
    os.mkdir(siteFolder + assetsPath)


# Copy assets to production folder
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

    # Converts the EU date to US date to allow page sorting
    if pathItems["date"] != "index":
        pathItems["usDate"] = str(
            datetime.strptime(pathItems["date"], '%d-%m-%Y'))
    else:
        # If index page, add a fake date to avoid empty object
        pathItems["usDate"] = str(datetime.strptime("01-01-2000", '%d-%m-%Y'))

    return pathItems


# Generate the list of sub pages for each section
def generateSubPages(entries, num, folder, title):

    # Sort entries by date using the usDate format
    entries.sort(key=lambda x: x["usDate"], reverse=True)

    # Take n number of entries (5 for the home, all for the sub-section pages)
    selectedEntries = entries[:num]

    # Create the list
    subPageList = "<ul class='listing'>"
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

    # If a title is necessary, use the folder name
    if title == True:
        title = "<h2>" + folder.capitalize() + \
            "</h2>"
        subPageList = title + subPageList
        subPageLink = "<small><a href='" + buildUrl + folder + "'>Voir tout</a></small>"
        subPageList += subPageLink

    return subPageList


# Creates the home page using home.md
def createHomePage(template, siteFolder):

    # Read the file
    homeFile = open("home.md", "r")

    # Add "contentList" as a future replacement point for sub page listing
    html = markdown(homeFile.read()) + "ContentList"

    # Replace template strings with content
    template = re.sub('pageTitle', "Accueil", template)
    template = re.sub('pageBody', html, template)
    template = re.sub('buildUrl', buildUrl, template)
    template = re.sub('pageNavigation', "", template)

    return template


# Create RSS Feed
def createRssFeed(rssEntries, rssTemplate, rssItemTemplate, siteFolder):
    template = getHtmlTemplate(rssTemplate)
    itemTemplate = getHtmlTemplate(rssItemTemplate)
    rssEntries.sort(key=lambda x: x["usDate"], reverse=True)

    rssItems = ""
    for rssEntry in rssEntries:
        entryTemplate = itemTemplate
        entryTemplate = re.sub(
            'rssItemTitle', rssEntry["title"], entryTemplate)
        entryTemplate = re.sub('rssItemUrl', buildUrl +
                               rssEntry["slug"], entryTemplate)
        entryTemplate = re.sub(
            'rssItemDate', rssEntry["usDate"], entryTemplate)
        entryTemplate = re.sub(
            'rssItemContent', rssEntry["pageContent"], entryTemplate)
        rssItems = rssItems + entryTemplate

    template = re.sub('siteName', config.siteName, template)
    template = re.sub('siteMetaDescription',
                      config.siteMetaDescription, template)
    template = re.sub('buildUrl', buildUrl, template)
    template = re.sub('dateBuild', str(datetime.now().date()), template)
    template = re.sub('rssContent', rssItems, template)

    rssFile = open(siteFolder + "feed.xml", "w")
    rssFile.write(template)
    rssFile.close()
    return


def generateWebsite(siteFolder, contentFolder, templateFile, assetsPath, rssTemplate, rssItemTemplate):
    print('Welcome to the builder!')
    deleteWebsite(config.buildFolder, assetsPath)
    template = getHtmlTemplate(templateFile)
    homePage = createHomePage(template, siteFolder)
    rssEntries = []

    for folder in contentFolder:
        pages = listPages(folder + "/")
        entries = createEntries(pages)
        subPagesList = generateSubPages(entries, len(entries), folder, False)

        # For each section, create a short listing of sub pages and add it to the home page
        homePageSubList = generateSubPages(entries, 5, folder, True)
        homePage = re.sub('ContentList', homePageSubList +
                          "ContentList", homePage)
        homePage = re.sub('pageDate', "", homePage)

        generateHtmlPages(siteFolder, entries, template, subPagesList)

        for entry in entries:
            rssEntries.append(entry)

     # Move the assets
    moveAssets(siteFolder, assetsPath)

    # Once all sections have been processed, finish the home page
    # Removes the "ContentList" in the partial
    homePage = re.sub('ContentList', "", homePage)
    homePage = re.sub('siteName', config.siteName, homePage)
    homePage = re.sub('siteMetaDescription',
                      config.siteMetaDescription, homePage)
    homePage = re.sub('twitterName', config.twitterName, homePage)
    pageFile = open(siteFolder + "index.html", "w")
    pageFile.write(homePage)
    pageFile.close()

    # Create RSS File
    createRssFeed(rssEntries, rssTemplate, rssItemTemplate, siteFolder)


# Triggers the website build
generateWebsite(config.buildFolder, config.contentFolder,
                config.templateFile, config.assetsFolder, config.rssTemplate, config.rssItemTemplate)
