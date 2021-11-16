import pandas as pd
import numpy as np
import time
from datetime import datetime
from scipy.stats import variation
from pandas.api.types import is_datetime64_any_dtype as is_datetime

import csv
import os     # set the working directory
import glob   # 

# user input
address=input("Folder location for data tables (*.csv):")
os.chdir(address)

# Get all file names
all_filenames = [i for i in glob.glob(f"*.csv")]
#print(all_filenames)

#--------------------------->>> preparation: identify event tables and non-event tables <<<--------------------------
get_c=[]
for file in all_filenames:
    df=pd.read_csv(file,nrows=10000, low_memory=False)
    is_time_format = df.astype(str).apply(lambda x : x.str.match(r'\d{4}-\d{2}-\d{2} \d{2}\:\d{2}\:\d{2}').all())
    #is_time_format = df.astype(str).apply(lambda x : x.str.match(r'\d{4}-\d{2}-\d{2}').all())
    #df.loc[:,mask] = df.loc[:,mask].apply(pd.to_datetime,errors='coerce')
    
    df.loc[:,is_time_format] = df.loc[:,is_time_format].apply(pd.to_datetime)
    is_time_columns = df.select_dtypes(include='datetime') # is_time_columns =[] or ['time']
    if not is_time_columns.empty:
        for c in is_time_columns.columns:
            c_max=is_time_columns[c].astype(str).str.len().max()
            get_c.append(c_max)
get_max=max(get_c)

#--->>> output: dict={'filename':[time columns]}
event_table=[]
non_event_table=[]
time_cols=[]
time_cols_dict={}

for file in all_filenames:
    df=pd.read_csv(file,nrows=50000, low_memory=False)
    #print(file)
    target_type = df.select_dtypes(include = ['object','datetime']) # target type
    temp_timecols=[]
    #-------------- Method 1 GET Time COlumns
    for column in target_type:
        col_max=df[column].astype(str).str.len().max()
        test=df[~df[column].isnull()] 
        test1=test[column]
        col_min=test1.astype(str).str.len().min()
    #        print(column,"->",col_min,'~',col_max)
        gap=col_max-col_min
    #        x=df.apply(lambda x: len(x.unique()))
        #check=len(df[column].unique())

        if (col_max==get_max or col_min ==get_max) and (gap==0 and column!='DOB'): # we can set different threshold based on the given data
            #print('Potential time column:',column,"->",col_min,'~',col_max,'numbers of unique values:',check)
            temp_timecols.append(column)
            time_cols.append(column)
    #------------------------     Method 2 GET    
    is_time_format = df.astype(str).apply(lambda x : x.str.match(r'\d{2,4}-\d{2}-\d{2,4} \d{2}\:\d{2}\:\d{2}').all()) # mask
    #is_time_format = df.astype(str).apply(lambda x : x.str.match(r'\d{4}-\d{2}-\d{2}').all())
    df.loc[:,is_time_format] = df.loc[:,is_time_format].apply(pd.to_datetime)
    is_time_columns = df.select_dtypes(include='datetime') # is_time_columns =[] or ['time']
    # remove DOB
    temp_cols=list(is_time_columns.columns)
    for i in temp_cols:
        if i=='DOB':
            temp_cols.remove('DOB')
    # --- >> criteria: length of datatime in the given datatable & exlude Date of Birth
    temp_timecols.extend(temp_cols)
    temp_timecols0=list(set(temp_timecols))
    if temp_timecols!=[]:
        time_cols_dict[file]=temp_timecols0    # ------------------------------------->>> get time columns    
        event_table.append(file)               # ------------------------------------->>> get event tables
    else:
        non_event_table.append(file)           # ------------------------------------->>> get non-event tables

print('Event tables are:')
print(event_table)
print()
print('Non-event tables are:')
print(non_event_table)
print()
print('Time columns dictionary:',time_cols_dict)



# >>> timestamp columns in event data tables
timestamp_list=list(set(time_cols))
print('Timestamp list:',timestamp_list)        # ------------------------------------->>> get time column list (unique element)


