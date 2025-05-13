// SillyQL.hpp

#ifndef SillyQL_hpp
#define SillyQL_hpp

#include <stdio.h>
#include <vector>
#include <unordered_map>
#include <map>
#include <iostream>
#include "TableEntry.h"

enum class CommandType
{
CREATE,
INSERT,
PRINT,
REMOVE,
DELETE,
GENERATE,
JOIN
};

class Table
{

public:
// ctor
Table(
const std::string &tn,
size_t numCols) : idxStatus{None}, tableName{tn}, idxCol{static_cast<size_t>(-1)}, rows{0}
{
// Set the number of columns.
colNamesAndIdx.reserve(numCols);
columnTypes.reserve(numCols);
} // ctor

// Overloaded print helper to display single entries
void entry_printer(size_t row, std::string colName);


// Overloaded print helper to display single entries
void entry_printer(
    const std::vector<TableEntry> &row,
    std::string colName
);


// Accepts one of three functors (=, <, >).
template <typename Pred>
void print_if(
    const std::vector<std::string> &colsToPrint,
    Pred &condition,
    bool &quiet
); // print_if()


// Accepts one of three functors (=, <, >)
template <typename Pred>
void delete_if(Pred &condition);


void print_all(
    const std::vector<std::string> &colsToPrint,
    bool &quiet
); // print_all()


// Performs a full scan.
void full_scan(
    char &operation, TableEntry &te,
    std::string &colToCheck, bool deleteCommand,
    bool &quiet,
    const std::vector<std::string> &colsToPrint
); // full_scan()


void BST_scan(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, bool deleteCommand
); // BST_scan()


void HASH_scan(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, bool deleteCommand
); // HASH_scan()


void index_lookup(
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, bool deleteCommand
); // index_lookup()


void three_way(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, std::string &colToCheck,
    bool &quiet, bool deleteCommand
); // three_way()


template <typename Func>
void four_way(EntryType type, Func &&callback);


// A helper that abstracts the create index functionality.
template <typename IndexContainer>
void populate_index(IndexContainer &index);

void create_hash_index();

void update_index();

void regenerate_hash_index();

void regenerate_BST_index();

void create_BST_index();

// Helper to print rows
void print_rows(
    const std::vector<size_t> &rows,
    const std::vector<std::string> &colsToPrint,
    bool quiet
); // print_rows()


// Helper to delete rows
void delete_rows(std::vector<size_t> &rows);

// Handles column initialization
void initialize_columns(size_t numCols);

EntryType get_column_type(const std::string &colName) const;

EntryType get_column_type(size_t idx) const;

size_t get_column_idx(const std::string &colName) const;

// Sets the indexed column's idx.
bool set_index_idx(const std::string &indexColName);

// Returns the indexed column's idx.
size_t get_index_idx() { return idxCol; }



/// NOTE: SHOULD I MAKE THE FOLLOWING PRIVATE????

// The type of index generated.
enum indexStatus : uint8_t
{
    None,
    Hash,
    BST
} idxStatus;

std::string tableName;

// The column I have an index on,
// and the number of table rows.
size_t idxCol, rows;

bool quietMode;

// Hash map of column names to their respective
// idx within the table, i.e., header position.
std::unordered_map<std::string, size_t> colNamesAndIdx;

// Container of the column data types in insertion order.
std::vector<EntryType> columnTypes;

// A single 2x2 table.
std::vector<std::vector<TableEntry>> data;

// Hash map of an arbitrary, user-selected database table
// column, which maps the column's entries to their rows.
std::unordered_map<TableEntry, std::vector<size_t>> idxHash;

// Binary Search Tree of an arbitrary, user-selected database
// table column, which maps the column's entries to their rows.
std::map<TableEntry, std::vector<size_t>> idxBST;

// In SillyQL.hpp, add this declaration to the Table class if not already present:
private:
    // Add temporary hash index for join operations
    std::unordered_map<TableEntry, std::vector<size_t>> tempIdxHash;


}; // Table

