Prénom    Yanis
Nom       Kheffache
Mail      yanis.kheffache@gmail.com

#TD réalisé sur WSL

Mes réponses :

Q1 : Quelle est le nom de l'algorithme de chiffrement ? Est-il robuste et pourquoi ?
  Il s'agit là d'un chiffrement en XOR.
  Ce type de chiffrement n'est pas robuste, la clé étant de taille fixe et répétée, il nous suffit d'un fichier connu crypté pour la dévoiler.

Q2 : Pourquoi ne pas hacher le sel et la clef directement ? Et avec un hmac ?
  Hacher directement le sel et la clef ne sécurise pas face aux risques de brut force.
  Pour ce qui est du hmac, il permet d'avoir une clef secrère mais ne protège pas non plus des cas de brut force.

Q3 : Pourquoi il est préférable de vérifier qu'un fichier token.bin n'est pas déjà présent ?
  Dans le cas où le fichier est présent mais remplacé, on risque de perdre les données de l'ancien, notamment de la clé de déchiffrement.

Q4 : Comment vérifier que la clef la bonne ?
  Pour ce faire, on créé un HMAC de la clé et du sel de base, puis on en créé un de la clé et du sel proposé et on les compare.

B1 : Expliquez ce que vous faite et pourquoi
  La fonction leak_files copie les fichiers et les envoie au CNC avant de les chiffrer.
  Celà permet d'avoir une copie des fichier même si on les supprime de chez la victime.
