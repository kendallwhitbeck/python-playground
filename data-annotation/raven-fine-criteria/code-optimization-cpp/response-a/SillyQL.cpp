// SillyQL.cpp (modified join function)


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


    // Store column names and their table ownership:
    vector<string> colsToPrint;
    vector<size_t> tablesToPrint;
    colsToPrint.reserve(numPrintCols);
    tablesToPrint.reserve(numPrintCols);


    // Validate the requested columns.
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


    // If an index exists on the correct column, use it
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
                // Should never reach here due to indexExists check
                break;
        }
    }
    else // No index or wrong column: create temporary hash index
    {
        // Create temporary hash index for table2's join column
        unordered_map<TableEntry, vector<size_t>> tempHashIndex;
        tempHashIndex.reserve(table2.rows); // Pre-allocate for efficiency


        // Populate temporary hash index
        for (size_t i = 0; i < table2.rows; i++) {
            tempHashIndex[table2.data[i][rhsIndex]].push_back(i);
        }


        // Perform join using temporary hash index
        for (size_t i = 0; i < table1Size; i++)
        {
            TableEntry &lhs = table1.data[i][lhsIndex];
            if (tempHashIndex.contains(lhs))
            {
                auto &rows = tempHashIndex.at(lhs);
                size_t numPrintRows = rows.size();
                printCounter += numPrintRows;


                if (!quiet)
                {
                    // Sort rows for consistent output order (similar to HASH_scan)
                    vector<size_t> sortedRows = rows;
                    stable_sort(sortedRows.begin(), sortedRows.end());


                    for (size_t j = 0; j < numPrintRows; j++)
                    {
                        for (size_t k = 0; k < numPrintCols; k++)
                        {
                            if (tablesToPrint[k] == 1)
                                table1.entry_printer(i, colsToPrint[k]);
                            else
                                table2.entry_printer(sortedRows[j], colsToPrint[k]);
                        }
                        cout << endl;
                    }
                }
            }
        }


        // Temporary index is automatically destroyed when it goes out of scope
    }


    cout << "Printed " << printCounter
         << " rows from joining "
         << table1.tableName << " to "
         << table2.tableName << endl;
}