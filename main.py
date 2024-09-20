# Version 1.3 updated 20240801
# By Zengjie Xia

import pandas as pd
import numpy as np

def due_with_replicates(df):
    """
    input
    """
    # Group by Categories and aggregate the values into lists
    grouped_df = df.groupby(['Sample Barcode', 'Assay', 'Plex', 'Location', 'Carrier Barcode']).agg(list).reset_index()

    # lambda x: [value for value in x if not pd.isna(value)] # This function returns all the non-NaN values
    grouped_df['Replicate AEB'] = grouped_df['Replicate AEB'].apply(lambda x: [value for value in x if not pd.isna(value)])
    grouped_df['Replicate Conc.'] = grouped_df['Replicate Conc.'].apply(lambda x: [value for value in x if not pd.isna(value)])

    # Define a function to extract the first non-NaN value from a list
    def first_non_nan(lst):
        """
        input: list
        output: return the first non-nan value - for means and std  

        """
        for item in lst:
            if not pd.isna(item):
                return item
        return np.nan  # Return NaN if all values are NaN

    def report_flag(lst):
        """
        input: list
        output: return the combined non-nan flags in format of "item1";"item2" - - for "Flag"
        """
        flags = np.array(lst)
        flags = flags[~np.isnan(flags)]
        flags = np.unique(flags)
        flags = [str(int(x)) for x in flags]
        flags = ','.join(list(flags))
        return flags  # Return largest number for flag

    def report_error(lst):
        """
        input: list
        output: return the combined non-nan error message in format of "item1";"item2" - for "Errors"
        """
        err_msg = None
        for item in lst:
            if not pd.isna(item):
                if err_msg == None:
                    err_msg = str(item)
                else:
                    err_msg = err_msg + '; ' + str(item)
        if err_msg == None:
            return np.nan
        else:
            return err_msg  # Return largest number for flag


    # Manually expand the lists into separate columns
    expanded_df = pd.DataFrame()
    expanded_df['Sample Barcode'] = grouped_df['Sample Barcode']
    expanded_df['Assay'] = grouped_df['Assay']
    expanded_df['Plex'] = grouped_df['Plex']
    expanded_df['Location'] = grouped_df['Location']
    expanded_df['Carrier Barcode'] = grouped_df['Carrier Barcode']
    
    # Create new columns for each AEB replicates in the lists
    if grouped_df['Replicate AEB'].apply(len).max() == 1:
        expanded_df[f'Replicate AEB'] = grouped_df['Replicate AEB'].apply(first_non_nan)
    else:
        for i in range(grouped_df['Replicate AEB'].apply(len).max()):  # Get the maximum length of lists in Value1
            expanded_df[f'Replicate AEB {i+1}'] = grouped_df['Replicate AEB'].apply(lambda x: x[i] if len(x) > i else None)

    expanded_df['Mean AEB'] = grouped_df['Mean AEB'].apply(first_non_nan)
    expanded_df['SD AEB'] = grouped_df['SD AEB'].apply(first_non_nan)
    expanded_df['CV AEB'] = grouped_df['CV AEB'].apply(first_non_nan)
    expanded_df['%CV AEB'] = expanded_df['CV AEB']*100
    
    # Create new columns for each Conc. replicates in the lists
    if grouped_df['Replicate Conc.'].apply(len).max() == 1:
        expanded_df[f'Replicate Conc. ({unit[0]})'] = grouped_df['Replicate Conc.'].apply(first_non_nan)
    else:
        for i in range(grouped_df['Replicate Conc.'].apply(len).max()):  # Get the maximum length of lists in Value1
            expanded_df[f'Replicate Conc. {i+1}'] = grouped_df['Replicate Conc.'].apply(lambda x: x[i] if len(x) > i else None)
    
    expanded_df[f'Mean Conc. ({unit[0]})'] = grouped_df['Mean Conc.'].apply(first_non_nan)
    expanded_df['SD Conc.'] = grouped_df['SD Conc.'].apply(first_non_nan)
    expanded_df['CV Conc.'] = grouped_df['CV Conc.'].apply(first_non_nan)
    expanded_df['%CV Conc.'] = expanded_df['CV Conc.']*100

    expanded_df['Flags'] = grouped_df['Flags'].apply(report_flag)
    expanded_df['Errors'] = grouped_df['Errors'].apply(report_error)
    
    expanded_df = expanded_df.sort_values(by=['Assay', "Plex", 'Sample Barcode'])
    expanded_df = expanded_df.reset_index(drop=True)
    
    return expanded_df

