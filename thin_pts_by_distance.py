# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 10:06:03 2018

filter input points to min sequential x,y spacing using KDtree

@author: jlogan
"""

import pandas as pd
from scipy import spatial
#from tqdm import tqdm

#inpointfile = 'D:\\jloganPython\\dem-validation\\data\\batch\\ob\\val_pts\\2018_03_14\\2018-0314-OB_ne_elht_NAD83_CORS96.csv'
#thinnedoutfile = 'D:\\jloganPython\\dem-validation\\data\\batch\\ob\\val_pts\\2018_03_14\\2018-0314-OB_ne_elht_NAD83_CORS96_hlfmeterThinned_kdtree.csv'

#inpointfile = 'D:\\jloganPython\\dem-validation\\data\\batch\\ob\\val_pts\\Data to Andy for SfM comparison\\Final points\\OB20180307finalPtsWithExtraColsQ1Only.xlsx'
#thinnedoutfile = 'D:\\jloganPython\\dem-validation\\data\\batch\\ob\\val_pts\\2017-0307-OB_ne_elht_NAD83_CORS96_hlfmeterThinned_kdtree_test.csv'

#Wildlands 2018-11-29
inpointfile = r"T:\UAS\2018-676-FA\validation\topo\wld17_06.txt"
thinnedoutfile = r"T:\UAS\2018-676-FA\validation\topo\wld17_06_KDthinned10cm.txt"
xcol_name = 'Easting'
ycol_name = 'Northing'

mindist = 0.1

def col_lower_case(df):
    outdf = df.copy(deep=True)
    outdf.columns = outdf.columns.str.lower()
    return outdf

def main(inpointfile, thinnedoutfile):
    #df = pd.read_excel(inpointfile)
    df = pd.read_csv(inpointfile)
    #df = col_lower_case(df)
    #df.rename(columns={'northing': 'n', 'easting': 'e', 'ellip_heig':'z'}, inplace=True)
    
    #run filter 
    outdf, ptsremoved = filter_pts_by_distance(df, mindist, xcol_name, ycol_name)
    
    #export
    outdf.to_csv(thinnedoutfile, index=False, float_format='%0.3f')
    
    print('Number of points removed with min. distance ' + str(mindist) + ': ' + str(ptsremoved))
    
    return 

def filter_pts_by_distance(df, mindist, xcol, ycol):
    """
    Filters input df by distance using kdtree
    args:
        df: dataframe
        mindist: minimum euclidean dist between points
        xcol: str name of xcolumn in df
        ycol: str name of ycolumn in df
    
    returns:
        outdf: filtered dataframe
        ptsremoved: number of points removed from input df
    """
    
    #make copy of df and make static index
    outdf = df.copy(deep=True)
    outdf = outdf.reset_index()
    outdf.rename(columns={'index': 'static_index'}, inplace=True)
    
    #get input df len
    len1 = len(df)
    
    #create set to store indices of removed points
    remset = set()
    
    #build kdtree on easting, northing
    tree =spatial.KDTree(list(zip(df[xcol],df[ycol])))
    
    #with tqdm(total=len(list(df.iterrows()))) as pbar:
        
    for index, row in df.iterrows():
        # if index not already dropped from dataframe, then look for points within dist
        if not index in remset:
            #query tree, just return list [0]
            #nearlist = tree.query_ball_point(df.loc[[index],['e','n']], mindist)[0]
            nearset = set(tree.query_ball_point(df.loc[[index],[xcol_name,ycol_name]], mindist)[0])
            #remove self
            #nearlist = [i for i in nearlist if i != index]
            nearset = nearset-{index}
            #remove points that have already been dropped
            nearset = nearset - remset
            
            #drop rows (using index)
            #outdf.drop(outdf.index[list(nearset)],inplace=True)
            outdf.drop(outdf.static_index[list(nearset)], inplace=True)
            
            #add dropped items to remset
            remset = remset|nearset
        #pbar.update(index)
        print('\rPoint ' + str(index+1) + '/' + str(len1) + '.', end='')
    
    print('\n')
    #remove static index        
    outdf.drop(['static_index'], axis=1, inplace=True)
    
    ptsremoved = len(df) - len(outdf)
       
    return outdf, ptsremoved
 
if __name__ == '__main__':
    # if called directly as script, execute main.
    main(inpointfile, thinnedoutfile)