class MessageHandler
{
public:
// Error types as specified
enum class ErrorType
{
TABLE_EXISTS, // Error 1
TABLE_NOT_FOUND, // Error 2
COLUMN_NOT_FOUND, // Error 3
UNRECOGNIZED_CMD // Error 4
};

static void report_error(
    CommandType command,
    ErrorType error,
    const std::string &tableName = "",
    const std::string &colName = "")
{
    std::string commandStr = command_to_string(command);
    std::string message;

    // Based on the error type, set the message.
    switch (error)
    {
        case ErrorType::TABLE_EXISTS:
            message = "Cannot create already existing table " + tableName;
            break;
        case ErrorType::TABLE_NOT_FOUND:
            message = tableName + " does not name a table in the database";
            break;
        case ErrorType::COLUMN_NOT_FOUND:
            message = colName + " does not name a column in " + tableName;
            break;
        case ErrorType::UNRECOGNIZED_CMD:
            message = "unrecognized command";
            break;
    }

    std::cout << "Error during " << commandStr << ": " << message << std::endl;

    // If the error is recognized, read-in the input rows:
    if (error != ErrorType::UNRECOGNIZED_CMD)
    {
        std::string junk;

        // For INSERT commands, read-in multiple input rows:
        if ((error == ErrorType::TABLE_NOT_FOUND) &&
            (command == CommandType::INSERT))
        {
            size_t expectedNumRows = 0;
            std::cin >> expectedNumRows;
            std::getline(std::cin, junk);

            for (size_t i = 0; i < expectedNumRows; i++)
                std::getline(std::cin, junk);
        }
        // O/W, read-in a single input row:
        else
        {
            std::getline(std::cin, junk);
        }
    }
} // report_error()



// Success message templates
static void report_success(
    CommandType command,
    size_t count,
    const std::string &metaData1,
    const std::string &metaData2 = "")
{
    static const std::map<CommandType, std::string> successTemplates =
    {
        {CommandType::CREATE, "New table %s with column(s) %s created"},
        {CommandType::INSERT, "Added %zu rows to %s from position %zu to %zu"},
        {CommandType::PRINT, "Printed %zu matching rows from %s"},
        {CommandType::REMOVE, "Table %s deleted"},
        {CommandType::DELETE, "Deleted %zu rows from %s"},
        {CommandType::GENERATE, "Created %s index for table %s on column %s"},
        {CommandType::JOIN, "Printed %zu rows from joining %s to %s"}
    };


    std::string message = successTemplates.at(command);
    switch (command)
    {
        case CommandType::INSERT:
            printf((message + "\n").c_str(), count, metaData1.c_str(), count, std::stoul(metaData2));
            break;

        case CommandType::GENERATE:
            printf((message + "\n").c_str(), metaData1.c_str(), metaData2.c_str(), count ? "hash" : "bst");
            break;

        default:
            if (metaData2.empty())
                printf((message + "\n").c_str(), count, metaData1.c_str());
            else
                printf((message + "\n").c_str(), count, metaData1.c_str(), metaData2.c_str());
            break;
    } // switch
} // report_success()



// Prints the column headers (e.g., column names).
static void print_col_headers(
    const std::vector<std::string> &colsToPrint,
    bool quiet)
{
    if (!quiet)
    {
        for (std::string colName : colsToPrint)
            std::cout << colName << " ";
        std::cout << std::endl;
    }
} // print_col_headers()
private:
static std::string command_to_string(CommandType command)
{
switch (command)
{
case CommandType::CREATE:
return "CREATE";
case CommandType::INSERT:
return "INSERT";
case CommandType::PRINT:
return "PRINT";
case CommandType::REMOVE:
return "REMOVE";
case CommandType::DELETE:
return "DELETE";
case CommandType::GENERATE:
return "GENERATE";
case CommandType::JOIN:
return "JOIN";
}
return "";
} // command_to_string()

}; // MessageHandler

///NOTE: SHOULD THESE GENERAL DATABASE FUNCTIONS BE MEMBER FUNCTIONS OF THE TABLE CLASS? THEY ALL USE THE TABLE CLASS AND HAVE IDENTICAL SIGNATURES.

// Alias to use the status within non-member functions.
using idxStat = Table::indexStatus;
using errType = MessageHandler::ErrorType;

bool process_command_line(int argc, char *argv[]);

void create(
std::unordered_map<std::string, Table> &dataBase
);

void insert(
std::unordered_map<std::string, Table> &dataBase
);

void print(
std::unordered_map<std::string, Table> &dataBase,
bool &quiet
);

void remove(
std::unordered_map<std::string, Table> &dataBase
);

void delete_from(
std::unordered_map<std::string, Table> &dataBase
);

void generate_index(
std::unordered_map<std::string, Table> &dataBase
);

void join(
std::unordered_map<std::string, Table> &dataBase,
bool &quiet
);

bool validate_table_name(
const std::unordered_map<std::string, Table> &dataBase,
const std::string &tableName,
CommandType command
);

bool validate_column_name(
Table &table,
const std::string &colName,
const std::string &tableName,
CommandType command
);

/// @brief Functor for equality checks.
class EQfunctor
{
public:
EQfunctor(TableEntry &valueIn, size_t &idxIn) : value{valueIn}, colIndex{idxIn}
{ }

bool operator()(const std::vector<TableEntry> &row)
{
    return row[colIndex] == value;
}
private:
TableEntry value;
size_t colIndex;
}; // EQfunctor

/// @brief Functor for less than checks.
class Lessfunctor
{
public:
Lessfunctor(TableEntry &valueIn, size_t &idxIn) : value{valueIn}, colIndex{idxIn}
{ }

// For full scans
bool operator()(const std::vector<TableEntry> &row)
{
    return row[colIndex] < value;
}

// For index scans
bool operator()(const TableEntry &indexEntry)
{
    return indexEntry < value;
}
private:
TableEntry value;
size_t colIndex;
}; // Lessfunctor

/// @brief Functor for greater than checks.
class Greaterfunctor
{
public:
Greaterfunctor(TableEntry &valueIn, size_t &idxIn) : value{valueIn}, colIndex{idxIn}
{ }

// For full scans
bool operator()(const std::vector<TableEntry> &row)
{
    return row[colIndex] > value;
}

// For index scans
bool operator()(const TableEntry &indexEntry)
{
    return indexEntry > value;
}
private:
TableEntry value;
size_t colIndex;
}; // Greaterfunctor

#endif /* SillyQL_hpp */

/// NOTE: In the comments, I denote the regular row and column indices w/ idx, and the BST/Hash as the full word "index".

// SillyQL.cpp

#include <stdio.h>
#include <map>
#include <unordered_map>
#include <algorithm>
#include "SillyQL.hpp"
#include "TableEntry.h"