# ------------------------------  Case ID Identification -------------------------
# Primary Keys in non-event data tables
sug_pm_keys=[]
for file in non_event_table:
    df=pd.read_csv(file, low_memory=False)
    ob_type = df.select_dtypes(include = ['integer','object'])
    row_count=len(df.index)
    temp_count_list=[]
    temp_colList=[]
    for col in ob_type:
        check=len(df[col].unique())
        temp_count_list.append(check)
        temp_colList.append(col)
    loc=temp_count_list.index(max(temp_count_list))
        
    sug_pm_keys.append(temp_colList[loc])
    #print(file,'/',temp_colList[loc],max(temp_count_list))
print('Suggested primary keys from non-event tables:')
print(sug_pm_keys)  # ------------------------------------->>> get suggest primary keys

# ----------------Basic Strategies for Case ID Identification----------------------

no_null_col=[]
new_test=[] # for new strategy
sug_caseID=[]
caseID=[]

for file in event_table: # ----------------->  Strategy I3: in a table containing time column
    df=pd.read_csv(file,nrows=10000, low_memory=False)
    #----------------------------------------------------------------------------> Strategy: I1
#    ob_int_type = df.select_dtypes(include = ['object','integer'])  
    ob_int_type = df.select_dtypes(include = ['integer'])  #-------> Strategy: I1

    # ---------------------------------------------------------------------------> Strategy: I2
    null_count=df.isnull().sum()
    null_list=np.array(null_count).tolist()
    # transfer to dataframe to create I2
    df_nullcount = pd.DataFrame(list(zip(ob_int_type,null_list)))
    df_nullcount.columns=['Column Name','x']
    filter_null=df_nullcount[df_nullcount['x']<10]
    no_null_cols=df_nullcount['Column Name'].tolist()    # Strategy:I2 --->> No blank in any row 
    
    # Obtain the length of cells in columns
    for column in ob_int_type:
        col_max=df[column].astype(str).str.len().max()
        col_min=df[column].astype(str).str.len().min()
#        print(column,"->",col_min,'~',col_max)
        gap=col_max-col_min
        check=len(df[column].unique())
        
        if col_max>1 and gap==0: # we can set different threshold   # -----------------------new Strategy
            if column not in timestamp_list: # --->> not timestamp
                caseID.append(column)
                #print('Potential Case ID:',column,"->",col_min,'~',col_max,'numbers of unique values:',check) 

# obtain Potential CaseIDs                
sug_caseID=list(dict.fromkeys(caseID))                              # ------------------------------------->>> get suggest case ID list
print('Suggested case ID list:', sug_caseID)

# -------------  Strategy: not a pm key in non-event data tables 
caseID = [element for element in sug_caseID if element not in sug_pm_keys] # ------------------------------------->>> get case ID list
print('Case IDs are:')
print(caseID)
print()

# Create case ID dictionary
file_caseID_dict={}
for file in event_table: 
    df=pd.read_csv(file,nrows=1000)
    caseID_col=[]
    for col in df.columns:
        if col in caseID:
            caseID_col.append(col)
    file_caseID_dict[file]=caseID_col

print(file_caseID_dict)
print()
# event data: case ID and timestamps
event_data=caseID+timestamp_list                                           # ------------------------------------->>> get event data list (case ID + timestampe)

# <<<<<<<<<<<<<<<<<<<<<----------------------------------- Enumerate Case ID sets for generic processes ----------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Define a dictionary to contain caseID data frames
genericProcess={}  # dictionary for all generic processes {processName:[caseID,all time columns]}
caseIDset={}       # dictionary for all case ID sets for generic processes {processName:caseID,duration,year|}
g_processName=[]
indices=[] # trend line of 6 cvs

# output ---> genericProcess={'fileName+caseID':[caseID dataframe]} ['caseID']
#create a new dataframe for each caseID set

g_count=0 # count the total amount of generic processes
for file in event_table: 
    df=pd.read_csv(file,nrows=50000, low_memory=False)  # dataframe from an event table
    timestamp_list=time_cols_dict[file] # get time columns in one file/table

    file_caseID_dict[file] # get case IDs in the table
    for name in file_caseID_dict[file]:
        
        # build caseID dataframe in a dictionary
        g_count+=1
        g_processName=file.replace('.csv', '')+'/'+name # process name = file name + caseID name
#        print(g_processName)
        genericProcess[g_processName]=pd.DataFrame(columns=['caseID']) # assign process name as dict index
        genericProcess[g_processName].caseID=df[name].to_list()  #----------------------------GET case ID sets and names for generic process
