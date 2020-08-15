
import numpy as np
import re
from urllib.parse import quote

def mult_table(df):
    '''
    if dataframe has 8 columns, it drops empty 
    columns and renames remaining columns
    df: dataframe
    return: dataframe
    '''
    df = df.drop(columns = [2,6])
    df = df.rename(columns = {3:2,
                              4:3,
                              5:4,
                              7:5})
    return df

def data_values(df, values = 'all'):
    '''
    default values is set to 'all' for complete data.
    'Casos' for cases and 'Porcentaje' for percentage
    df: dataframe
    values: str
    return: dataframe
    '''
    if values == 'all':
        return df
    elif values == 'Casos':
        df = df.drop(columns = ['Porcentaje'])
        return df
    elif values == 'Porcentaje':
        df = df.drop(columns = ['Casos'])    
        return df
    
def fix_table(df):
    '''
    this renames columns and switch order if there are only two columns
    instead of three. some tables have switched columns ('Parroquia' appears last).
    df: dataframe
    return: dataframe
    '''
    df = df.rename(columns = {3: 'e',
                              4: 'g'})
    replacement = {'e':{r'\n ':',',
                        r'\n':'',
                        r'  ':''}}
    df = df.replace(replacement, regex = True)
    df[['e', 'f']] = df['e'].str.split(',', expand = True) #splits values into 2 columns using a comma
    df = df.drop(df[df['f'].isnull()].index) #removes rows with None values
    if 'TUMBACO' in str(df['f']):
        df = df.rename(columns = {'e': 4,
                                  'f': 3,
                                  'g': 5})
        df = df[[3,4,5]]
        print("switch columns")
    else:
        df = df.rename(columns = {'e': 3,
                                  'f': 4,
                                  'g': 5})
    return df

def unify_names(df):
    '''
    removes characters and modifies strings for final table.
    changes decimals ',' to '.'
    df: dataframe
    return: dataframe
    '''
    df['Parroquia'] = df['Parroquia'].str.replace(r'\s\(.*\)|\s\*|\*|\s\(T','') #removes ' ( )| *|*'
    if 'Casos' in df:
        df['Casos'] = df['Casos'].str.replace(r'\(.*\)|A.*\)|\.','') #removes ' ( )' for dates after 07-07        
    name = {'ALANGASI': ['ALANGASi'],
            'MANUEL CORNEJO ASTORGA': ['MANUEL CORNEJO ASTORGA    '],
            'INDETERMINADO': ['INDETERMINADA']}
    for canton in name:
        for altname in name[canton]:
            df['Parroquia'] = np.where((df['Parroquia'] == altname),
                                       df['Parroquia'].str.replace(altname, canton),
                                       df['Parroquia'])
    if 'Porcentaje' in df:
        df['Porcentaje'] = df['Porcentaje'].str.replace(',','.')
    return df

def read_files(filename):
    '''
    reads txt and turns into list to transform files
    filename: "filename.txt"
    return: list with file names
    '''
    days = []
    dfile = open(filename, 'r')
    for line in dfile:
        days.append(line.strip())        
    return days

def extract_date(filename, pattern = 'date'):
    '''
    extracts date from filename.
    pattern is set to date to take the whole date (e.g. 24_06_2020),
    month (e.g. 06) or day (e.g. 20)
    filename: str
    pattern: str
    return: str
    '''
    date = re.compile(r'(?i)[\d]{2}[_][\d]{2}[_][\d]{4}') #e.g 20_05_2020
    month = re.compile(r'(?i)[\d]{2}[_]([\d]{2})[_][\d]{4}') #e.g. 05
    day = re.compile(r'(?i)([\d]{2})[_][\d]{2}[_][\d]{4}') #e.g 20
    if pattern == 'date':
        for match in re.findall(date, filename):
            return match
    elif pattern == 'month':
        for match in re.findall(month, filename):
            return match
    elif pattern == 'day':
        for match in re.findall(day, filename):
            return match

def fix_month(month, day):
    '''
    fixes last days of month to read pdf file
    month: str
    day: str
    return: str
    '''
    if int(day) >= 30 and int(month) < 7 and int(month) > 4:
        return str(int(month) + 1).zfill(2)
    elif int(day) > 30 and int(month) >= 7:
        return str(int(month) + 1).zfill(2)
    else:
        return month

def add_date(df, date):
    '''
    add string to column name
    df: dataframe
    date: str
    return: dataframe
    '''
    if 'Casos' in df:
        df = df.rename(columns = {'Casos' : 'Casos_' + date})
    if 'Porcentaje' in df:
        df = df.rename(columns = {'Porcentaje' : 'Porcentaje_' + date})                              
    return df

def verify_quote(filename):
    '''
    fixes a problem with the accents in the name of the files.
    some files have an accent (´ -%CC%81) instead of (´ %C3%AD).
    if correct accent is not found, 'no html' error appears
    filename: string
    '''
    pr_dates = ["23.-Infografía-Provincial-02_05_2020.pdf", 
                "6.-Infografía-Cantonal-29_05_2020.pdf", #no data 
                "Infografía-Cantonal-25_06_2020.pdf", #no data
                "105.-Infografía-Provincial-26_07_2020.pdf",
                "108.-Infografía-Provincial-29_07_2020.pdf"]
    if filename in pr_dates:
        corrected_accent = re.sub('Infografía', 'Infografía', filename) #the accents in these files are different from the rest
        return quote(corrected_accent)
    else:
        return quote(filename)

def new_filename(filename, date):
    '''
    creates new file with dates to be updated.
    filename: string
    date: string
    return: NA
    '''
    dates = read_files(filename)
    fr_date = dates.index("\n".join(s for s in dates if date in s)) #index of date in list
    last_dates = dates[fr_date + 1:] #slices from date until final date
    with open('dupdate.txt', 'w') as f:
        for item in last_dates:
            f.write('%s\n' % item)
    with open('dupdate.txt', 'r') as f:
        data = f.read()
        with open('dupdate.txt', 'w') as w:
            w.write(data[:-1])

def correct_names(df):
    '''
    adapts current df values of 'Parroquia' to the ones in the location
    df for merge.
    df: dataframe
    return: dataframe
    '''
    name = {'AMAGUAÑA': ['AMAGUANA'],
            'IÑAQUITO': ['INAQUITO'],
            'QUINCHE': ['EL QUINCHE']}
    for canton in name:
        for altname in name[canton]:
            df['Parroquia'] = np.where((df['Parroquia'] == altname),
                                       df['Parroquia'].str.replace(altname, canton),
                                       df['Parroquia'])
    return df

def col_to_dates(df):
    '''
    changes names of columns to dates
    df: dataframe
    return: dataframe
    '''
    list_of_col = list(df.columns)
    list_of_dates = [date.replace('Casos_', '') for date in list_of_col]    
    list_of_dates = [date.replace('_', '-') for date in list_of_dates]
    df.columns = list_of_dates
    return df

def create_annotations(df,last_column):
    '''
    turns df into label df by removing intermediate values
    df: dataframe
    last_column: int
    return: label dataframe
    '''
    annot_df = df.copy()
    col_list = list(annot_df.columns)
    col_list = col_list[0:last_column:5] #+ [col_list[-1]]
    for column in annot_df:
        annot_df = annot_df.fillna(0)
        annot_df[[column]] = annot_df[[column]].astype(int).astype(str)
        if column not in col_list:
            annot_df[column] = ""
    return annot_df