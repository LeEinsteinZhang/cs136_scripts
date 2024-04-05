#!/bin/bash

# Ensure the ~/bin directory exists
mkdir -p ~/bin

# Initial command names
edx="edx"
marm2="marm2"

# Function to create a symbolic link
create_link() {
    local src=$1
    local cmd_name_ref=$2
    local dst="$HOME/bin/${!cmd_name_ref}" # Use indirect reference to get the value of the name variable
    # Check if the destination link already exists
    if [ -e "$dst" ]; then
        # Ask the user whether to replace the existing file
        read -p "$dst already exists. Do you want to update it? (y/n) " choice
        if [[ "$choice" == "Y" || "$choice" == "y" ]]; then
            # Update the link
            ln -sf "$src" "$dst"
            echo "Updated $dst"
        else
            # Ask for renaming
            read -p "[This will use new name for script] Do you want to rename it? (y/n) " rename_choice
            if [[ "$rename_choice" == "Y" || "$rename_choice" == "y" ]]; then
                read -p "Enter new name: " new_name
                local new_dst="$HOME/bin/$new_name"
                ln -s "$src" "$new_dst"
                echo "Created $new_dst"
                eval $cmd_name_ref='$new_name' # Update the command name variable
            else
                echo "No change made to $dst"
            fi
        fi
    else
        # If there is no file at the destination, just create the link
        ln -s "$src" "$dst"
        echo "Created $dst."
    fi
}

# Get the script path
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Main function calls
create_link "$script_dir/edx/edx" "edx"
create_link "$script_dir/marm2/marm2" "marm2"

# Final message
echo "Setup is done. Now you can use edx and marm2 in your terminal."
echo "edx by calling $edx"
echo "marm2 by calling $marm2"
