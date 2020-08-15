
import vfunc
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# import data for cases for three months and names of locations
cases = pd.read_csv('vchan_cases.csv')
locations = pd.read_csv('locations.csv', encoding='latin1')

# merging
cases = pd.merge(vfunc.correct_names(cases), locations, how='left', on='Parroquia')

# reordering and formating columns
col = cases['Canton']
cases.insert(cases.columns.get_loc('Parroquia'), col.name, col, allow_duplicates = True) #moving canton to the front
cases = cases.loc[:,~cases.columns.duplicated()] #deleting duplicated column
cases = cases.sort_values(['Canton','Tipo','Parroquia'])
cases['Parroquia'] = cases.Parroquia.str.title()

# changing names of columns
vfunc.col_to_dates(cases)
cases.set_index('Parroquia', inplace = True)

# heatmap function
def heatmap_canton(df, CANTON, TIPO, last_column=0, hm='General'):
    '''
    creates heatmap based on cases (number or percent) based on 
    selected canton, type of parish and type of data
    df: dataframe
    CANTON: str
    TIPO: str
    hm: str ("General or Normal")
    returns: seaborn heatmap
    '''
    df = df.drop(df[df.Canton != CANTON].index)
    df = df.drop(df[df.Tipo != TIPO].index)
    df = df.drop(columns = ['Canton', 'Tipo'])    
    annota = vfunc.create_annotations(df, last_column-3)
    if hm == 'General':
        plt.figure(figsize=(20,17))
        #change annot to True for numbers
        ax = sns.heatmap(df, cmap=sns.cm.rocket_r, robust=True, xticklabels=5, annot=annota, annot_kws={'fontsize':7},
                         fmt='', cbar=False, mask=df.isnull())        
        plt.title('Heatmap of reported cases in '+CANTON.title()+' ('+TIPO.title()+')', fontsize=18)
        # ax.vlines([14,24,31], *ax.get_ylim()) #adds vertical lines for specific dates
    elif hm == 'Normal':
        normal_df = df.div(df.max(axis=1), axis=0)
        plt.figure(figsize=(20,17))        
        ax = sns.heatmap(normal_df, cmap=sns.cm.rocket_r, robust=True, xticklabels=5, annot=False,
                         cbar=False, mask=df.isnull())
        # ax.vlines([14,24,31], *ax.get_ylim())
        plt.title('Heatmap of reported cases in '+CANTON.title()+' ('+TIPO.title()+')'+' - Normalized', fontsize=18)

# plotting heatmaps for each canton and type
# cantones = locations['Canton'].drop_duplicates().to_list()
# for canton in cantones:
#     for tipo in ['URBANA', 'RURAL']:
#         for hm in ['General', 'Normal']:
#             fig = heatmap_canton(cases, canton, tipo, hm=hm)
#             plt.savefig('casos_'+canton+'_'+tipo+'_'+hm+'.png', bbox_inches='tight')
#             plt.close(fig)


heatmap_canton(cases, 'QUITO', 'URBANA', 101)
plt.savefig('casos_quito_urb_gen.png', bbox_inches='tight')

heatmap_canton(cases, 'QUITO', 'URBANA', hm='Normal')
plt.savefig('casos_quito_urb_norm.png', bbox_inches='tight')

heatmap_canton(cases, 'QUITO', 'RURAL', 101)
plt.savefig('casos_quito_rur_gen.png', bbox_inches='tight')

heatmap_canton(cases, 'QUITO', 'RURAL', hm='Normal')
plt.savefig('casos_quito_rur_norm.png', bbox_inches='tight')