if __name__ == "__main__":

    while True:
        path = input('Please input the path for raw data: \n')
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]

        try:
            df =  pd.read_csv(path)
        except UnicodeDecodeError:
            print("Error: The path is not for a .csv file.")
            continue
        except FileNotFoundError:
            print("Error: File does not exist.")
            continue

        unit = df.Unit.unique() # Get the unit for assay
        if len(unit) > 1:
            print(f'Warning: Multiple concentration units found in the data, they are {unit}. The first one in the list will be used in the result file: {unit[0]}.')

        df = df[['Sample Barcode', 'Assay', 'Plex', 'Location', 'Carrier Barcode',
               'Replicate AEB', 'Mean AEB', 'SD AEB', 'CV AEB', 
                'Replicate Conc.','Mean Conc.', 'SD Conc.', 'CV Conc.',
                 #'Unit', 'Job Status', 'Job ID',
               'Flags', 'Errors']]
        # Only keep columns listed above

        # This part is more fragile than others because we are using specific condition to select data entries.
        # There should be no uncategorised entry, if there is, check the "Sample Barcode" naming.
        # Any entry with "Calibrator" in their "Sample Barcode" is a calibrator
        df_cals = df.loc[df['Sample Barcode'].str.contains('Calibrator')] 

        # Any entry with 
        # "Control", "Int Ctrl", "Digital", "Analog"
        # in their "Sample Barcode" is a control
        df_ctrls = df.loc[(df['Sample Barcode'].str.contains('Control'))|(df['Sample Barcode'].str.contains('Int Ctrl'))|(df['Sample Barcode'].str.contains('Digital'))|(df['Sample Barcode'].str.contains('Analog'))]
        
        # All entries with numerical "Sample Barcode" is a sample
        df_samples = df.loc[df['Sample Barcode'].str.isnumeric()]

        df_leftover = df.loc[~df['Sample Barcode'].str.isnumeric()]
        for i in ['Calibrator', 'Control', 'Int Ctrl', 'Digital', 'Analog']:
            df_leftover = df_leftover.loc[~df_leftover['Sample Barcode'].str.contains(i)]
        print(f"{len(df_cals)} calibration levels, {len(df_ctrls)} controls and {len(df_samples)} samples were found. \n{len(df_leftover)} entries were uncategorised.")


        # Process calibration standards
        df_cals = due_with_replicates(df_cals) 

        # Process controls
        df_ctrls = due_with_replicates(df_ctrls)
        df_ctrls.drop(columns=['%CV AEB'], inplace=True) # Don't need this for controls now

        # Process samples
        df_samples = due_with_replicates(df_samples)
        df_samples.drop(columns=['%CV AEB', '%CV Conc.'], inplace=True) # Don't need these for samples now
        df_samples['Sample Barcode'] = df_samples['Sample Barcode'].astype(int)
        df_samples = df_samples.sort_values(by=['Assay', "Plex", 'Sample Barcode'])

        # Calculate intra-plate %CV
        # Based on Int Ctrls and drop all entries for machine calculated means
        df_intra_CV = df.loc[(df['Sample Barcode'].str.contains('Int Ctrl'))|(df['Sample Barcode'].str.contains('Digital'))|(df['Sample Barcode'].str.contains('Analog'))]
        df_intra_CV = df_intra_CV.loc[df_intra_CV['Replicate Conc.'].notna()]
        df_intra_CV['Ctrl Type'] = df_intra_CV['Sample Barcode'].str.replace(r'\d', '',regex=True)
        # Calculate for each plex
        #df_intra_CV = df_intra_CV.groupby(['Assay', 'Plex', 'Carrier Barcode', 'Ctrl Type', 'Location']).agg({'Replicate Conc.':'mean'}) # Use the average readout from the well.
        #df_intra_CV = df_intra_CV.reset_index()
        df_intra_CV = df_intra_CV.groupby(['Assay', 'Plex', 'Carrier Barcode', 'Ctrl Type']).agg(Average=('Replicate Conc.','mean'), Stdev=('Replicate Conc.','std'), NumberOfTests=('Replicate Conc.','count'))
        df_intra_CV = df_intra_CV.reset_index()
        df_intra_CV['%CV'] = df_intra_CV['Stdev']/df_intra_CV['Average']*100
        df_intra_CV = df_intra_CV[['Assay', 'Plex', 'Ctrl Type', 'Carrier Barcode', 'Average', 'Stdev', '%CV', 'NumberOfTests']]
        #df_intra_CV.drop(columns='Ctrl Type', inplace=True)

        # Calculate inter-plate %CV
        # Based on Int Ctrls and drop all entries for machine calculated means
        df_inter_CV = df.loc[(df['Sample Barcode'].str.contains('Int Ctrl'))|(df['Sample Barcode'].str.contains('Digital'))|(df['Sample Barcode'].str.contains('Analog'))]
        df_inter_CV = df_inter_CV.loc[df_inter_CV['Replicate Conc.'].notna()]
        df_inter_CV['Ctrl Type'] = df_inter_CV['Sample Barcode'].str.replace(r'\d', '',regex=True)
        # Calculate for each plex
        #df_inter_CV = df_inter_CV.groupby(['Assay', 'Plex', 'Ctrl Type', 'Location']).agg({'Replicate Conc.':'mean'}) # Use the average readout from the well.
        #df_inter_CV = df_inter_CV.reset_index()
        df_inter_CV = df_inter_CV.groupby(['Assay', 'Plex', 'Ctrl Type']).agg(Average=('Replicate Conc.','mean'), Stdev=('Replicate Conc.','std'), NumberOfTests=('Replicate Conc.','count'))
        df_inter_CV = df_inter_CV.reset_index()
        df_inter_CV['%CV'] = df_inter_CV['Stdev']/df_inter_CV['Average']*100
        df_inter_CV = df_inter_CV[['Assay', 'Plex', 'Ctrl Type', 'Average', 'Stdev', '%CV', 'NumberOfTests']]
        #df_inter_CV.drop(columns='Ctrl Type', inplace=True)

        # Process uncategorised data if present
        if len(df_leftover) != 0:
            df_leftover = due_with_replicates(df_leftover)

        import pandas.io.formats.excel as pdexcel
        pdexcel.ExcelFormatter.header_style = None

        # Create a Pandas Excel writer using XlsxWriter as the engine
        with pd.ExcelWriter(path.replace('.csv', '_sorted.xlsx'), engine='xlsxwriter') as writer:
            # Write each DataFrame to a different worksheet
            df_samples=df_samples.style.set_properties(**{'text-align': 'center'})
            df_samples.to_excel(writer, sheet_name='Samples', index=False)
            df_ctrls=df_ctrls.style.set_properties(**{'text-align': 'center'})
            df_ctrls.to_excel(writer, sheet_name='Controls', index=False)
            df_cals=df_cals.style.set_properties(**{'text-align': 'center'})
            df_cals.to_excel(writer, sheet_name='Cals', index=False)
            df_intra_CV=df_intra_CV.style.set_properties(**{'text-align': 'center'})
            df_intra_CV.to_excel(writer, sheet_name='Intra-Plate %CV', index=False)
            df_inter_CV=df_inter_CV.style.set_properties(**{'text-align': 'center'})
            df_inter_CV.to_excel(writer, sheet_name='Inter-Plate %CV', index=False)

            # Access the workbook and worksheet objects
            workbook  = writer.book
            worksheet_cals = writer.sheets['Cals']
            worksheet_ctrls = writer.sheets['Controls']
            worksheet_samples = writer.sheets['Samples']
            worksheet_cv = writer.sheets['Intra-Plate %CV']
            worksheet_intercv = writer.sheets['Inter-Plate %CV']


            # Define a format for the highlighted cells, Highlight %CV AEB and %CV conc. > 15% in calibration sheet
            # Check the column name!
            highlight_format = workbook.add_format({'bg_color': 'yellow'})
            #worksheet_cals.conditional_format('J2:J1048575', {'type': 'cell',
            #                                        'criteria': '>',
            #                                        'value': 0.15,
            #                                        'format': highlight_format})
            worksheet_cals.conditional_format('K2:K1048575', {'type': 'cell',
                                                    'criteria': '>',
                                                    'value': 15,
                                                    'format': highlight_format})
            #worksheet_cals.conditional_format('P2:P1048575', {'type': 'cell',
            #                                        'criteria': '>',
            #                                        'value': 0.15,
            #                                        'format': highlight_format})
            worksheet_cals.conditional_format('Q2:Q1048575', {'type': 'cell',
                                                    'criteria': '>',
                                                    'value': 15,
                                                    'format': highlight_format})

            worksheet_ctrls.conditional_format('P2:P1048575', {'type': 'cell',
                                                    'criteria': '>',
                                                    'value': 15,
                                                    'format': highlight_format})

            # Define a format for the header
            header_format = workbook.add_format({'bold': True, 'bg_color': '#BFBFBF', 'valign': 'vcenter', 'align': 'center',})
            for col_num, value in enumerate(df_samples.columns.values):
                worksheet_samples.write(0, col_num, value, header_format)
            for col_num, value in enumerate(df_ctrls.columns.values):
                worksheet_ctrls.write(0, col_num, value, header_format)
            for col_num, value in enumerate(df_cals.columns.values):
                worksheet_cals.write(0, col_num, value, header_format)
            for col_num, value in enumerate(df_intra_CV.columns.values):
                worksheet_cv.write(0, col_num, value, header_format)
            for col_num, value in enumerate(df_inter_CV.columns.values):
                worksheet_intercv.write(0, col_num, value, header_format)

            # Create new sheet for uncategorised data if present
            if len(df_leftover) != 0:
                df_leftover=df_leftover.style.set_properties(**{'text-align': 'center'})
                df_leftover.to_excel(writer, sheet_name='Uncategorised', index=False)
                worksheet_leftover = writer.sheets['Uncategorised']
                for col_num, value in enumerate(df_leftover.columns.values):
                    worksheet_leftover.write(0, col_num, value, header_format)

        print(f"Sorted excel file generated successfully at {path.replace('.csv', '_sorted.xlsx')}.\n")