#            genericProcess[name][test[0]]=df[test[0]].to_list() # test ['timea','timeb']

        #--------------- Get all time columns ------------------
        var_tcol=timestamp_list
        for i in timestamp_list:
            testTimeCol=pd.to_datetime(df[i])
            genericProcess[g_processName][i]=testTimeCol.to_list()

        #--------------- Transform and calculate Min and Max by case ID -------------------------- 
        temp_df=genericProcess[g_processName]
        unique_caseID=temp_df['caseID'].unique()
#        print('check rows in generic process dataframe: ',len(temp_df.index),'|unique case ID number is:',len(unique_caseID))
#            print(temp_df.dtypes)
        id_vars=['caseID']      
        df1 = (temp_df.melt(id_vars=['caseID'], value_vars=var_tcol)
             .groupby(id_vars)['value']
             .agg(['min', 'max']))                       
        caseID_group= df1.groupby('caseID').aggregate({'min':'min', 'max':'max'}) # transform to new dataframe 
        duration0 =caseID_group['max']-caseID_group['min'] # --->>> Key step: Duration Calculation
        duration=duration0.astype('timedelta64[s]') # transfer to floate
        caseID_group['duration']=duration.to_list()
        caseID_group[caseID_group['duration'].astype(bool)]  # --->>> remove empty rows
        #caseID_group=caseID_group[caseID_group.duration != 0]
        #print('The duration mean:',duration.mean())
        # --------------- Get Year for each case
        caseID_group['max']=pd.to_datetime(caseID_group['max'],format='%Y-%m-%d')
        caseID_group['Year']=pd.DatetimeIndex(caseID_group['max']).year # if aggregate yearly data
        caseID_group['Month_Year']=pd.to_datetime(caseID_group['max']).dt.to_period('M') # if aggregate monthly data
        #caseID_group['Period']=caseID_group['Month_Year']
        caseID_group['Period']=caseID_group['Year']
        caseIDset[g_processName]=caseID_group # ------------------------------------------------------>>>> GET new dataframe |caseID|Duration|year|
        
        
        
        #print(caseID_group['Year'])
        # ----------------Get CVs for recent 6 years or months --------
        #max_value = caseID_group['Year'].max() # if real time, it should be current week/month/year
        sort_period=caseID_group['Period'].sort_values(ascending=False)
        unique_p=sort_period.unique()
        #print(unique_p)

        print('length of the period (years):',len(unique_p))
        print('Number of rows in dataframe: ',len(caseID_group.index))
        if len(unique_p)>=10: # sample size > 30 
            unique_p=[2200,2199,2198,2197,2196,2195] # testing - override
            p1=unique_p[0] # period 1
            p2=unique_p[1]
            p3=unique_p[2]
            p4=unique_p[3]
            p5=unique_p[4]
            p6=unique_p[5]
            #print('6 periods:',unique_p[0],unique_p[1],unique_p[2],unique_p[3],unique_p[4],unique_p[5])

            p1_duration=duration[caseID_group['Period']==p1]
            p2_duration=duration[caseID_group['Period']==p2]
            p3_duration=duration[caseID_group['Period']==p3]
            p4_duration=duration[caseID_group['Period']==p4]
            p5_duration=duration[caseID_group['Period']==p5]
            p6_duration=duration[caseID_group['Period']==p6]
            # two checking points
            case_count=[len(p1_duration),len(p2_duration),len(p3_duration),len(p4_duration),len(p5_duration),len(p6_duration)]
            print('case count:',case_count, '| Min~Max:',min(case_count),'~',max(case_count))

            check_divisor=[float("{:.3f}".format(p1_duration.mean())),p2_duration.mean(),p3_duration.mean(),p4_duration.mean(),p5_duration.mean(),p6_duration.mean()]
            #print('Check base:', check_divisor)

            if ((min(check_divisor)>0) and (min(case_count)>=3)):
                cv1 = p1_duration.std()/p1_duration.mean()  # Period 1 - most recent
                cv2 = p2_duration.std()/p2_duration.mean()  # Period 2
                cv3 = p3_duration.std()/p3_duration.mean()  # Period 3
                cv4 = p4_duration.std()/p4_duration.mean()  # Period 4
                cv5 = p5_duration.std()/p5_duration.mean()  # Period 5
                cv6 = p6_duration.std()/p6_duration.mean()  # Period 6
                # calculate the slop of single linear regression
                x = np.array([1,2,3,4,5,6]) # x represents years
                y = np.array([cv6,cv5,cv4,cv3,cv2,cv1]) # y represents CV in each year
                n = np.size(x)

                x_mean = np.mean(x)
                y_mean = np.mean(y)
                Sxy = np.sum(x*y)- n*x_mean*y_mean
                Sxx = np.sum(x*x)-n*x_mean*x_mean

                slope = float("{:.3f}".format(Sxy/Sxx)) # --------->>> GET process performance index for one process based on recent 6-year period
                #b0 = y_mean-slope*x_mean
            else:
                slope=-900 # one of divisor = 0 and case number <3
        else:
            #slope = 'not calculated due to inadequate data'
            slope=-999 # sample size is less than 30
        indices.append(slope)                           #-------------------------- GET a list of process index

