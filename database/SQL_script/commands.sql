-- Drop tables if they exist

DROP SCHEMA IF EXISTS EDT cascade;

CREATE SCHEMA EDT;
SET SEARCH_PATH TO EDT;

-- Create tables
CREATE TABLE Groupe(
   idGroupe SERIAL,
   nom VARCHAR(50) not null,
   idGroupeParent INTEGER,
   PRIMARY KEY(idGroupe),
   FOREIGN KEY(idGroupeParent) REFERENCES Groupe(idGroupe) ON DELETE CASCADE
);

CREATE TABLE Salle(
   idSalle SERIAL,
   nom VARCHAR(50) not null ,
   capacite INTEGER,
   PRIMARY KEY(idSalle),
   UNIQUE(nom)
);

CREATE TABLE Equipement(
   idEquipement SERIAL,
   nom VARCHAR(50) not null ,
   Unique(nom),
   PRIMARY KEY(idEquipement)
);

CREATE TABLE Semestre(
   idSemestre SERIAL,
   numero INTEGER ,
   PRIMARY KEY(idSemestre)
);

CREATE TABLE Ressource(
   idRessource SERIAL,
   titre VARCHAR(50) not null ,
   numero VARCHAR(50) not null ,
   nbrHeureSemestre TIME ,
   codeCouleur VARCHAR(50) ,
   idSemestre INTEGER NOT NULL,
   PRIMARY KEY(idRessource),
   UNIQUE(numero),
   FOREIGN KEY(idSemestre) REFERENCES Semestre(idSemestre)
);

CREATE TABLE Utilisateur(
   idUtilisateur SERIAL,
   firstName VARCHAR(50) not null ,
   lastName VARCHAR(50) not null,
   username VARCHAR(50) not null ,
   password VARCHAR(50) not null,
   firstLogin BOOLEAN DEFAULT true,
   PRIMARY KEY(idUtilisateur),
   UNIQUE(username)
);

CREATE TABLE Admin(
   idAdmin SERIAL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idAdmin),
   UNIQUE(idUtilisateur),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Professeur(
   idProf SERIAL,
   initiale VARCHAR(50) ,
   idSalle INTEGER NOT NULL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idProf),
   UNIQUE(idUtilisateur),
   UNIQUE(initiale),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

CREATE TABLE Eleve(
   idEleve SERIAL,
   idGroupe INTEGER NOT NULL,
   idUtilisateur INTEGER NOT NULL,
   PRIMARY KEY(idEleve),
   UNIQUE(idUtilisateur),
   FOREIGN KEY(idGroupe) REFERENCES Groupe(idGroupe),
   FOREIGN KEY(idUtilisateur) REFERENCES Utilisateur(idUtilisateur)
);

Create type TypeCours as ENUM ('Amphi', 'Td', 'Tp', 'Sae');

CREATE TABLE Cours(
   idCours SERIAL,
<<<<<<< HEAD
   HeureDebut TIME,
   NombreHeure TIME,
   Jour DATE,
=======
   heureDebut TIME ,
   nombreHeure TIME,
   jour DATE,
>>>>>>> Uniformalisation des données du script commands.sql
   idRessource INTEGER NOT NULL,
   typeCours TypeCours,
   PRIMARY KEY(idCours),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);




CREATE TABLE Manager(
   idManager SERIAL,
   idProf INTEGER NOT NULL,
   idGroupe INTEGER NOT NULL,
   PRIMARY KEY(idManager),
   UNIQUE(idProf),
   UNIQUE(idGroupe),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf)
);

CREATE TABLE Accuellir(
   idSalle INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idSalle, idCours),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours)
);

CREATE TABLE Equiper(
   idSalle INTEGER,
   idEquipement INTEGER,
   PRIMARY KEY(idSalle, idEquipement),
   FOREIGN KEY(idSalle) REFERENCES Salle(idSalle),
   FOREIGN KEY(idEquipement) REFERENCES Equipement(idEquipement)
);

CREATE TABLE Enseigner(
   idProf INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idProf, idCours),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours) 
);

CREATE TABLE Responsable(
   idProf INTEGER,
   idRessource INTEGER,
   PRIMARY KEY(idProf, idRessource),
   FOREIGN KEY(idProf) REFERENCES Professeur(idProf),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);

CREATE TABLE Etudier(
   idGroupe INTEGER,
   idCours INTEGER,
   PRIMARY KEY(idGroupe, idCours),
   FOREIGN KEY(idGroupe) REFERENCES Groupe(idGroupe),
   FOREIGN KEY(idCours) REFERENCES Cours(idCours) 
);

