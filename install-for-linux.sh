#!/bin/bash
source ./progress_bar.sh

chose_to_do () {
    func=$1
    message=$2
    valid=false
    until [ $valid == true ]
    do
        echo $message
        read -p "           [y/n]?" config
        case "$config" in 
            y|Y ) 
                $func
                codeSortie=$?
                if [ $codeSortie -eq 0 ]; then
                    valid=true
                else
                    printf erreur lors de la configuration
                fi
            ;;
            n|N ) 
                valid=true
                codeSortie=1
            ;;
            * ) 
                printf invalid caractère
            ;;
        esac
    done
    return $codeSortie
}
setup_bdd_host(){
    read -p "Qu'elle est l'host : " host
    echo $'[postgresql]\nhost='"$hostBDD" >> config.ini
    return 0
}
setup_bdd_user(){
    read -p "Qu'elle est la database : " database
    read -p "Qu'elle est l'user : " user
    read -p "Qu'elle est le mot de passe : " host
    echo $'database='"$database"$'\nuser='"$user"$'\npassword='"$password" >> config.ini
    return 0
}
setup_server() {
    read -p "Qu'elle est l'host : " host
    read -p "Qu'elle est le port : " port
    valid=false
    until [ $valid == true ]
    do
        read -p "Le server est-il en mode débug [y/n]? " debug
        case "$config" in 
            y|Y ) 
                valid=true
                debug=True
            ;;
            n|N ) 
                valid=true
                debug=False
            ;;
            * ) 
                printf invalid caractère
            ;;
        esac
    done
    echo $'[server]\nhost='"$hostServer"$'\nport='"$portServer"$'\ndebug='"$debug" >> config.ini
    return 0
}
setup_config_ini() {
    # BDD default value
    hostBDD=database-etudiants.iut.univ-paris8.fr
    database=postgres
    user=postgres
    password=postgres
    # Server default value
    hostServer=localhost
    portServer=5050
    debug=True

    # Set up config
    cd src
    draw_progress_bar 46
    # default file
    rm config.ini
    echo $'[postgresql]\nhost='"$hostBDD" > bddHostFileTemp
    echo $'user='"$user"$'\npassword='"$password" > bddUserFileTemp
    echo $'[server]\nhost='"$hostServer"$'\nport='"$portServer"$'\ndebug='"$debug" > serverFileTemp
    draw_progress_bar 50
    # put content in config.ini file
    chose_to_do setup_bdd_host "Voulez-vous modifiez la partie BDD par défaut host=$hostBDD"
    if [ $? -eq 1 ]; then
        cat bddHostFileTemp >> config.ini
    fi
    rm bddHostFileTemp
    draw_progress_bar 60
    chose_to_do setup_bdd_user "Voulez-vous modifiez la partie BDD par défaut database=$database user=$user password=$password"
    if [ $? -eq 1 ]; then
        cat bddUserFileTemp >> config.ini
    fi
    rm bddUserFileTemp
    draw_progress_bar 70
    chose_to_do setup_server "Voulez-vous modifiez la partie server par défaut $hostServer:$portServer debug=$debug"
    if [ $? -eq 1 ]; then
        cat serverFileTemp >> config.ini
    fi
    rm serverFileTemp
    draw_progress_bar 80
    cd ..
    return 0
}
alias_python() {
    alias python=python3
    python --version
    return 0
}
download_setup_and_test() {
    draw_progress_bar 1
    pip install -r requirements.txt
    pip install flask_jwt_extended
    draw_progress_bar 5
    cd app/back
    make setup
    draw_progress_bar 15
    make pytest
    return 0
}

setup_scroll_area
chose_to_do download_setup_and_test "Veux-tu refaire tes requirement, setup and pytest ?"
draw_progress_bar 45
chose_to_do setup_config_ini "Veux-tu changer ton config.ini ?"
draw_progress_bar 81
chose_to_do alias_python "Est-ce que ton alias python ne lance pas la bonne version de python ?"
draw_progress_bar 85
make run
draw_progress_bar 95
destroy_scroll_area

