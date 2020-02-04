L'objectif de TDMOJ est de documenter l'utilisation de la plateforme de compétitions de programmation DMOJ, pour la gestion de TDs en classe.
Ce document reprend et clarifie les instructions données dans la [documentation officielle](https://dmoj.readthedocs.io/en/latest/README/), en documentant également les besoins essentiels en enseignement.

Installation
------------

DMOJ est développé et testé principalement pour Debian Linux, sur les autres systèmes il faudra une machine virtuelle comme [VirtualBox](https://www.virtualbox.org/).

Télécharger l'image d'installation de Debian sur https://www.debian.org/CD/netinst/ et l'installer sur une machine. Les fichiers de configuration suivants présupposent un compte utilisateur nommé `dmoj`. Notez que pour utiliser sudo il _ne faut pas_ créer un compte root.

Pour travailler de l'extérieur de la machine :
```sh
sudo apt install openssh-server
```

Pour travailler dans l'environnement de bureau intégré à la machine, on paramètre le clavier avec :
```sh
sudo apt install keyboard-configuration
sudo dpkg-reconfigure keyboard-configuration
sudo service keyboard-setup restart
```

Pour ajouter le support du copier-coller avec une machine virtuelle, on fait Devices -> Insert Guest Additions CD image... et Devices -> Shared Clipboard -> Bidirectional, puis :
```sh
sudo apt install build-essential module-assistant
sudo m-a prepare
sudo mount /media/cdrom
sudo sh /media/cdrom/VBoxLinuxAdditions.run
sudo reboot now
```

Installation groupée de paquets :
```sh
sudo apt install curl
curl -sL http://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt install git gcc g++ make libxml2-dev libxslt1-dev zlib1g-dev gettext python3-dev python3-pip python3-venv mariadb-server libmariadb-dev-compat supervisor nginx libseccomp-dev nodejs
```

Paramétrage de NodeJS :
```sh
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
cat >.profile <<EOF
if [ -d "$HOME/.npm-global/bin" ] ; then
  PATH="$HOME/.npm-global/bin:$PATH"
fi
EOF
source .profile
npm i -g sass postcss-cli autoprefixer
```

Création de la base de données (donner le mot de passe du compte `dmoj`) :
```sh
sudo mysql
MariaDB [(none)]> CREATE DATABASE dmoj DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
MariaDB [(none)]> GRANT ALL PRIVILEGES ON dmoj.* to 'dmoj'@'localhost' IDENTIFIED BY '<password>';
MariaDB [(none)]> exit
```

Création d'un espace local pour les paquets Python et téléchargement des fichiers du site (ignorer les messages d'erreur `Failed building wheel for ...` qui sont un format de paquet optionnel) :
```sh
python3 -m venv site
cd site
. bin/activate
git clone https://github.com/DMOJ/site.git
cd site
git submodule init
git submodule update
pip install -r requirements.txt
pip install mysqlclient sqlparse uwsgi
```

Copier https://github.com/DMOJ/docs/blob/master/sample_files/local_settings.py dans `dmoj/` en modifiant :
* `DEBUG = False` directement
* le mot de passe de la base de données
* `LANGUAGE_CODE` à `'fr-fr'` et `DEFAULT_USER_TIME_ZONE`
* `STATIC_ROOT` à `'/home/dmoj/site/site/static'`
* décommenter `STATIC_URL` et `STATICFILES_STORAGE`
* modifier le nom du fichier de log de `bridge` dans `LOGGING`

Pour vérifier que tout fonctionne à ce niveau : `python3 manage.py check`

Paramétrage du site Django (lancer manage.py sans argument pour une liste des commandes disponibles) :
```sh
./make_style.sh
python3 manage.py collectstatic
python3 manage.py compilemessages
python3 manage.py compilejsi18n
python3 manage.py migrate
python3 manage.py loaddata navbar
python3 manage.py loaddata language_small
python3 manage.py loaddata demo
python3 manage.py createsuperuser
```

À ce niveau on peut tester le fonctionnement du serveur. Dans la configuration réseau de VirtualBox, NAT -> Avancé -> Redirection de ports -> 8000 vers 8000 (pour le premier test de `runserver`), 8080 vers 80 et 2222 vers 22.
```sh
python3 manage.py runserver 0.0.0.0:8000 # ouvrir http://localhost:8000
python3 manage.py runbridged # ne doit rien renvoyer
```

Copier https://github.com/DMOJ/docs/blob/master/sample_files/uwsgi.ini dans le répertoire courant et modifier :
* `uid = dmoj` et `gid = dmoj`
* `chdir = /home/dmoj/site/site`, `pythonpath` pareil, et `virtualenv = /home/dmoj/site`

Copier https://github.com/DMOJ/docs/blob/master/sample_files/site.conf dans `/etc/supervisor/conf.d/` et modifier :
* `command=/home/dmoj/site/bin/uwsgi --ini uwsgi.ini`
* `directory=/home/dmoj/site/site`
* rediriger les logs vers `/home/dmoj/site.log`
* ajouter `user=dmoj` et `group=dmoj`

Copier https://github.com/DMOJ/docs/blob/master/sample_files/bridged.conf dans `/etc/supervisor/conf.d/` et modifier :
* `command=/home/dmoj/site/bin/python3 manage.py runbridged`
* `directory=/home/dmoj/site/site`
* rediriger les logs vers `/home/dmoj/bridged.log`
* ajouter `user=dmoj` et `group=dmoj`

Copier https://github.com/DMOJ/docs/blob/master/sample_files/nginx.conf dans le répertoire courant et modifier :
* `server_name localhost;` et ajouter `server_name 127.0.0.1;`
* remplacer les deux `<site code path>` par `/home/dmoj/site/site`
* dans `location /static`, retirer `root` et ajouter `alias /home/dmoj/site/site/static`

Installation du juge :
```sh
cd ~
python3 -m venv judge
cd judge
. bin/activate
git clone https://github.com/DMOJ/judge
cd judge
pip3 install -r requirements.txt
python3 setup.py develop
```

Exécuter `dmoj-autoconf` et copier le block `runtime:` dans un nouveau fichier `~/.dmojrc`, puis y ajouter :
```yml
id: Judge
key: "A changer depuis l'interface admin"
problem_storage_root:
  - /home/dmoj/site/site
```

Créer un fichier `/etc/supervisor/conf.d/judge.conf` avec :
```
[program:judge]
command=/home/dmoj/judge/bin/dmoj -p 9999 localhost
user=dmoj
group=dmoj
stdout_logfile=/home/dmoj/judge.log
stderr_logfile=/home/dmoj/judge.log
```

Tester le tout :
```sh
uwsgi uwsgi.ini
sudo supervisorctl update
sudo supervisorctl start all
sudo supervisorctl status
sudo nginx -t
sudo service nginx restart
```

Paramétrage
-----------

Il est temps d'accéder au site à l'adresse http://localhost:8080/

Dans l'interface admin (login/mdp : `admin`/`admin`) on va dans Judges -> Ajouter. Name doit correspondre à l'id dans `.dmojrc`. Ensuite on regénère la clé d'authentification qu'on inscrit aussi dans `.dmojrc`, et on enregistre ce nouveau juge pour le site. Enfin, pour intégrer la nouvelle clé dans le juge on exécute `sudo supervisorctl restart judge`.

Pour vérifier que le site fonctionne, on doit pouvoir résoudre le problème d'exemple A plus B, avec par exemple en Python3 :
```python3
for _ in range(int(input())):
	print(sum(int(i) for i in input().split()))
```

Création d'un nouveau sujet de TD
---------------------------------

Les problèmes des compétitions de programmation ont un format standard à respecter :
* Les énoncés demandent le calcul de données de sortie pour chaque donnée d'entrée.
* Les programmes doivent prendre leurs entrées sur `stdin` et écrire leurs sorties sur `stdout`.
* Les entrées sont dimensionnées en fonction de la complexité de l'algorithme attendu, avec des limites en temps et mémoire d'exécution. Par exemple O(n) = 1_000_000, O(log n) = 100_000, O(n²) = 1_000.
* Des tests d'exemple sont fournis dans l'énoncé, et des tests supplémentaires secrets vérifient les cas critiques.

Un sujet de TD sur DMOJ aura donc la structure suivante :
* Description du contexte et du problème
* Spécification du format des données d'entrée, avec toutes les bornes des valeurs possibles
* Spécification du format des données de sortie
* Exemple de couple entrées/sorties

Pour créer un nouveau sujet de TD avec DMOJ on va dans Problèmes -> Ajouter.
Là, il faut bien faire attention à ce qu'un utilisateur soit mentionné comme _Creator_ (autrement le problème ne pourra plus être édité).
Le texte du problème est au format Markdown, avec l'utilisation de `~` pour activer un mode Math similaire à LaTeX ([plus d'informations](https://dmoj.readthedocs.io/en/latest/site/managing_problems/)).

Une fois le problème enregistré, il s'agit de lui ajouter des tests.
On conseille de faire un test pour chaque cas critique, ainsi que des tests de tailles croissantes pour approcher doucement la complexité visée.
Les données d'entrée et sortie seront stockés dans des fichiers, qu'on nomme par exemple `<problem code>.X.in` et `<problem code>.X.out`, avec X le numéro de chaque test.
On va sur la page du problème tel que vu par les étudiants, puis sur "Edit test data".
Là on envoie les fichiers de tests compressés dans une archive zip, puis on clique sur Submit!
Ensuite on fait correspondre chaque numéro de test avec chaque couple de fichiers.

Les points donnés à chaque test permettent de calculer la proportion de points de points gagnés sur le problème.
Par exemple, pour trois tests à 1 point chacun et un problème qui vaut 30 points, la réussite de chaque test comptera comme 10 points.

Gestion de groupes de TDs
-------------------------

On crée une nouvelle organisation (Admin -> Organisations) par groupe, et on demande aux étudiants de s'y inscrire dans leur page de profil (champ Affiliated organizations). Pour les obliger à renseigner leur groupe, on impose que tous les problèmes de TDs ne soient visible que par les membres des groupes de TDs.

