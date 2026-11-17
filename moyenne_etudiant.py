#note_cc =12
#note_examen =15.5
#progression = note_examen - note_cc
#print("progression:",progression,"points")
note = 8
seuil_validation = 10
#if note <seuil_validation:
 #   print("module non valider")
  #  print("note actuelle:",note)
  # -*- coding: utf-8 -*-
# Exercices : encapsulation, classes abstraites et interfaces en Python
# Chaque exercice est dans sa propre section avec un petit test à la fin.

from abc import ABC, abstractmethod
from typing import Protocol
import json
import os


# =====================================================================
# EXERCICE 1 : classe abstraite Animal
# =====================================================================
print("===== EXERCICE 1 =====")


class Animal(ABC):
    def __init__(self, nom: str):
        self.nom = nom

    @abstractmethod
    def crier(self) -> str:
        """Chaque animal doit définir son propre cri."""

    # méthode concrète : elle est partagée par toutes les classes filles
    def se_presenter(self) -> None:
        print(f"Je m'appelle {self.nom} et je fais : {self.crier()}")


class Chien(Animal):
    def crier(self) -> str:
        return "Wouf !"


class Chat(Animal):
    def crier(self) -> str:
        return "Miaou !"


# On ne peut pas instancier la classe abstraite
try:
    a = Animal("Inconnu")
except TypeError as erreur:
    print("Animal() impossible :", erreur)

for animal in [Chien("Rex"), Chat("Mimi")]:
    animal.se_presenter()  # polymorphisme : même appel, comportement différent


# =====================================================================
# EXERCICE 2 : interface Stockage (mémoire et fichier JSON)
# =====================================================================
print("\n===== EXERCICE 2 =====")


# Interface = ABC pure : que des méthodes abstraites, aucun code, aucun état
class Stockage(ABC):
    @abstractmethod
    def sauvegarder(self, cle: str, valeur) -> None: ...

    @abstractmethod
    def charger(self, cle: str): ...


class StockageMemoire(Stockage):
    def __init__(self):
        self._donnees = {}  # dictionnaire interne (protégé par convention)

    def sauvegarder(self, cle: str, valeur) -> None:
        self._donnees[cle] = valeur

    def charger(self, cle: str):
        # .get() renvoie None si la clé n'existe pas, au lieu de planter
        return self._donnees.get(cle)


class StockageFichier(Stockage):
    def __init__(self, chemin: str):
        self._chemin = chemin

    def _lire_tout(self) -> dict:
        # si le fichier n'existe pas encore, on part d'un dictionnaire vide
        if not os.path.exists(self._chemin):
            return {}
        with open(self._chemin, "r", encoding="utf-8") as f:
            return json.load(f)

    def sauvegarder(self, cle: str, valeur) -> None:
        donnees = self._lire_tout()  # on relit pour ne pas écraser les autres clés
        donnees[cle] = valeur
        with open(self._chemin, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)

    def charger(self, cle: str):
        return self._lire_tout().get(cle)


# Cette fonction marche avec n'importe quel Stockage (c'est l'intérêt du contrat)
def tester_stockage(stockage: Stockage) -> None:
    stockage.sauvegarder("nom", "Amina")
    stockage.sauvegarder("notes", [12, 15.5])
    print(type(stockage).__name__, "->", stockage.charger("nom"),
          stockage.charger("notes"), stockage.charger("absent"))


tester_stockage(StockageMemoire())
tester_stockage(StockageFichier("test_stockage.json"))
os.remove("test_stockage.json")  # on nettoie le fichier de test


# =====================================================================
# EXERCICE 3 : Protocol Comparable
# =====================================================================
print("\n===== EXERCICE 3 =====")


class Comparable(Protocol):
    def comparer(self, autre) -> int:
        """Renvoie un nombre > 0 si self > autre, < 0 si self < autre, 0 si égaux."""
        ...


# Ces deux classes n'héritent pas de Comparable : elles ont juste la bonne méthode
class Produit:
    def __init__(self, nom: str, prix: float):
        self.nom = nom
        self.prix = prix

    def comparer(self, autre) -> int:
        return self.prix - autre.prix


class Etudiant:
    def __init__(self, nom: str, moyenne: float):
        self.nom = nom
        self.moyenne = moyenne

    def comparer(self, autre) -> int:
        return self.moyenne - autre.moyenne


def plus_grand(a: Comparable, b: Comparable) -> Comparable:
    # si comparer() > 0, a est plus grand que b ; sinon on renvoie b
    if a.comparer(b) > 0:
        return a
    return b


p1 = Produit("Clavier", 15000)
p2 = Produit("Souris", 8000)
print("Produit le plus cher :", plus_grand(p1, p2).nom)