print('Process index:', indices)
calculable=[x for x in indices if (x!=-900 and x!=-999)]
rate0=len(calculable)/g_count
print('The total amount of processes detected:',g_count,'|',len(calculable),'are calculable (', "{:.0%}".format(rate0),')')
print()
#print('Case ID sets for generic processes are:')
#print(genericProcess)
#print('The total amount of case ID sets for generic processes',g_count)

#---------------------------------- Specialisation Process -------------------------------------    

#  ----->>> 1. Process Identifier for the specialisations of processes

# Specialisation Identifier
# rule:  	 'object' type & not event data

identifier_list=[]
spec_idfier_dict={}

for file in event_table:
    df=pd.read_csv(file,nrows=100000, low_memory=False)
    object_columns=df.select_dtypes(include='object') # -----------------------------------   select identifier   
    identifiers=[] # only a list of identifiers for one file
    element = [element for element in object_columns if 'UOM' in element]  # a list of UOM columns
    for i in object_columns:
        if i not in event_data + element:   # ------------------------------------------------------>>> strategy
            identifiers.append(i)
            identifier_list.append(i)
#    print(identifier_list)
    spec_idfier_dict[file]=identifiers
print('Total number of specialisation identifiers obtained:',len(identifier_list))
#print('Identifier dictionary:')
#print(spec_idfier_dict) 
print()

# ----->>> 2. Obtain values in specialisation identifiers
#identifiers >> identifier_sets

identifier_sets={}
num_value_element=0
for file in event_table:
    df=pd.read_csv(file,nrows=10000)
    x=[]
    identi_value_dict={}
    for col in spec_idfier_dict[file]:
        x=[col]
        value=df[col].unique()
        idfier_value=value.tolist()
        x.append(idfier_value)
        remove_null= [item for item in idfier_value if not(pd.isnull(item))==True]  # aim to remove "nan" from identifier list
        num_value_element+=len(remove_null) # calculate number of values that will be used to enumeration the specialisations of processes
        identi_value_dict[col]=remove_null
    identifier_sets[file]=identi_value_dict
    
print('Total amount of values for identifiers:',num_value_element)
print()
#print('The identifiers in each table:')
#print(identifier_sets)

#------->>> 3.Enumerate Case ID sets for specialised processes -----------------
# obtain subsets of case ID based on specialisation identifier
# output ---> specialProcess={'fileName+caseID':[caseID dataframe]} 
# create a new dataframe for each caseID set

#s_Process={} # dictionary for all specialised processes
caseIDsubset={}   # deictionary for case ID sets for specialised processes
s_ProcessName=[] # a list of name for each process
s_indices=[] # trend line of 6 cvs
s_count=0 # count the total amount of specialised processes

