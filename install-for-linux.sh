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
setup_bdd(){
    read -p "Qu'elle est l'host : " host
    read -p "Qu'elle est la database : " database
    read -p "Qu'elle est l'user : " user
    read -p "Qu'elle est le mot de passe : " host
    echo $'[postgresql]\nhost='"$hostBDD"$'\ndatabase='"$database"$'\nuser='"$user"$'\npassword='"$password" >> config.ini
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
    hostBDD=localhost
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
    echo $'[postgresql]\nhost='"$hostBDD"$'\ndatabase='"$database"$'\nuser='"$user"$'\npassword='"$password" > bddFileTemp
    echo $'[server]\nhost='"$hostServer"$'\nport='"$portServer"$'\ndebug='"$debug" > serverFileTemp
    draw_progress_bar 50
    # put content in config.ini file
    chose_to_do setup_bdd "Voulez-vous modifiez la partie BDD par défaut host=$hostBDD datbase=$database user=$user password=$password"
    if [ $? -eq 1 ]; then
        cat bddFileTemp > config.ini
    fi
    rm bddFileTemp
    draw_progress_bar 65
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
    
}

setup_scroll_area
cd app/back
draw_progress_bar 1
make setup
draw_progress_bar 15
make pytest
draw_progress_bar 45
chose_to_do setup_config_ini "Do you want to change config.ini"
draw_progress_bar 81
chose_to_do alias_python "Is your alias for python incorect ?"
draw_progress_bar 85
make run
draw_progress_bar 95
destroy_scroll_area

