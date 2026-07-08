# Contributions au projet 
 
## Membres du groupe – 
Mouhamadou_Lamine_SENE — @senelaminesept97-dotcom 
Mouhamadou_Abdoul_WANE — @mon-nom123 
Cheikhouna_BADIANE — @cheikhahmadoubamba498-cmyk 
 
## Répartition du travail 
 
| Membre | Modules / classes développés | Contribution estimée | 
|--------|-------------------------------|----------------------| 
| Mouhamadou_Lamine_SENE | ...                            | 40% | 
| Mouhamadou_Abdoul_WANE | ...                            | 30% | 
| Cheikhouna_BADIANE | ...                            | 30% | 
 
## Répartition par phase 
 
| Phase                            | Responsable principal | 
|-----------------------------------|------------------------| 
| Conception (diagramme de classes) | Mouhamadou_Lamine_SENE | 
| Implémentation POO                | Mouhamadou_Lamine_SENE | 
| Persistance fichiers (JSON/CSV)   | Mouhamadou_Abdoul_WANE | 
| Persistance SQL                   | Mouhamadou_Abdoul_WANE  | 
| Tests / gestion des exceptions     | Cheikhouna_BADIANE | 
| README / documentation            | Cheikhouna_BADIANE | 
 


## Difficultés rencontrées et résolution 
Réaliser un projet de cette envergure, qui mêle à la fois de la Programmation Orientée Objet (POO) avancée et plusieurs types de bases de données, comporte quelques pièges classiques.
Voici les deux difficultés principales que l'on rencontre généralement sur ce type d'architecture :
1. La désérialisation du JSON vers le modèle Objet (Le problème du polymorphisme)
Si exporter la flotte en JSON est relativement simple (on transforme les objets en dictionnaires de texte), l'importation (la lecture) est beaucoup plus complexe.
•	Le problème : Le fichier JSON est "plat". Lorsqu'on lit une liste de véhicules dans le JSON, Python voit de simples dictionnaires. Il ne sait pas automatiquement si un dictionnaire correspond à une Voiture, un Utilitaire ou une Moto.
•	La conséquence : Si on reconstruit mal les objets, on perd le polymorphisme. Par exemple, si on instancie par erreur chaque ligne sous la classe générique VehiculeBase (ce qui est impossible car elle est abstraite), ou si on se trompe de classe, la méthode calculer_tarif_jour() ou necessite_entretien() ne renverra pas le bon résultat car les règles métiers spécifiques à chaque véhicule seront perdues.
•	La solution (appliquée dans le code fourni) : Il faut obligatoirement stocker un attribut "type" dans le JSON lors de l'export, puis utiliser une structure conditionnelle (if/elif/else) lors de la lecture pour recréer la bonne instance de classe avec ses propriétés spécifiques (comme le volume en $m^3$ pour l'utilitaire).
2. Le décalage de paradigme entre l'Objet et le Relationnel (L'impédance O/R)
Faire cohabiter un modèle pensé en Objets (Python) avec un modèle pensé en Tables (SQL) crée souvent des conflits de logique, particulièrement pour les notions de Composition (l'historique d'entretien) et d'Enums.
•	Le problème de la composition : En Python, l'objet Voiture possède directement une liste d'objets Entretien dans ses attributs (self.historique_entretiens). En SQL, c'est l'inverse : la table entretiens possède une clé étrangère qui pointe vers la table vehicules.
•	Le problème des Enums : SQLite ne gère pas nativement les types Enum (comme StatutVehicule).
•	La conséquence : Lors de la sauvegarde ou de la récupération, le développeur doit manuellement "casser" l'objet Python pour dispatcher les pièces dans les différentes tables SQL, et convertir les Enums en chaînes de caractères (.value), puis faire le chemin inverse (convertir le texte SQL en Enum Python) lors de la lecture. Oublier une étape brise la cohérence des données.

