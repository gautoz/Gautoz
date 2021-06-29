![Gautoz logo](assets/social.jpg)

# Gautoz

Ce dépôt contient les sources et le contenu du site de [Gautoz](https://twitter.com/gautoz). 

## Comment ajouter des pages dans une sous-section (exemple : _matinales_) ?

1. Allez dans le dossier désiré, par exemple `/matinales`
2. Cliquez sur `Add file` puis `Create new file`
3. Nommez le fichier à la date voulue au format `JJ-MM-AAAA` (ex : `13-06-2021`)
4. N'oubliez pas de lui donner l'extension `.md`
5. Complétez le fichier avec le contenu voulu
6. Cliquez sur `Commit new file`

Le nouveau fichier déclenchera la reconstruction du site et sous quelques minutes, la nouvelle page apparaîtra.  
Le flux RSS disponible via l'URL `/feed.xml` sera également mis à jour.

## Comment uploader et ajouter une image dans un page ?
 
1. Allez dans le dossier `/medias` 
2. Utilisez le bouton `Add file` puis `Upload files` pour envoyer votre image (par exemple `image1.jpg`)
2. Dans votre page, utilisez la syntaxe [Markdown](https://daringfireball.net/projects/markdown/syntax) pour l'ajouter : `![image1](image1.jpg)`

Lors de la construction du site l'image sera immédiatement copiée et le lien sera créé.  
Attention à compresser vos image ! Utilisez par exemple [Tiny PNG](https://tinypng.com)

## Comment ajouter une vidéo venant de YouTube, Vimeo, etc. ?

1. Dans votre page, copiez le code HTML donné par YouTube ou Vimeo. Il doit commencer par `<iframe `
2. Vous n'avez rien d'autre à faire : le générateur se chargera de créer la vidéo

## Comment customiser la page d'accueil et les pages intermédiaires ?

- Le contenu de la page d'accueil se trouve dans le fichier `home.md`. Il peut être rédigé comme n'importe quel fichier Markdown.
- Le contenu de la page _matinales_ se trouve dans `matinales/index.md`. Comme la page d'accueil, il peut être rédigé comme n'importe quelle autre page.

La seule différence avec une page classique est que **la page d'accueil et les pages intermédiaires listent automatiquement le contenu des sous-dossiers par ordre antéchronologique**.

La page d'accueil ne liste que les 5 dernières entrées, tandis que la page intermédiaire liste toutes les entrées.

En modifiant le fichier `src/config.py` il est possible de changer :

- Le nom du site via `siteName`
- La meta description du site via `siteMetaDescription`
- Le compte Twitter utilisé lors des embeds Twitter via `twitterName`

## Comment ajouter une nouvelle section ?

Le site est prévu pour accueillir autant de sous-sections que nécessaire. Pour en ajouter une :

1. Ajoutez un dossier à la racine du projet, par exemple `blog/`
2. Dans `/blog`, ajoutez `index.md` afin de créer la page intermédiaire
3. Dans le fichier `src/config.py`, ajoutez le nom de cette nouvelle sous-section dans la variable `contentFolder`. Par exemple `['matinales', 'blog']`

La nouvelle section `blog` est prête, il suffit maintenant d'ajouter des pages. Le contenu de cette nouvelle sous-section sera automatiquement listé sur la page d'accueil.

## Détails techniques

Les fichiers utilisés pour construire le site sont :

- `src/config.py` contient la configuration pour certaines étapes de la construction du site comme les URL, le nom des fichiers, etc.
- `src/build.py` est le fichier créant le site en lui-même
- `src/mistune.py` est le parser Markdown utilisé pour générer le contenu en HTML
- `assets/` contient les images et le fichier de style du site
- `partials/` content le fichier de templating du site
- `docs/` contient la version buildée du site
- `kantan.sh` est un script bash permettant de créer un environnement de développement

Lors du build le script génère les pages HTML à partir des fichiers Markdown, puis génère les pages intermédiaires et la page d'accueil. Enfin, il copie le contenu du dossier assets dans un dossier du même nom.

Il existe deux méthodes pour construire le site :

1. `python3 src/build.py` construit le site avec une URL _relative_, à savoir `/`.
2. `python 3 src/build.py --prod` construit le site avec une URL _absolue_, par exemple `https://gautoz.cool/`.

L'URL absolue est à renseigner dans le fichier `src/config.py`.

## Automatisation de la mise en ligne via la branche `github-pages`

Le site est automatiquement reconstruit à chaque changement via une GitHub Action nommée `build and deploy`. Celle-ci crée un environnement permettant l'execution de `build.py`, puis copie le site généré dans la branche `github-pages`. Celle-ci est ensuite utilisée par GitHub pour afficher le site.
