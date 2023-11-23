source ./progress_bar.sh
setup_scroll_area

draw_progress_bar 45
Valid=false
until ["$Valid"=true]
do
    echo '      Do you want to change config.ini'
    read -p "           [y/n]?" config
    case "$config" in 
        y|Y ) 
            setup_config
            Valid=true
        ;;
        n|N ) 
            Valid=true
            echo "erreur de caractère"
        ;;
        * ) echo "invalid";;
    esac
done

draw_progress_bar 95
destroy_scroll_area




setup_config() {
    echo "yay"
}

