-- Drop tables if they exist

DROP SCHEMA IF EXISTS EDT cascade;

CREATE SCHEMA EDT;
SET SEARCH_PATH TO EDT;

-- Create tables
CREATE TABLE Groupe(
   idGroupe SERIAL,
<<<<<<< HEAD
   Nom VARCHAR(50) ,
   AnneeScolaire INTEGER,
   Annee VARCHAR(50),
=======
   Nom VARCHAR(50) not null,
>>>>>>> Amélioration du script commands.sql
   idGroupe_parent INTEGER,
   PRIMARY KEY(idGroupe),
   FOREIGN KEY(idGroupe_parent) REFERENCES Groupe(idGroupe) ON DELETE CASCADE
);

CREATE TABLE Salle(
   idSalle SERIAL,
   Nom VARCHAR(50) not null ,
   Capacite INTEGER,
   PRIMARY KEY(idSalle),
   UNIQUE(Nom)
);

CREATE TABLE Equipement(
   idEquipement SERIAL,
   Nom VARCHAR(50) not null ,
   Unique(Nom),
   PRIMARY KEY(idEquipement)
);

CREATE TABLE Semestre(
   idSemestre SERIAL,
   Numero INTEGER ,
   PRIMARY KEY(idSemestre)
);

CREATE TABLE Ressource(
   idRessource SERIAL,
   Titre VARCHAR(50) ,
   Numero VARCHAR(50) ,
   NbrHeureSemestre TIME,
   CodeCouleur VARCHAR(50) ,
   idSemestre INTEGER NOT NULL,
   PRIMARY KEY(idRessource),
   UNIQUE(Numero),
   FOREIGN KEY(idSemestre) REFERENCES Semestre(idSemestre)
);

CREATE TABLE Utilisateur(
   idUtilisateur SERIAL,
   FirstName VARCHAR(50) not null ,
   LastName VARCHAR(50) not null,
   Username VARCHAR(50) not null ,
   Password VARCHAR(50) not null,
   FirstLogin BOOLEAN DEFAULT true,
   PRIMARY KEY(idUtilisateur),
   UNIQUE(Username)
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

CREATE TABLE Cours(
   idCours SERIAL,
   HeureDebut TIME,
   NombreHeure TIME,
   Jour DATE,
   idRessource INTEGER NOT NULL,
   PRIMARY KEY(idCours),
   FOREIGN KEY(idRessource) REFERENCES Ressource(idRessource)
);

CREATE TABLE Manager(
   idManager SERIAL,
   idProf INTEGER NOT NULL,
   PRIMARY KEY(idManager),
   UNIQUE(idProf),
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