using namespace std;

/// @brief After the user's request to create an index is executed, we store the idx within the table corresponding to the column we indexed.
/// @param indexColName
/// @return True upon successful index creation, and false o/w.
bool Table::set_index_idx(const string &indexColName)
{
// Look for and validate the column's existence.
if (validate_column_name(
*this,
indexColName,
tableName,
CommandType::GENERATE))
{
// Store the indexed column's table idx.
idxCol = colNamesAndIdx[indexColName];
return true;
}

return false;
} // set_index_idx()

/// @brief Syntax: CREATE <tablename> <N> <coltype1> <coltype2> ... <coltypeN> <colname1> <colname2> ... <colnameN>
/// @param dataBase
void create(unordered_map<string, Table> &dataBase)
{
// Read in table name and the number of columns.
string tableName;
cin >> tableName;
size_t numCols;
cin >> numCols;

if (!validate_table_name(
    dataBase,
    tableName,
    CommandType::CREATE)
) { return; }

Table newTable(tableName, numCols);

// Read in the table's columns and init them.
newTable.initialize_columns(numCols);

// Insert the table into the database via move.
dataBase.emplace(tableName, std::move(newTable));
} // create()

/// @brief Input is as follows: <colType0>, ..., <colTypeN>, <colName0>, ..., <colNameN>. This is why it takes two seperate for-loops.
/// @param numCols
void Table::initialize_columns(size_t numCols)
{
string typeStr, colName;

// Read in column types.
for (size_t i = 0; i < numCols; i++)
{
    cin >> typeStr;
    switch (typeStr[0])
    {
    case 's':
        columnTypes.push_back(EntryType::String);
        break;
    case 'd':
        columnTypes.push_back(EntryType::Double);
        break;
    case 'i':
        columnTypes.push_back(EntryType::Int);
        break;
    case 'b':
        columnTypes.push_back(EntryType::Bool);
        break;
    default:
        throw runtime_error("Unknown column type: " + typeStr);
    }
}

cout << "New table " << tableName << " with column(s) ";

// Read in column names and create the mapping.
for (size_t i = 0; i < numCols; i++)
{
    cin >> colName;
    cout << colName << " ";

    // Create an entry in tableColumns with index = i
    // and the type from the temporary vector.
    colNamesAndIdx.emplace(colName, i);
}

cout << "created" << endl;
} // initialize_columns()

/// @brief A helper to fetch column type from name.
/// @param colName
/// @return Data type.
EntryType Table::get_column_type(const string &colName) const
{
if (colNamesAndIdx.contains(colName))
return columnTypes[colNamesAndIdx.at(colName)];
throw runtime_error("Column type not found");
} // get_column_type(string)

/// @brief A helper to fetch column type from index.
/// @param idx
/// @return Data type.
EntryType Table::get_column_type(size_t idx) const
{
if (idx < columnTypes.size())
return columnTypes[idx];
throw runtime_error("Column type not found");
} // get_column_type(size_t)

/// @brief A helper to fetch column name from index.
/// @param idx
/// @return Name string.
size_t Table::get_column_idx(const string &colName) const
{
if (colNamesAndIdx.contains(colName))
return colNamesAndIdx.at(colName);
throw runtime_error("Column index not found");
} // get_column_idx()

/// @brief Syntax: INSERT INTO <tablename> <N> ROWS
/// <value11> <value12> ... <value1M>
/// <valueN1> <valueN2> ... <valueNM>
/// @param dataBase
void insert(unordered_map<string, Table> &dataBase)
{
// Read the <tablename>.
string tn;
cin >> tn;

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::INSERT)
) { return; }

// Extract the current data table.
Table &table = dataBase.at(tn);
size_t tableSize = table.columnTypes.size();

// Read in the number of rows to be inserted.
size_t newNumRows = 0,
       oldNumRows = table.rows;
cin >> newNumRows; // <N>

// Throw away the 'ROWS' string.
string junk;
cin >> junk;

// Update the overall rows count.
table.rows += newNumRows;

// Resize the actual table, i.e.,
// the underlying 2d vec (data).
table.data.resize(table.rows);

// Loop from old numRows to newNumRows, which appends.
for (size_t i = oldNumRows; i < table.rows; i++)
{
    // Since I extract a reference to the new row here,
    // I dont have to emplace_back nor push_back to
    // add the row. I just modify it directly.
    vector<TableEntry> &row = table.data[i];

    // Reserve room in the new row container to match
    // the data table's inner dimension.
    row.reserve(tableSize);

    // Traverse the column types to get the appropriate variable
    // type for the read-in data: {string, int, double, bool}.
    for (size_t j = 0; j < tableSize; j++)
    {
        // Each column is one of the entry types.
        // The col types dictate what we will read in.
        // 4way: string, int, double, bool
        table.four_way(
            table.get_column_type(j),
            // Callback
            [&row](TableEntry &te)
            { row.push_back(te); }
        );
    } // for k
} // for i

cout << "Added " << newNumRows << " rows to " << tn
     << " from position " << oldNumRows << " to "
     << (table.rows - 1)
     << endl;

// Index maintenence.
table.update_index();
} // insert()

