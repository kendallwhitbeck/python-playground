// In SillyQL.cpp, modify the join function:
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


    Table &table2 = dataBase.at(tn);


    // Get join condition columns: <lhs = rhs>
    string colToCheck;
    cin >> colToCheck // lhs: <colname1>
        >> junk;      // and '='
    size_t lhsIndex = 0, rhsIndex = 0;


    if (!validate_column_name(
        table1,
        colToCheck,
        table1.tableName,
        CommandType::JOIN)
    ) { return; }


    lhsIndex = table1.get_column_idx(colToCheck);


    cin >> colToCheck    // rhs: <colname2>
        >> junk >> junk; // "AND PRINT" strings


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


    vector<string> colsToPrint;
    vector<size_t> tablesToPrint;
    colsToPrint.reserve(numPrintCols);
    tablesToPrint.reserve(numPrintCols);


    for (size_t i = 0; i < numPrintCols; i++)
    {
        string colName;
        size_t tableNumber;
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
    }


    MessageHandler::print_col_headers(colsToPrint, quiet);


    // Check if an index is available on the rhs column
    bool indexExists = ((table2.idxStatus != idxStat::None) &&
                        (table2.idxCol == rhsIndex));


    if (indexExists)
    {
        switch (table2.idxStatus)
        {
            case idxStat::BST:
            {
                for (size_t i = 0; i < table1Size; i++)
                {
                    TableEntry &lhs = table1.data[i][lhsIndex];
                    if (table2.idxBST.contains(lhs))
                    {
                        auto &rows = table2.idxBST.at(lhs);
                        size_t numPrintRows = rows.size();
                        printCounter += numPrintRows;


                        if (!quiet)
                        {
                            for (size_t j = 0; j < numPrintRows; j++)
                            {
                                for (size_t k = 0; k < numPrintCols; k++)
                                {
                                    if (tablesToPrint[k] == 1)
                                        table1.entry_printer(i, colsToPrint[k]);
                                    else
                                        table2.entry_printer(rows[j], colsToPrint[k]);
                                }
                                cout << endl;
                            }
                        }
                    }
                }
                break;
            }


            case idxStat::Hash:
            {
                for (size_t i = 0; i < table1Size; i++)
                {
                    TableEntry &lhs = table1.data[i][lhsIndex];
                    if (table2.idxHash.contains(lhs))
                    {
                        auto &rows = table2.idxHash.at(lhs);
                        size_t numPrintRows = rows.size();
                        printCounter += numPrintRows;


                        if (!quiet)
                        {
                            for (size_t j = 0; j < numPrintRows; j++)
                            {
                                for (size_t k = 0; k < numPrintCols; k++)
                                {
                                    if (tablesToPrint[k] == 1)
                                        table1.entry_printer(i, colsToPrint[k]);
                                    else
                                        table2.entry_printer(rows[j], colsToPrint[k]);
                                }
                                cout << endl;
                            }
                        }
                    }
                }
                break;
            }


            case idxStat::None:
            default:
                // Should never reach here due to indexExists check
                break;
        }
    }
    else // Hash scan with temporary index
    {
        // Create temporary hash index on table2's join column
        table2.tempIdxHash.clear();
        for (size_t i = 0; i < table2.rows; i++) {
            table2.tempIdxHash[table2.data[i][rhsIndex]].push_back(i);
        }


        // Perform join using temporary hash index
        for (size_t i = 0; i < table1Size; i++)
        {
            TableEntry &lhs = table1.data[i][lhsIndex];
            if (table2.tempIdxHash.contains(lhs))
            {
                auto &rows = table2.tempIdxHash.at(lhs);
                size_t numPrintRows = rows.size();
                printCounter += numPrintRows;


                if (!quiet)
                {
                    for (size_t j = 0; j < numPrintRows; j++)
                    {
                        for (size_t k = 0; k < numPrintCols; k++)
                        {
                            if (tablesToPrint[k] == 1)
                                table1.entry_printer(i, colsToPrint[k]);
                            else
                                table2.entry_printer(rows[j], colsToPrint[k]);
                        }
                        cout << endl;
                    }
                }
            }
        }


        // Clear temporary index
        table2.tempIdxHash.clear();
    }


    cout << "Printed " << printCounter
         << " rows from joining "
         << table1.tableName << " to "
         << table2.tableName << endl;
}