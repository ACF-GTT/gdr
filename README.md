# exploitation de données routières

traitement de fichiers de mesure routière

## installation sous windows :

- installer python stable : https://www.python.org/downloads/windows/
- installer vscode : https://code.visualstudio.com/
- installer github desktop si on ne souhaite pas utiliser git en ligne de commande : https://desktop.github.com/download/

```
py -m pip install -r requirements.txt
```

## organisation des répertoires de données

exemple de structure pour le dossier `datas` à implanter dans le répertoire `src`

```
├───datas
|   |───Aigle3D
│   |   │───Table_Indicateurs_Etat_surface_DIRMC.xlsx
│   ├───CD43
│   │   ├───pôle Craponne sur Arzon
│   │   │       RD906 VOIE DROITE PR20 a 23+446.csv
│   │   │       RD906 VOIE GAUCHE PR23+446 a 20.csv
│   │   └───pôle Le Puy en Velay
│   │           RD136 VOIE DROITE PR0 a 4+153.csv
│   │           RD136 VOIE GAUCHE PR4+153 a 0.csv
│   │           RD902 N1 voie droite PR3+072 a 11+186.csv
│   │           RD902 N1 voie gauche PR11+186 a 3+072.csv
│   │           RD902 N2 voie droite PR11+865 a 17+.csv
│   │           RD902 N2 voie gauche PR17+030 a 11+865.csv
│   └───DIRMC
│   |   └───Bessamorel
│   |       │   N88 Bessamorel VL AXE.csv
│   |       │   N88 Bessamorel VL TRACE DROITE.csv
│   |       └───RUGO
│   |           ├───APO0122030190.SES
│   |           │       APO0122030190.EV0
│   |           │       APO0122030190.ID0
│   |           │       APO220105.CFG
│   |           │       APORUG0121030190.ME0
│   |           │       APORUG0121030190.RE0
│   |           └───APO0122030200.SES
│   |                   APO0122030200.EV0
│   |                   APO0122030200.ID0
│   |                   APO220105.CFG
│   |                   APORUG0121030200.ME0
│   |                   APORUG0121030200.RE0
|   └───PR_ABS
|      |───exp_N0122_Vauclair.csv
```

Dans cette structure de données exemple, on a :
- 2 clients : CD43 et DIRMC
- 2 types de mesures différentes: griptester MK2 (format csv) et rugolaser (format APO)
- le fichiers xls des indicateurs de surface Aigle3D
- un fichier [exp_N0122_Vauclair.csv](src/examples_datasets/PR_ABS/exp_N0122_Vauclair.csv) au format csv contenant des données référencées en PR + ABSCISSE

grip et rugo sont des séries monomesure : dans le csv on a un seul type de données, CFL pour le grip et PMP pour le rugolaser par exemple


## utilisation

Pour faire un schéma itinéraire à partir de 2 sessions de mesure :

```
py .\src\generate_si.py --multi=2
```
On est ensuite invité à choisir les fichiers de mesure un par un.

Pour recaler les données une fois qu'on a bien en tête le PR sur lequel on veut effectuer le recalage :

```
py .\src\generate_si.py --multi=2 --pr=20
```

![](images/exemple_si.png)

Les scripts peuvent aussi :
- transcoder les données du griptester au format geojson, pour les utiliser dans un SIG comme QGIS
- recompiler un fichier csv des données indexées au format PR+abscisse, moyennant une identification manuelle dans les geojson des PR depuis un référentiel connu (exemple BPTOPO)
- intégrer les **états de surface AIGLE3D** (IES / IEP / IETP) si le fichier Excel et les paramètres sont renseignés.

La mention de `aigle_3d : 1`  dans [configuration.yml](src/configuration.yml) permet d'activer l'utilisation des données aigle

Il faut aussi s'assurer que [configuration.yml](src/configuration.yml) contient l'emplacement correct du fichier excel, le nom de la route, le département et les sens qu'on veut afficher
```
aigle_3d : 1
aigle_xls : "Aigle3D/Table_Indicateurs_Etat_surface_DIRMC.xlsx"
aigle_route : N0088
aigle_dep : 43
aigle_sens:
  - P
  - M
```

si on veut ne travailler qu'avec des données aigle, sans besoin de synchro avec des appareils monomesure (rugo, grip), on doit préciser `multi=0`

```
py .\src\generate_si.py --multi=0 --bornes 30 37
```
le paramètre bornes sert à préciser les numéros de PR pour délimiter la fenêtre d'affichage

## Synchronisation de données monomesures et de données Aigle3D


Si les données monomesures sont uniquement dans un sens, par exemple le sens moins, le recalage ne peut se faire que si on force le retournement. 

Pour celà on impose `force_reverse: 1` dans [configuration.yml](src/configuration.yml)


## Exemple Intégration grip + A3D

![](images/exemple_grip_aigle.png)


## Autres paramètres

`legend: 0` permet de désactiver les légendes sur les séries monomesures

`mean_step: 100` permet d'afficher les moyennes sur des pas de 100 mètres (200 mètres est la valeur par défaut)

`datas: DIRMC` permet de filtrer les fichiers de mesure qui seront proposées au choix de l'utilisateur.
Celà améliore l'ergonomie lorsqu'on commence à avoir beaucoup de fichiers de mesure.

```
py .\src\generate_si.py --multi=4               
2026-01-16 13:04:03,386 WARNING  pr_plus_abs     __init__ :42       pas de datas PR+ABS pour N0088 ou pas de bdd PR+ABS
[?] fichier de mesure 0:
 > C:\Users\alexandre.cuer\Documents\GitHub\gdr\src\datas\DIRMC\Bessamorel\N88 Bessamorel  VL AXE.csv
   C:\Users\alexandre.cuer\Documents\GitHub\gdr\src\datas\DIRMC\Bessamorel\N88 Bessamorel VL TRACE DROITE.csv
   C:\Users\alexandre.cuer\Documents\GitHub\gdr\src\datas\DIRMC\Bessamorel\RUGO\APO0122030190.SES\APORUG0121030190.RE0
   C:\Users\alexandre.cuer\Documents\GitHub\gdr\src\datas\DIRMC\Bessamorel\RUGO\APO0122030200.SES\APORUG0121030200.RE0
```


## Transparence des bandes de couleur en fond des graphiques griptester

mettre tous ces paramétres à 0 pour revenir au fond blanc
```yaml
background_alpha:
  - poor: 0.1
  - fine: 0.3
  - good: 0.4
  - excellent: 0.4
```