/// @brief Index scans delete helper.
/// @param rows
void Table::delete_rows(vector<size_t> &rows)
{
// Sort in descending order to delete larger indices first.
sort(rows.begin(), rows.end(), greater<>());

// Upon deletion, rows w/ smaller indices dont get shifted
// therefore, they keep the same position and rowsVec stays valid.
for (size_t row : rows)
    data.erase(data.begin() + static_cast<ptrdiff_t>(row));

// Update the member variable.
this->rows = data.size();
} // delete_rows()

/// @brief
/// @param dataBase
/// @param tableName
/// @param command
/// @return
bool validate_table_name(
const unordered_map<string, Table> &dataBase,
const string &tableName,
CommandType command)
{
switch (command)
{
case CommandType::CREATE:
{
if (dataBase.contains(tableName))
{
MessageHandler::report_error(
command,
errType::TABLE_EXISTS,
tableName
);

            return false;
        }

        break;
    }

    default:
    {
        if (!dataBase.contains(tableName))
        {
            MessageHandler::report_error(
                command,
                errType::TABLE_NOT_FOUND,
                tableName
            );

            return false;
        }

        break;
    }
}
return true;
} // validate_table_name()

/// @brief
/// @param table
/// @param colName
/// @param tableName
/// @param command
/// @return
bool validate_column_name(
Table &table,
const string &colName,
const string &tableName,
CommandType command)
{
if (!table.colNamesAndIdx.contains(colName))
{
MessageHandler::report_error(
command,
errType::COLUMN_NOT_FOUND,
tableName, colName
);

    return false;
}

return true;
} // validate_column_name()

/// @brief PRINT FROM <tablename> <N> <print_colname1> <print_colname2> ... <print_colnameN> [ WHERE <colname> <OP> <value> || ALL ]
/// @param dataBase
/// @param quiet
void print(unordered_map<string, Table> &dataBase, bool &quiet)
{
// Read the <tablename>.
string tn;
cin >> tn;

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::PRINT)
) { return; }

// Extract the current data table.
Table &table = dataBase.at(tn);

// Read in the number of columns to be printed.
size_t numPrintCols = 0; // <N>
cin >> numPrintCols;

// A container for the N column names to be printed.
vector<string> colsToPrint;
colsToPrint.reserve(numPrintCols);

// Validate the requested columns.
for (size_t i = 0; i < numPrintCols; i++)
{
    // Read-in <print_colnameN>
    string colName;
    cin >> colName;

    // Since the columns might be in a
    // different order, we simply store them.
    if (!validate_column_name(
        table,
        colName,
        tn,
        CommandType::PRINT)
    ) { return; }

    colsToPrint.push_back(colName);
} // for i

// Throw away the 'WHERE' string.
string junk;
cin >> junk;

// "junk" represents [ WHERE <colname> <OP> <value> || ALL ]
if (junk[0] == 'A')
{
    // Print all rows
    table.print_all(colsToPrint, quiet);
}
else // junk[0] == "W"
{
    // Read the condition col name <colname>.
    string conditionCol;
    cin >> conditionCol;

    // Validate <colname> exists.
    if (!validate_column_name(
        table,
        conditionCol,
        tn,
        CommandType::PRINT)
    ) { return; }

    // Print the column headers (names)
    MessageHandler::print_col_headers(colsToPrint, quiet);

    // Read the condition operator {>, <, =}:
    char operation; // <OP>
    cin >> operation;

    // 4way: string, int, double, bool
    table.four_way(
        table.get_column_type(conditionCol),
        [&](TableEntry &te)
        {
            table.three_way(
                operation,
                colsToPrint,
                te,
                conditionCol, 
                quiet,
                false // PRINT command
            );
        });
} // if-else
} // print()

/// @brief Come here for equality conditions. Since the three_way confirms the appropriate index exists, we can use .contains and not worry about errors.
/// @param colsToPrint
/// @param te
/// @param colToCheck
/// @param quiet
void Table::index_lookup(
const vector<string> &colsToPrint,
TableEntry &te, bool &quiet, bool deleteCommand)
{
size_t numProcessedRows = 0;

switch (idxStatus)
{
    case Hash:
    {
        if (idxHash.contains(te))
        {
            auto &rowsVector = idxHash.at(te);
            numProcessedRows = rowsVector.size();

            if (deleteCommand)
                delete_rows(rowsVector);
            else // printCommand
                print_rows(rowsVector, colsToPrint, quiet);
        }

        break;
    }

    case BST:
    {
        if (idxBST.contains(te))
        {
            auto &rowsVector = idxBST.at(te);
            numProcessedRows = rowsVector.size();

            if (deleteCommand)
                delete_rows(rowsVector);
            else // printCommand
                print_rows(rowsVector, colsToPrint, quiet);
        }

        break;
    }

    default:
        break;
}

if (deleteCommand)
{
    cout << "Deleted " << numProcessedRows
         << " rows from " << tableName
         << endl;
}
else
{
    cout << "Printed " << numProcessedRows
         << " matching rows from " << tableName
         << endl;
}
} // index_lookup()

