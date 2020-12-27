def average_influenza_doses():
    # YOUR CODE HERE
    # raise NotImplementedError()
    import pandas as pd
    import numpy as np
    df = pd.read_csv("assests/NISPUF17.csv", index_col=0)
    
    cbf_flu=df.loc[:,['CBF_01','P_NUMFLU']]
    
    
    cbf_flu1=cbf_flu[cbf_flu['CBF_01'] ==1].dropna()
    cbf_flu2=cbf_flu[cbf_flu['CBF_01'] ==2].dropna()
    
    flu1=cbf_flu1['P_NUMFLU'].values.copy()
    flu1[np.isnan(flu1)] = 0
    f1=np.sum(flu1)/len(flu1)
    
    flu2=cbf_flu2['P_NUMFLU'].values.copy()
    flu2[np.isnan(flu2)] = 0
    f2=np.sum(flu2)/len(flu2)
    
    aid =(f1,f2)
    return aid