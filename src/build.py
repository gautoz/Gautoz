# Je met autant des commentaires de forme, de fond ou de bonnes pratiques, prend ce qui te plaît :)

# Plus simple de s'y retrouver si tu tries par ordre alphabétique
import subprocess
import os
import shutil
import glob
import re
import argparse
import sys
from datetime import datetime
# Tu peux utiliser les mots-clefs
#   from . import config
#   from . import mistune
# mais ça nécessite de lancer le script en mode module : `python -m src.build`
mistune = __import__('mistune')
config = __import__('config')


# Checking for dev command
parser = argparse.ArgumentParser()
# La norme c'est de proposer une option longue et une option courte : `'-p', '--prod'`. Tu peux garder `'-prod'` cela
# dit, ça dépanne sur les typos :p
parser.add_argument(
    "-prod", "--prod", help="Prints the supplied argument.", action="store_true")
args = parser.parse_args()

# Declaring build url that will be used in several parts of the app
# La norme en python est de nommer les variables en `snake_case` (ça vaut pour les fonctions et les variables) :
# `build_url`. Pas la peine de définir une valeur par défaut ici puisque tu as un `if-else` basique, ta valeur par
# défaut c'est `absoluteBuildUrl` ici. Aussi, on préfère ne pas comparer les booléens à leur constantes `True` ou
# `False`, tu peux faire `if foo` ou `if not foo` tout court. Perso je trouve ça mieux aussi de privilégier les
# assertions vraies que faux (donc faire un `if args.prod` ici). Enfin, tu peux faire plus court, mais ça c'est question
# de goût :
#   build_url = config.absoluteBuildUrl if args.prod else config.relativeBuildUrl
buildUrl = ""
if args.prod == False:
    buildUrl = config.relativeBuildUrl
else:
    buildUrl = config.absoluteBuildUrl


# Generates html files in the site folder, using the entries and the template.
def generateHtmlPages(siteFolder, entries, template, subPagesList):
    # Ailleurs tu fais 'for entry in entries', d'expérience ça aide vraiment pour s'y retrouver de toujours nommer les
    # variables de la même façon.
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
        # C'est perturbant je trouve de créer du template à la volée en code comme ça, tu pourrais avoir un fichier avec
        # des placeholder à remplacer comme le reste non ?
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
        # Tu peux utiliser un context ici :
        #   slug_file = siteFolder + val['slug']
        #   with open(slug_file, 'w') as fobj:
        #       fobj.write(pageTemplate)
        pageFile = open(siteFolder + val['slug'], "w")
        pageFile.write(pageTemplate)
        pageFile.close()

    print("All pages created!")


# Recovers the html template to be used on the website
# Pas la peine d'une fonction pour ça à mon avis : html = open(templatePath, 'r').read()
def getHtmlTemplate(templatePath):
    template = open(templatePath, 'r')
    html = template.read()
    return html


# Parses markdown and converts it to html
# Le contenu de cette fonction est assez trivial, et tu ne l'utilises qu'une fois, je pense que tu peux t'en penser et
# faire directement :
#   html = mistune.markdown(open(page, 'r').read())
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
    # Tu peux utiliser .strip() : https://docs.python.org/3/library/stdtypes.html#str.strip
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
        # Même remarque qu'ailleurs, tu peux assigner un dict avec des clefs : temp_page = { ... }. D'ailleurs tu copies
        # une majeure partie du dict path, tu peux faire plus court en utilisant dict() :
        #   temp_page = dict(path, title=title, pageContent=pageContent)
        # ou alors :
        #   temp_page = dict(path)
        #   temp_page['title'] = title
        #   temp_page['pageContent'] = pageContent
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
# Cette fonction n'est utilisée qu'une fois, et elle ne fait qu'en appeler une autre, tu peux t'en passer je pense.
def listPages(contentFolder):
    pages = glob.glob(contentFolder + '**/*.md', recursive=True)
    return pages


# Deletes existing production folder and its content then recreates it
# Same for the assets folder
def deleteWebsite(siteFolder, assetsPath):
    print("Deleting site...")
    # Checks if production folder exists
    # Pas la peine de passer par une variable ici, tu peux faire un if directement sur os.path.exists
    siteExists = os.path.exists(siteFolder)
    if siteExists:
        shutil.rmtree(siteFolder)

    print("Creating folders...")
    # La fonction s'appelle deleteWebsite, mais elle ne fait pas que supprimer, ça surprend. Tu peux la renommer
    # empty_build_folder peut-être ? Perso ce genre de manip j'aurais fait ça dans un Makefile, mais ça fait un autre
    # truc à apprendre si tu connais pas, c'est peut-être pas le but !
    os.mkdir(siteFolder)
    # Il existe os.makedirs pour créer directement tous les dossiers parents : os.makedires(siteFolder + assetsPath). Tu
    # peux jeter un oeil aux objets Path : https://docs.python.org/3/glossary.html#term-path-like-object, mais pas
    # nécessaire.
    os.mkdir(siteFolder + assetsPath)


