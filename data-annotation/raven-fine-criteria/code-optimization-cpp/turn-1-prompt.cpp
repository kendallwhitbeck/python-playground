// main.cpp

#include <stdio.h>
#include <getopt.h>
#include "SillyQL.hpp"

int main(int argc, char *argv[])
{
// speeds up I/O
std::ios_base::sync_with_stdio(false);

// to read and write bools
std::cin >> std::boolalpha;
std::cout << std::boolalpha;

// create a database
std::unordered_map<std::string, Table> dataBase;
bool quiet = process_command_line(argc, argv);
    
// for commands and comments
std::string command, junk;

// execute atleast once
do
{
    // check for incomplete/incorrect commands
    if (std::cin.fail())
    {
        std::cerr << "Error: Reading from cin has failed" << std::endl;
        exit(1);
    } // if
    
    // prompt
    std::cout << "% ";
    std::cin >> command;
    
    // carry out the command
    switch (command[0])
    {
        case '#':
            // Ignore the comment.
            std::getline(std::cin, junk);
            break;
            
        case 'C':
            // Create the table.
            create(dataBase);
            break;
            
        case 'I':
            // Throw away the 'INTO' string
            std::cin >> junk;
            
            // Insert the table
            insert(dataBase);
            break;
            
        case 'P':
            // Throw away the 'FROM' string
            std::cin >> junk;
            
            // Print the request
            print(dataBase, quiet);
            break;
            
        case 'R':
            // Remove the table
            remove(dataBase);
            break;
            
        case 'D':
            // Throw away the 'FROM' string
            std::cin >> junk;
            
            // Delete requested rows
            delete_from(dataBase);
            break;
            
        case 'G':
            // Throw away the 'FOR' string
            std::cin >> junk;
            
            // Generate an index for a table
            generate_index(dataBase);
            break;
            
        case 'J':                
            // Join two sets
            join(dataBase, quiet);
            break;
            
        case 'Q':
            // Exit the program
            std::cout << "Thanks for being silly!" << std::endl;
            break;
            
        default:
            // Unrecognized command
            std::cout << "Error: unrecognized command" << std::endl;
            std::getline(std::cin, junk);
            break;
    } // switch
    
} while(command[0] != 'Q'); // do-while
} // main()

/// @brief
/// @param argc
/// @param argv
/// @return
bool process_command_line(int argc, char * argv[])
{
// To handle all error output for command line options manually
opterr = false;

int choice;
int option_index = 0;

option long_options[] =
{
    { "help",      no_argument, nullptr, 'h' },
    { "quiet",     no_argument, nullptr, 'q' },
    { nullptr, 0,               nullptr, '\0' }
};


while ((choice = getopt_long(argc, argv, "hq",
                             long_options, &option_index)) != -1)
{
    switch (choice)
    {
            // --help, -h: Print a useful help message and exit,
            // ignores all other options
        case 'h':
            std::cout << "Supported Options: \n";
            std::cout << "--quiet, ";
            exit(0);

        case 'q':
            return true;
            break;

        default:
            std::cerr << "Error: Unknown command line option" << std::endl;
            exit(1);
    } // switch
} // while
return false;
} // process_command_line()