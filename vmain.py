
import vfunc
import camelot
import pandas as pd
import unidecode
import tabula

def transf_pdf(table, values):
    '''
    transforms imported table into preliminary dataframe.
    table: import from camelot
    returns: dataframe
    '''
    #transform into dataframe
    if isinstance(table, pd.DataFrame): #for dates with tabula
        df = table
        na_values = True
    else:
        df = table[0].df
        na_values = False
        if(len(df.columns)) == 8:
            df = vfunc.mult_table(df)            
    #separate parallel columns
    df1 = df.loc[:, '0':'2']
    df2 = df.loc[:, '3':'5']
    #correction of tab2
    if len(df2.columns) == 2:
        df2 = vfunc.fix_table(df2)
    #rename and append
    df2 = df2.rename(columns = {3:0,
                                4:1,
                                5:2})
    df = pd.concat([df1, df2]).reset_index(drop = True)
    #rename new columns
    df = df.rename(columns = {0:'Parroquia',
                              1:'Casos',
                              2:'Porcentaje'})
    #drop rows witn na
    if na_values == True: #for dates with tabula
        df = df.dropna()
    else:
        df = df.drop(df[(df['Parroquia'] == '')].index).reset_index(drop = True)
    #pick value (cases or percent)
    df = vfunc.data_values(df, values)
    return df

def format_table(table, values):
    '''
    corrects details from previous imported table.
    table: import from camelot
    return: dataframe
    fn: transf_pdf()
    pk: unidecode
    '''
    #applies previous fn.
    df = transf_pdf(table, values)
    #overall format
    df['Parroquia'] = df['Parroquia'].apply(unidecode.unidecode) #removes accents
    df = df.drop_duplicates(subset = 'Parroquia', keep = 'last') #removes duplicates
    #removes names for 'canton'
    cantones = ['D. M. QUITO', 'MEJIA', 'PEDRO MONCAYO', 'RUMINAHUI', 'TOTAL', 'Canton / Parroquia', 
                'DISTRITO METROPOLITANO DE QUITO', 'Parroquia de domicilio declarada por la persona atendida',
                'Total', ' TOTAL', 'QUITO', 'QUITO (CABECERA CANTONAL)', 'SITUACIO', 
                '* Corresponde a Quito Cabecera Cantonal']
    for row in df['Parroquia']:
        if row in cantones:
            df = df.drop(df[df.Parroquia == row].index)
    df = vfunc.unify_names(df)
    return df.reset_index(drop = True)


def v_chan(filename, values):
    '''
    reads names in files to import tables.
    applies previous fn. to transform table.
    merges tables for final result.    
    filename: .txt file
    return: dataframe
    fn: vfunc.read_files(), format_table(), vfunc.extract_date(), vfunc.add_date
    pk: tkinter, camelot, urllib.parse
    '''
    #reads names of files
    files = vfunc.read_files(filename)
    #extracts date, month, day and transform filename for url
    for file in files:
        date = vfunc.extract_date(file, pattern='date')
        day = vfunc.extract_date(file, pattern='day')
        ini_month = vfunc.extract_date(file, pattern='month')
        month = vfunc.fix_month(ini_month, day)
        file_url = vfunc.verify_quote(file)
        #access pdf and transforms it into table
        print((date) + " in " + (file))        
        if ini_month == "07" and int(day) > 6:
            table = tabula.read_pdf("https://coe-pichincha.senescyt.gob.ec/wp-content/uploads/2020/" + month + "/" + file_url, 
                                    columns=[357, 492, 574, 842, 976, 1058], guess=False, pages='5', pandas_options={'header':None})
        elif (ini_month == "06" and day != "01") or ini_month == "07":
            table = camelot.read_pdf("https://coe-pichincha.senescyt.gob.ec/wp-content/uploads/2020/" + month + "/" + file_url, 
                                     pages = '5', flavor = "stream")
            print("Total tables extracted:", table.n)
        else:
            table = camelot.read_pdf("https://coe-pichincha.senescyt.gob.ec/wp-content/uploads/2020/" + month + "/" + file_url, 
                                     pages = '4', flavor = "stream")
            print("Total tables extracted:", table.n)
        #first file transforms to dataframe. works as basis
        if file == files[0]:
            df = vfunc.add_date(format_table(table, values), date)            
        #other files are merged into first
        else:
            df = pd.merge(
                df,
                vfunc.add_date(format_table(table, values), date),
                how = 'outer', on = 'Parroquia')   
    return df

#data from April 10th until June 10th (71 pdfs)
# complete = v_chan("dfiles.txt", values = "all")
# cases = v_chan("dfiles.txt", values = "Casos") #number of cases
# percent = v_chan("dfiles.txt", values = "Porcentaje") #percentage of cases

#save base file
# complete.to_csv("vchan.csv", index = False)
# cases.to_csv("vchan_cases.csv", index = False)
# percent.to_csv("vchan_percent.csv", index = False)

#to update values
# def update_values(df, filename, values):
#     '''
#     updates values for dataframe.
#     df: previous dataframe
#     filename: complete filename with all dates
#     values: 'all' for everything, 'Casos' for cases, 'Porcentaje' for percentages
#     returns: dataframe
#     '''
#     #gets name from last column
#     last_column = df.columns[len(df.columns) - 1]
#     #gets last registered date
#     last_date = vfunc.extract_date(last_column, pattern = 'date')
#     #creates new textfile with missing dates
#     vfunc.new_filename(filename, last_date)
#     #imports pdfs into new df
#     new_df = v_chan("dupdate.txt", values)
#     #merges old df with new df
#     updated_df = pd.merge(df, new_df)
#     return updated_df

# complete = update_values(complete, "dfiles.txt", values = "all")
# complete.to_csv("vchan.csv", index = False)