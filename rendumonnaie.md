Écrivez un programme qui étant donnés un système de monnaie ~S~ et une valeur cible ~M~ renvoie les nombres de pièces de ~S~ à fournir pour payer ~M~ avec le moins de pièces possible.

## Données d'entrée

La première ligne contient des entiers ~v_i~ (~1 \le v_i \le 100\,000~), les valeurs des pièces de ~S~ séparées par des espaces et données dans l'ordre croissant.
La deuxième ligne contient la somme à atteindre ~M~ (~0 \le M \le 100\,000~).

## Données de sortie

Votre programme doit imprimer une ligne avec les entiers ~x_i~ tels que ~\sum x_i \cdot v_i = M~ (dans le même ordre que les ~v_i~ donnés en entrée).

## Exemple d'entrée

```
1 2 5 10 20 50 100 200 500 1000 2000 5000 10000
23665
```

## Exemple de sortie

```
0 0 1 1 0 1 1 0 1 1 1 0 2
```