/// @brief Delegates work to the appropriate Data Structure: bst, hash, or none
/// @param operation
/// @param colsToPrint
/// @param te
/// @param colToCheck
/// @param quiet
/// @param deleteCommand
void Table::three_way(
char &operation,
const vector<string> &colsToPrint,
TableEntry &te, string &colToCheck,
bool &quiet, bool deleteCommand)
{
// If an index is available on the correct column, then use it.
bool indexExists =
(get_index_idx() == get_column_idx(colToCheck));

// Index status can be BST, Hash, or None.
switch (idxStatus)
{
    case BST:
    {
        if (indexExists)
        {
            BST_scan(
                operation,
                colsToPrint,
                te,
                quiet,
                deleteCommand
            );

            break;
        }
    } // BST

    case Hash:
    {
        if (indexExists)
        {
            HASH_scan(
                operation,
                colsToPrint,
                te,
                quiet,
                deleteCommand
            );

            break;
        }
    } // Hash

    // If the index is on the wrong column, then
    // fall through to this case: Full scan
    case None:
    default:
        full_scan(
            operation,
            te,
            colToCheck,
            deleteCommand,
            quiet,
            colsToPrint
        );

        break;
} // switch
} // three_way()

/// @brief 4way: string, int, double, bool
/// @tparam Func
/// @param type
/// @param callback
template <typename Func>
void Table::four_way(EntryType type, Func &&callback)
{
switch (type)
{
case EntryType::String:
{
string value;
cin >> value;
TableEntry te{value};
callback(te);
break;
}
case EntryType::Double:
{
double value;
cin >> value;
TableEntry te{value};
callback(te);
break;
}
case EntryType::Int:
{
int value;
cin >> value;
TableEntry te{value};
callback(te);
break;
}
case EntryType::Bool:
{
bool value;
cin >> value;
TableEntry te{value};
callback(te);
break;
}
default:
break;
}
} // four_way()

/// NOTE: SINCE BSTSCAN IS MERELY A COLLECTION OF INDEX_LOOKUPS, WE CAN RECYCLE CODE!
/// @brief
/// @param operation
/// @param colsToPrint
/// @param te
/// @param quiet
/// @param deleteCommand
void Table::BST_scan(
char &operation,
const vector<string> &colsToPrint,
TableEntry &te, bool &quiet, bool deleteCommand)
{
size_t numProcessedRows = 0;
vector<size_t> rowsToProcess;

switch (operation)
{
    case '=':
    {
        index_lookup(colsToPrint, te, quiet, deleteCommand);
        return;
    }
    case '>':
    {
        // Traverse BST
        for (auto start = idxBST.upper_bound(te);
            start != idxBST.end(); start++)
        {
            auto rowsVector = start->second;
            numProcessedRows += rowsVector.size();

            // Store the rows we need to process.
            rowsToProcess.insert(
                rowsToProcess.end(),
                rowsVector.begin(),
                rowsVector.end()
            );
        } // for upperBound in bst

        break;
    }

    case '<':
    {
        // Loop the lower range of BST: the smallest to the max < te
        for (auto start = idxBST.begin();
            start != idxBST.lower_bound(te); start++)
        {
            auto rowsVector = start->second;
            numProcessedRows += rowsVector.size();

            // Store the rows we need to process.
            rowsToProcess.insert(
                rowsToProcess.end(),
                rowsVector.begin(),
                rowsVector.end()
            );
        } // for start in bst

        break;
    }

    default:
        break;
} // switch

if (deleteCommand)
{
    delete_rows(rowsToProcess);

    cout << "Deleted " << numProcessedRows
         << " rows from " << tableName
         << endl;
}
else
{
    print_rows(rowsToProcess, colsToPrint, quiet);

    cout << "Printed " << numProcessedRows
         << " matching rows from " << tableName
         << endl;
}
} // BST_scan()

/// @brief If no index exists or there is a hash index on the conditional column, the results should be printed in order of insertion into the table.
/// @param operation
/// @param colsToPrint
/// @param te
/// @param quiet
/// @param deleteCommand
void Table::HASH_scan(
char &operation,
const vector<string> &colsToPrint,
TableEntry &te, bool &quiet, bool deleteCommand)
{
size_t numProcessedRows = 0;
vector<size_t> rowsToProcess;

switch (operation)
{
    case '=':
    {
        index_lookup(colsToPrint, te, quiet, deleteCommand);
        return;
    }

    case '>':
    {
        // Similar to full scan, but scan the index, not the table.
        Greaterfunctor gr(te, idxCol);
        for (auto &[key, rowIndices] : idxHash)
        {
            if (gr(key))
            {
                numProcessedRows += rowIndices.size();

                // Store the rows we need to process.
                rowsToProcess.insert(
                    rowsToProcess.end(),
                    rowIndices.begin(),
                    rowIndices.end());
            }
        }

        break;
    }

    case '<':
    {
        Lessfunctor ls(te, idxCol);
        for (auto &[key, rowIndices] : idxHash)
        {
            if (ls(key))
            {
                numProcessedRows += rowIndices.size();

                // Store the rows we need to process.
                rowsToProcess.insert(
                    rowsToProcess.end(),
                    rowIndices.begin(),
                    rowIndices.end());
            }
        }

        break;
    }

    default:
        break;
} // switch

if (deleteCommand)
{
    delete_rows(rowsToProcess);

    cout << "Deleted " << numProcessedRows
         << " rows from " << tableName 
         << endl;
}
else
{
    // Stable sort puts the rows in insertion order, i.e.,
    // in ascending order. This suffices since the rows are idx.
    stable_sort(rowsToProcess.begin(), rowsToProcess.end());
    print_rows(rowsToProcess, colsToPrint, quiet);

    cout << "Printed " << numProcessedRows
         << " matching rows from " << tableName
         << endl;
}
} // HASH_scan()