for file in event_table:
    df=pd.read_csv(file,nrows=50000, low_memory=False)
    
    caseIDnames=file_caseID_dict[file]
    for caseID in caseIDnames:
        caseIDset_name=file.replace('.csv', '')+'/'+caseID # generic process name = file name + caseID name
        caseIDset0=caseIDset[caseIDset_name] # get the data frame from the extracted caseID duration dataframe
        caseIDset0=caseIDset0.reset_index()
    
        identifiers=identifier_sets[file]
        for i in identifiers:
            for value in identifiers[i]:
                filter = df[df[i]==value]
                subset = filter[caseID]  # obtain subset case ID based on filter 'value'
                subset_list=subset.to_list() # -> list for filter
                caseID_group=caseIDset0.loc[caseIDset0['caseID'].isin(subset_list)] #matching case ID to get the subset

                #tempName = all_filenames[0].replace('.csv', '')+'/' + caseID+'//'+i+'///'+value
                tempName = caseIDset_name+'//'+i+'///'+value
                caseIDsubset[tempName]= caseID_group
                s_ProcessName.append(tempName)  #----------------------------->>> portfolio

                # ----------------Get CVs for recent 6 years or months --------
                duration=caseID_group['duration'] # duration not based on calculation, but from caseID_group
                    
                max_value = caseID_group['Period'].max() # if real time, it should be current week/month/year
                sort_period=caseID_group['Period'].sort_values(ascending=False)
                unique_p=sort_period.unique()
        
                if len(unique_p)>=30: # sample size >=30, according to Central Limit Theorem
                    unique_p=[2200,2199,2198,2197,2196,2195] # testing - override
                    p1=unique_p[0] # period 1
                    p2=unique_p[1]
                    p3=unique_p[2]
                    p4=unique_p[3]
                    p5=unique_p[4]
                    p6=unique_p[5]
                    #print('6 periods:',unique_p[0],unique_p[1],unique_p[2],unique_p[3],unique_p[4],unique_p[5])

                    p1_duration=duration[caseID_group['Period']==p1]
                    p2_duration=duration[caseID_group['Period']==p2]
                    p3_duration=duration[caseID_group['Period']==p3]
                    p4_duration=duration[caseID_group['Period']==p4]
                    p5_duration=duration[caseID_group['Period']==p5]
                    p6_duration=duration[caseID_group['Period']==p6]
                    # two checking points
                    case_count=[len(p1_duration),len(p2_duration),len(p3_duration),len(p4_duration),len(p5_duration),len(p6_duration)]
                    #print('case count:',case_count, '| Min~Max:',min(case_count),'~',max(case_count))
                    check_divisor=[float("{:.3f}".format(p1_duration.mean())),p2_duration.mean(),p3_duration.mean(),p4_duration.mean(),p5_duration.mean(),p6_duration.mean()]
                    
                    if ((min(check_divisor)>0) and (min(case_count)>=3)):
                        cv1 = p1_duration.std()/p1_duration.mean()  # Period 1 - most recent
                        cv2 = p2_duration.std()/p2_duration.mean()  # Period 2
                        cv3 = p3_duration.std()/p3_duration.mean()  # Period 3
                        cv4 = p4_duration.std()/p4_duration.mean()  # Period 4
                        cv5 = p5_duration.std()/p5_duration.mean()  # Period 5
                        cv6 = p6_duration.std()/p6_duration.mean()  # Period 6
                        # calculate the slop of single linear regression
                        x = np.array([1,2,3,4,5,6]) # x represents years
                        y = np.array([cv6,cv5,cv4,cv3,cv2,cv1]) # y represents CV in each year
                        n = np.size(x)

                        x_mean = np.mean(x)
                        y_mean = np.mean(y)
                        
                        Sxy = np.sum(x*y)- n*x_mean*y_mean
                        Sxx = np.sum(x*x)-n*x_mean*x_mean

                        slope = float("{:.3f}".format(Sxy/Sxx)) # process performance index for one process based on recent 6-year period
                        b0 = y_mean-slope*x_mean
                    else:
                        slope=-900
                    #print('Slope for this process in recent 6 years: ', slope)
                else:
                    #slope = 'not calculated due to inadequate data'
                    slope=-999 # sample size <30
                    b0 = 'not calculated due to inadequate data'

                s_indices.append(slope)

#print(caseIDsubset) 
cal=[x for x in s_indices if (x!=-900 and x!=-999)]
rate1=len(cal)/len(s_ProcessName)
print('The total amount of processes detected:',len(s_ProcessName),'|',len(cal),'are calculable (', "{:.0%}".format(rate1),')')
print()

#---------------------------------------PROCESS PORTFOLIO --------------------------------------------------------
portfolio = pd.DataFrame()
portfolio['processName']=genericProcess.keys()
portfolio['processIndex'] = indices
portfolio['processType']='Generic Process'

sub_portfolio = pd.DataFrame(s_ProcessName, columns=['processName'])
sub_portfolio['processIndex'] = s_indices
sub_portfolio['processType']='Specialisation'

total=portfolio.append(sub_portfolio)
totalProcessNum=len(genericProcess)+len(s_ProcessName)

print(len(genericProcess)+len(s_ProcessName),' processes are detected.')
x=total.sort_values(by=['processIndex'],ascending=False)
print(x.head(60))