e1 = Etudiant("Amina", 14.1)
e2 = Etudiant("Brice", 10.6)
print("Meilleur étudiant :", plus_grand(e1, e2).nom)


# =====================================================================
# EXERCICE 4 : conception d'un système de paiement e-commerce
# =====================================================================
print("\n===== EXERCICE 4 =====")

# Conception proposée :
#  - une INTERFACE Payable : le contrat que tout moyen de paiement doit respecter
#    (payer / rembourser). Le reste du site ne connaît que ce contrat.
#  - une CLASSE ABSTRAITE Paiement qui implémente Payable : elle garde ce que tous
#    les paiements ont en commun (le montant, l'historique, et l'algorithme
#    traiter()), et laisse chaque moyen de paiement définir sa validation.
#  - trois classes concrètes : MobileMoney, CarteBancaire, CashLivraison.
#
# Justification :
#  - L'interface permet au panier / à la caisse de fonctionner avec n'importe quel
#    moyen de paiement, même un futur (PayPal...), sans modifier le code existant.
#  - La classe abstraite évite de dupliquer le code commun (principe DRY) : montant,
#    journal et traiter() sont écrits une seule fois. On a bien une relation
#    "est un" avec du code et un état partagés, donc la classe abstraite se justifie.
#  - Chaque classe fille garde ses détails privés (numéro de téléphone, numéro de
#    carte) grâce à l'encapsulation.


class Payable(ABC):  # interface pure
    @abstractmethod
    def payer(self) -> bool: ...

    @abstractmethod
    def rembourser(self) -> bool: ...


class Paiement(Payable):  # classe abstraite (code commun + état)
    def __init__(self, montant: float):
        if montant <= 0:
            raise ValueError("Le montant doit être positif")
        self._montant = montant  # protégé : utilisable par les classes filles
        self._historique = []

    @abstractmethod
    def valider(self) -> bool:
        """Chaque moyen de paiement a sa propre règle de validation."""

    def payer(self) -> bool:
        # algorithme commun : on valide, puis on enregistre le résultat
        if not self.valider():
            self._historique.append("refusé")
            return False
        self._historique.append("payé")
        return True

    def traiter(self) -> str:
        if self.payer():
            return f"{type(self).__name__} : paiement de {self._montant} FCFA accepté"
        return f"{type(self).__name__} : paiement refusé"


class MobileMoney(Paiement):
    def __init__(self, montant: float, numero: str):
        super().__init__(montant)
        self.__numero = numero  # détail privé

    def valider(self) -> bool:
        # numéro camerounais sur 9 chiffres
        return len(self.__numero) == 9 and self.__numero.isdigit()

    def rembourser(self) -> bool:
        return True


class CarteBancaire(Paiement):
    def __init__(self, montant: float, numero_carte: str):
        super().__init__(montant)
        self.__numero_carte = numero_carte

    def valider(self) -> bool:
        return len(self.__numero_carte) == 16 and self.__numero_carte.isdigit()

    def rembourser(self) -> bool:
        return True


class CashLivraison(Paiement):
    def valider(self) -> bool:
        return True  # rien à vérifier avant la livraison

    def rembourser(self) -> bool:
        return False  # pas de remboursement automatique pour du cash


paiements = [
    MobileMoney(5000, "677123456"),
    CarteBancaire(25000, "1234567890123456"),
    CarteBancaire(25000, "123"),  # carte invalide, sera refusé
    CashLivraison(12000),
]
for paiement in paiements:
    print(paiement.traiter())


# =====================================================================
# EXERCICE 5 : encapsulation avec la classe Etudiant
# =====================================================================
print("\n===== EXERCICE 5 =====")


class EtudiantNotes:
    def __init__(self, nom: str):
        self.nom = nom
        self.__notes = []  # attribut privé (name mangling)

    def ajouter_note(self, note: float) -> None:
        # on refuse toute note en dehors de [0, 20]
        if note < 0 or note > 20:
            raise ValueError("La note doit être comprise entre 0 et 20")
        self.__notes.append(note)

    @property
    def moyenne(self) -> float:
        # propriété en lecture seule : pas de setter défini
        if not self.__notes:
            return 0.0
        return sum(self.__notes) / len(self.__notes)


etu = EtudiantNotes("Amina")
etu.ajouter_note(12)
etu.ajouter_note(16)
print("Moyenne :", etu.moyenne)  # 14.0

# Test 1 : note invalide
try:
    etu.ajouter_note(25)
except ValueError as erreur:
    print("Note refusée :", erreur)

# Test 2 : tenter de modifier la moyenne (propriété sans setter)
try:
    etu.moyenne = 15
except AttributeError as erreur:
    print("Modification impossible :", erreur)

# Test 3 : l'attribut privé n'est pas accessible directement
try:
    print(etu.__notes)
except AttributeError as erreur:
    print("Accès direct impossible :", erreur)