/// @brief A full scan traverses the entire data table.
/// @param operation
/// @param te
/// @param colToCheck
/// @param deleteCommand
/// @param quiet
/// @param colsToPrint
void Table::full_scan(
char &operation, TableEntry &te,
string &colToCheck, bool deleteCommand,
bool &quiet,
const vector<string> &colsToPrint)
{
size_t colIdx = get_column_idx(colToCheck);

if (deleteCommand)
{
    switch (operation)
    {
        case '=':
        {
            EQfunctor eq(te, colIdx);
            delete_if(eq);
            break;
        }

        case '>':
        {
            Greaterfunctor gr(te, colIdx);
            delete_if(gr);
            break;
        }

        case '<':
        {
            Lessfunctor ls(te, colIdx);
            delete_if(ls);
            break;
        }

        default:
            break;
    } // switch
}
else
{
    switch (operation)
    {
        case '=':
        {
            EQfunctor eq(te, colIdx);
            print_if(colsToPrint, eq, quiet);
            break;
        }

        case '>':
        {
            Greaterfunctor gr(te, colIdx);
            print_if(colsToPrint, gr, quiet);
            break;
        }

        case '<':
        {
            Lessfunctor ls(te, colIdx);
            print_if(colsToPrint, ls, quiet);
            break;
        }

        default:
            break;
    } // switch
} // else
} // full_scan()

/// @brief Full scans delete helper. It passes the functor/predicate "condition" to the remove_if member to filter data rows that pass the query's condition, which will use one in the set {=, <, or >}.
/// @tparam Pred
/// @param condition
template <typename Pred>
void Table::delete_if(Pred &condition)
{
// Put delete_if rows at the tail.
auto it = remove_if(
data.begin(),
data.end(),
condition
);

// Erase the delete_if tail.
data.erase(it, data.end());

// Old size - New size = Deleted number of rows.
size_t deletedCount = rows - data.size();

// Update the member variable.
rows = data.size();

cout << "Deleted " << deletedCount
     << " rows from " << tableName
     << endl;
} // delete_if()

/// @brief Full scans print helper. It calls the functor/predicate "condition" and passes it the row to see if it passes the query's condition, which will be one in the set {=, <, or >}.
/// @tparam Pred
/// @param colsToPrint
/// @param condition
/// @param quiet
template <typename Pred>
void Table::print_if(
const vector<string> &colsToPrint,
Pred &condition, bool &quiet)
{
// If the condition is satisfied on the entry
// at coord: (row, colName), then print it.
int count = 0;
for (const auto &row : data)
{
bool satisfied = condition(row);
if (satisfied)
{
if (!quiet)
{
for (string colName : colsToPrint)
entry_printer(row, colName);
cout << endl;
}

        count++;
    }
} // for i

cout << "Printed " << count
     << " matching rows from "
     << tableName << endl;
} // print_if()

/// @brief The PRINT command's helper when there is no 'WHERE' clause.
/// @param colsToPrint
/// @param quiet
void Table::print_all(
const vector<string> &colsToPrint,
bool &quiet)
{
if (!quiet)
{
// Column headers
MessageHandler::print_col_headers(colsToPrint, quiet);

    // Column values
    for (const auto &row : data)
    {
        for (string colName : colsToPrint)
            entry_printer(row, colName);
        cout << endl;
    }
}

cout << "Printed " << rows
     << " matching rows from "
     << tableName << endl;
} // print_all()

/// @brief Index scans print helper.
/// @param rows
/// @param colsToPrint
/// @param quiet
void Table::print_rows(
const vector<size_t> &rows,
const vector<string> &colsToPrint,
bool quiet)
{
if (!quiet)
{
for (size_t row : rows)
{
for (string colName : colsToPrint)
entry_printer(row, colName);
cout << endl;
}
}
} // print_rows()

/// @brief Syntax: REMOVE <tablename>
/// @param dataBase
void remove(
unordered_map<string, Table> &dataBase)
{
string tn;
cin >> tn;

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::REMOVE)
) { return; }

dataBase.erase(tn);
cout << "Table " << tn << " deleted" << endl;
} // remove()

/// @brief Syntax: DELETE FROM <tablename> WHERE <colname> <OP> <value>
/// @param dataBase
void delete_from(unordered_map<string, Table> &dataBase)
{
// Read the <tablename>.
string tn;
cin >> tn;

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::DELETE)
) { return; }

// Extract the current data table.
Table &table = dataBase.at(tn);

// Throw away the 'WHERE' string.
string junk;
cin >> junk;

// Read the condition col name <colname>.
string conditionCol;
cin >> conditionCol;

// Validate <colname> exists.
if (!validate_column_name(
    table,
    conditionCol,
    tn,
    CommandType::DELETE)
) { return; }

// Read the condition operator {>, <, =}:
char operation; // <OP>
cin >> operation;

// 4way: string, int, double, bool
table.four_way(
    table.get_column_type(conditionCol),
    [&](TableEntry &te)
    {
        table.three_way(
            operation,
            {},              // nothing to print
            te,
            conditionCol,
            table.quietMode, // dummy 'quiet' boolean
            true             // DELETE command
        );
    }
);

table.update_index();
} // delete_from()

/// @brief Syntax: GENERATE FOR <tablename> <indextype> INDEX ON <colname>
/// @param dataBase
void generate_index(std::unordered_map<std::string, Table> &dataBase)
{
// Read the <tablename>.
string tn;
cin >> tn;

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::GENERATE)
) { return; }

