#include <iostream>

using namespace std;


class PersonneDetails
{
public:
    string nom;
    string prenom;
    int age;
public:
    PersonneDetails(string , string);
    PersonneDetails(string , string, int);
    ~PersonneDetails();
    void anniversaire();
    void setNom(string);
    void setPremom(string);
    void setAge(int);
    string GetNom();
    string GetPrenom();
    int GetAge();
    void afficher();

    
};

PersonneDetails::PersonneDetails(string nm, string prm)
{
    nom= nm;
    prenom=prm;
}
PersonneDetails::PersonneDetails(string nm, string prm, int a){
    nom= nm;
    prenom=prm;
    age = a;
}



void PersonneDetails::anniversaire(){
    age ++;
}    

void PersonneDetails::setNom(string nm){
    nom=nm;
}

void PersonneDetails::setPremom(string prm){
    prenom= prm;
}

void PersonneDetails::setAge(int a){
    age = a;
}

string PersonneDetails:: GetNom(){
    return nom;
}

string PersonneDetails:: GetPrenom(){
    return prenom;
}

int PersonneDetails:: GetAge(){
    return age;
}

void PersonneDetails::afficher(){
   // cout<< 
}


int main(){
   PersonneDetails pD("DOSSOU" ,"Roland");
   cout<< " \n Votre identité :"<< pD.nom<< " "<< pD.prenom ; 

    return 0;
}