# Copy assets to production folder
# Là aussi j'aurais bien vu ce genre d'opération dans un Makefile
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
    # Tu peux créer un dict avec des clefs déjà :
    #   path_items = {
    #       'slug': path + '.html',
    #       ...
    #   }
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
    # À mon avis il vaut mieux nommer les fichiers au format iso : yyyy-mm-dd. Ça sera trié sur le file system aussi
    # comme ça. T'auras un problème en 2022 en utilisant le format US : 01-01-2022 sera trié avant 01-02-2021
    if pathItems["date"] != "index":
        pathItems["usDate"] = str(
            datetime.strptime(pathItems["date"], '%d-%m-%Y'))
    else:
        # If index page, add a fake date to avoid empty object
        pathItems["usDate"] = str(datetime.strptime("01-01-2000", '%d-%m-%Y'))

    return pathItems


# Generate the list of sub pages for each section
# Tu peux obliger que title soit passé en keyword-argument obligatoirement :
#   def generateSubPages(entries, num, folder, *, title)
# avec cette syntaxe la fonction doit être appelée comme ça :
#   generateSubPages(entries, num, folder, title=False)
# Je trouve ça plus clair quand les paramètres sont des booléens !
def generateSubPages(entries, num, folder, title):

    # Sort entries by date using the usDate format
    # .sort() trie in-place, donc ça modifier le paramètre entries pour l'appelant, c'est surprenant. Tu devrais plutôt
    # le trier avant d'appeler cette fonction, ou alors utiliser sorted() qui crée une copie.
    entries.sort(key=lambda x: x["usDate"], reverse=True)

    # Take n number of entries (5 for the home, all for the sub-section pages)
    # Si tu tries avant d'appeler generateSubPages, tu peux aussi passer seulement le nombre d'éléments que tu veux, et
    # te passer complètement du paramètre num
    selectedEntries = entries[:num]

    # Create the list
    subPageList = "<ul class='listing'>"
    for entry in selectedEntries:
        # 'if title' suffit
        if title == True:
            linkUrl = entry["slug"]
        else:
            linkUrl = entry["file"] + ".html"

        if entry["file"] != "index":
            # Jette un oeil aux f-string pour toutes tes manipulations de string :
            # https://realpython.com/python-f-strings/
            entryString = "<li><a href='" + \
                linkUrl + "'>" + entry["date"] + \
                " : " + entry["title"] + "</a></li>\n"
            subPageList = subPageList + entryString
    subPageList += "</ul>"

    # If a title is necessary, use the folder name
    if title == True:
        # Un exemple de f-string ici : f"<h2>{folder.capitalize()}</h2>", c'est pas mal je trouve !
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
    html = mistune.markdown(homeFile.read()) + "ContentList"

    # Replace template strings with content
    # Je sais que tu aimes bien faire tes propres outils, mais au cas où, perso j'aime bien Jinja pour le templating, ça
    # se prête bien à ce que tu fais en HTML un peu partout dans le code :
    # https://jinja.palletsprojects.com/en/2.11.x/
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


# Les noms des paramètres ne sont pas les mêmes que les noms des variables de configuration c'est perturbant :
# buildFolder devient siteFolder, et assetsFolder devient assetsPath
def generateWebsite(siteFolder, contentFolder, templateFile, assetsPath, rssTemplate, rssItemTemplate):
    print('Welcome to the builder!')
    # Attention tu accèdes à la config globale avec que tu as reçu cette valeur en paramètre, sous le nom siteFolder
    deleteWebsite(config.buildFolder, assetsPath)
    template = getHtmlTemplate(templateFile)
    homePage = createHomePage(template, siteFolder)
    rssEntries = []

    for folder in contentFolder:
        # Pages n'est utilisée que pour être passé à createEntries, elle pourrait plutôt prendre folder en paramètre et
        # lister les pages elle-même
        pages = listPages(folder + "/")
        entries = createEntries(pages)
        subPagesList = generateSubPages(entries, len(entries), folder, False)

        # For each section, create a short listing of sub pages and add it to the home page
        homePageSubList = generateSubPages(entries, 5, folder, True)
        homePage = re.sub('ContentList', homePageSubList +
                          "ContentList", homePage)
        homePage = re.sub('pageDate', "", homePage)

        generateHtmlPages(siteFolder, entries, template, subPagesList)

        # Plus court : rssEntries += entries
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
    # Tu peux utiliser un context ici aussi : with open(...)
    pageFile = open(siteFolder + "index.html", "w")
    pageFile.write(homePage)
    pageFile.close()

    # Create RSS File
    createRssFeed(rssEntries, rssTemplate, rssItemTemplate, siteFolder)


# Triggers the website build
generateWebsite(config.buildFolder, config.contentFolder,
                config.templateFile, config.assetsFolder, config.rssTemplate, config.rssItemTemplate)


# Pour info, il a une convention lorsque l'on crée des scripts comme ça :
#   if __name__ == '__main__':
#       parser = ...
#       generateWebsite(...)
# En gros l'idée c'est de n'avoir aucun code exécuté à l'import du fichier (ici tu as la construction du parser et le
# parsing en lui-même, la construction de buildUrl et l'appel à generateWebsite). Comme ça, dans un éventuel futur
# module ou script tu pourrais importer celui-ci pour réutiliser certaines de ses fonctions. Bon c'est pas vraiment
# pertinent ici à mon avis, mais au moins tu le sais :)

# Jette un oeil à quelques outils comme pylint ou isort par exemple, ça pourrait t'aider à respecter les conventions de
# base (ça va râler sur les variables en camelCase, les imports dans le désordre, les imports inutilisés, etc.)