// Extract the current data table.
Table &table = dataBase.at(tn);

// Read the type of index requested {hash, bst}.
string indexType; // <indextype>
cin >> indexType;

switch (indexType[0])
{
    case 'h':
        table.idxStatus = idxStat::Hash;
        table.create_hash_index();
        break;

    case 'b':
        table.idxStatus = idxStat::BST;
        table.create_BST_index();
        break;

    default:
        break;
} // switch
} // generate_index()

/// @brief Maintains the index state.
void Table::update_index()
{
switch (idxStatus)
{
case Hash:
{
regenerate_hash_index();
break;
} // Hash

    case BST:
    {
        regenerate_BST_index();
        break;
    } // BST

    case None:
        // biz as uzual        
    default:
        break;
} // switch
} // update_index

/// @brief Maps table entries to their table positions
/// @tparam IndexContainer
/// @param index
template <typename IndexContainer>
void Table::populate_index(IndexContainer &index)
{
// Clear existing index
idxHash.clear();
idxBST.clear();

/// NOTE: If you know roughly how many unique entries you’ll have in idxHash, calling reserve(n) before populating it can reduce rehashing overhead.

// Fill the index container with entries: {tableEntry : indices}
for (size_t i = 0; i < rows; i++)
    index[data[i][idxCol]].push_back(i);
} // populate_index()

/// @brief Handles the "INDEX ON <colname>" part of the GENERATE command.
void Table::create_hash_index()
{
// Read in the "INDEX ON" part and the index column name.
string junk, indexColName;
cin >> junk >> junk >> indexColName; // <colname>

// Validate the column's existence.
if (!set_index_idx(indexColName))
{ return; }

populate_index(idxHash);

cout << "Created hash index for table " << tableName
     << " on column " << indexColName << endl;
} // create_hash_index()

/// @brief Helper to maintain the index upon insertions and deletions.
void Table::regenerate_hash_index()
{
populate_index(idxHash);
} // regenerate_hash_index()

/// @brief Handles the "INDEX ON <colname>" part of the GENERATE command.
void Table::create_BST_index()
{
// Read in the "INDEX ON" part and the index column name.
string junk, indexColName;
cin >> junk >> junk >> indexColName; // <colname>

// Validate the column's existence.
if (!set_index_idx(indexColName))
{ return; }

populate_index(idxBST);

cout << "Created bst index for table " << tableName
     << " on column " << indexColName << endl;
} // create_BST_index()

/// @brief Helper to maintain the index upon insertions and deletions.
void Table::regenerate_BST_index()
{
populate_index(idxBST);
} // regenerate_bst_index()

/// @brief Syntax: JOIN <tablename1> AND <tablename2> WHERE <colname1> = <colname2> AND PRINT <N> <print_colname1> <1|2> <print_colname2> <1|2> ... <print_colnameN> <1|2>
/// @param dataBase
/// @param quiet
void join(unordered_map<string, Table> &dataBase, bool &quiet)
{
size_t printCounter = 0;
string tn, junk;

// Read and validate first table:
cin >> tn    // <tablename1>
    >> junk; // the "AND" string

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::JOIN)
) { return; }

// Extract the current data table1.
Table &table1 = dataBase.at(tn);
const vector<TableEntry> *table1Rows = table1.data.data();
size_t table1Size = table1.rows;

// Read and validate second table:
cin >> tn    // <tablename2>
    >> junk; // the "WHERE" string

if (!validate_table_name(
    dataBase,
    tn,
    CommandType::JOIN)
) { return; }

// Extract the current data table2.
Table &table2 = dataBase.at(tn);

// Get join condition columns: <lhs = rhs>
string colToCheck;
cin >> colToCheck // lhs: <colname1>
    >> junk;      // and '='
size_t lhsIndex = 0, rhsIndex = 0;

// Validate the lhs name:
if (!validate_column_name(
    table1,
    colToCheck,
    table1.tableName,
    CommandType::JOIN)
) { return; }

lhsIndex = table1.get_column_idx(colToCheck);

// Get join condition columns: <lhs = rhs>
cin >> colToCheck    // rhs: <colname2>
    >> junk >> junk; // "AND PRINT" strings

// Validate the rhs name:
if (!validate_column_name(
    table2,
    colToCheck,
    table2.tableName,
    CommandType::JOIN)
) { return; }

rhsIndex = table2.get_column_idx(colToCheck);

// Read the number of columns requested.
size_t numPrintCols; // <N>
cin >> numPrintCols;

// Store column names and their table ownership:
// {colName, tableNumber}
vector<string> colsToPrint;
vector<size_t> tablesToPrint;
colsToPrint.reserve(numPrintCols);
tablesToPrint.reserve(numPrintCols);

// Validate the requested columns.
for (size_t i = 0; i < numPrintCols; i++)
{
    string colName;     // <print_colnameN>
    size_t tableNumber; // <1|2>
    cin >> colName >> tableNumber;

    Table &table = (tableNumber == 1) ? table1 : table2;

    if (!validate_column_name(
        table,
        colName,
        table.tableName,
        CommandType::JOIN)
    ) { return; }

    colsToPrint.emplace_back(colName);
    tablesToPrint.push_back(tableNumber);
} // for i in columns to print

MessageHandler::print_col_headers(colsToPrint, quiet);

// Check if an index is available on the rhs column.
bool indexExists = ((table2.idxStatus != idxStat::None) &&
                    (table2.idxCol == rhsIndex));

// If an index is available, then use it on the 2nd table
if (indexExists)
{
    switch (table2.idxStatus)
    {
        // BST scan
        case idxStat::BST:
        {
            // Traverse table 1 and look for its match in table 2's index:
            for (size_t i = 0; i < table1Size; i++)
            {
                // Current entry from table 1: lhs.
                TableEntry &lhs = table1.data[i][lhsIndex];
                if (table2.idxBST.contains(lhs))
                {
                    // Save the entry's mapped-to rows.
                    auto &rows = table2.idxBST.at(lhs);
                    size_t numPrintRows = rows.size();
                    printCounter += numPrintRows;

                    if (!quiet)
                    {
                        // Loop thru each row-idx table 1's entry maps-to:
                        for (size_t j = 0; j < numPrintRows; j++)
                        {
                            // Loop thru the set of columns requested to print
                            for (size_t k = 0; k < numPrintCols; k++)
                            {
                                // Get the entry from either table 1 or table 2:
                                if (tablesToPrint[k] == 1)
                                    table1.entry_printer(i, colsToPrint[k]);
                                else
                                    table2.entry_printer(rows[j], colsToPrint[k]);
                            } // for columns to print

                            cout << endl;
                        } // for rows to print
                    }
                } // if not found
            } // for i in table 1
            break;
        }

        // Hash map scan
        case idxStat::Hash:
        {
            // Traverse table 1 and look for its match in table 2's index:
            for (size_t i = 0; i < table1Size; i++)
            {
                // Current entry from table 1: lhs.
                TableEntry &lhs = table1.data[i][lhsIndex];
                if (table2.idxHash.contains(lhs))
                {
                    // Save the entry's mapped-to rows.
                    auto &rows = table2.idxHash.at(lhs);
                    size_t numPrintRows = rows.size();
                    printCounter += numPrintRows;

                    if (!quiet)
                    {
                        // Loop thru each row idx table 1's entry maps-to:
                        for (size_t j = 0; j < numPrintRows; j++)
                        {
                            // Loop thru the set of columns requested to print
                            for (size_t k = 0; k < numPrintCols; k++)
                            {
                                // Get the entry from either table 1 or table 2:
                                if (tablesToPrint[k] == 1)
                                    table1.entry_printer(i, colsToPrint[k]);
                                else
                                    table2.entry_printer(rows[j], colsToPrint[k]);
                            } // for columns to print

                            cout << endl;
                        } // for rows to print
                    }
                } // if not found
            } // for i in table 1
            break;
        }

        // Full scan
        case idxStat::None:
        {
            // SHOULD NEVER REACH HERE
        }

        default:
            break;
    } // switch 
} // if index exists
// Full scan
else
{
    // No index: full scan of table2
    const vector<TableEntry> *table2Rows = table2.data.data();
    size_t table2Size = table2.rows;

    // Traverse table 1:
    for (size_t i = 0; i < table1Size; ++i)
    {
        const TableEntry &lhs = table1Rows[i][lhsIndex];

        // Traverse table 2:
        for (size_t j = 0; j < table2Size; ++j)
        {
            const TableEntry &rhs = table2Rows[j][rhsIndex];

            // Case: equality '='
            if (lhs == rhs)
            {
                printCounter++;
                if (!quiet)
                {
                    // Loop thru the set of columns requested to print
                    for (size_t k = 0; k < numPrintCols; k++)
                    {
                        // Get the entry from either table 1 or table 2:
                        if (tablesToPrint[k] == 1)
                            table1.entry_printer(i, colsToPrint[k]);
                        else
                            table2.entry_printer(j, colsToPrint[k]);
                    } // for columns to print

                    cout << endl;
                }
            }
        }
    }
}

cout << "Printed " << printCounter
     << " rows from joining "
     << table1.tableName << " to "
     << table2.tableName << endl;
} // join()

/// @brief Print helper to extract and print table entries.
/// @brief Overloaded to accept a row idx to access the data base.
/// @param row
/// @param colIndex
void Table::entry_printer(size_t row, string colName)
{
cout << data[row][colNamesAndIdx[colName]] << " ";
} // entry_printer()

/// @brief Print helper to extract and print table entries.
/// @brief Overloaded to accept an entire row of table entries.
/// @param row
/// @param colIndex
void Table::entry_printer(const vector<TableEntry> &row, string colName)
{
cout << row[colNamesAndIdx[colName]] << " ";
} // entry_printer()

// Add the new abstraction function
void print_scan_results(
    CommandType command,
    bool &quiet,
    std::vector<size_t> &rowsVec,
    const std::vector<std::string> &colsToPrint
);

// Update function declarations to use CommandType instead of deleteCommand
void full_scan(
    char &operation, TableEntry &te,
    std::string &colToCheck, CommandType command,
    bool &quiet,
    const std::vector<std::string> &colsToPrint
);

void BST_scan(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, CommandType command
);

void HASH_scan(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, CommandType command
);

void index_lookup(
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, bool &quiet, CommandType command
);

void three_way(
    char &operation,
    const std::vector<std::string> &colsToPrint,
    TableEntry &te, std::string &colToCheck,
    bool &quiet, CommandType command
);

