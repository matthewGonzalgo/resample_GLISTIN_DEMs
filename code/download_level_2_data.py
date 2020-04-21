# Copyright 2020, by the California Institute of Technology.
# ALL RIGHTS RESERVED. United States Government Sponsorship acknowledged.
# Any commercial use must be negotiated with the Office of Technology Transfer at the California Institute of Technology.
# This software may be subject to U.S. export control laws.
# By accepting this software, the user agrees to comply with all applicable U.S. export laws and regulations.
# User has the responsibility to obtain export licenses, or other export authority as may be required before exporting
# such information to foreign countries or providing access to foreign persons.

# Codes last tested 05 April 2020 by MW and IF

import os
import numpy as np
import requests
import argparse
import swath_references as ref



def createDirectoryStructure(dataFolder,years):

    if 'Raw' not in os.listdir(dataFolder):
        os.mkdir(os.path.join(dataFolder,'Raw'))

    for year in years:
        if str(year) not in os.listdir(os.path.join(dataFolder,'Raw')):
            os.mkdir(os.path.join(dataFolder,'Raw',str(year)))
        if 'Data' not in os.listdir(os.path.join(dataFolder,'Raw',str(year))):
            os.mkdir(os.path.join(dataFolder,'Raw',str(year),'Data'))
        if 'Metadata' not in os.listdir(os.path.join(dataFolder,'Raw',str(year))):
            os.mkdir(os.path.join(dataFolder,'Raw',str(year),'Metadata'))

def generateDownloadLinks(swathIndices,yearList):
    dataDownloadLinks=[]
    metadataDownloadLinks=[]
    years=[]
    swathIDs=[]
    for index in swathIndices:
        for year in yearList:
            if year==2016 and index in ref.swathIndicesMissingIn2016():
                print('Note: Swath index ' + str(index) + ' is not available in 2016')
            else:
                fileID = ref.indexAndYearToFileID(index, year)
                years.append(year)
                swathID = ref.fileNameToSwathID(fileID)
                swathIDs.append(swathID)
                dataLink = ref.swathIDtoDataLink(swathID)
                metadatalink = ref.swathIDtoMetadataLink(swathID)
                dataDownloadLinks.append(dataLink)
                metadataDownloadLinks.append(metadatalink)

    return(dataDownloadLinks,metadataDownloadLinks,years,swathIDs)

def downloadDataGrid(dataFolder,year,swathID,downloadLink):
    outputFile = os.path.join(dataFolder,'Raw',str(year),'Data',swathID+'.hgt.grd')
    with requests.get(downloadLink, stream=True) as r:
        r.raise_for_status()
        with open(outputFile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def downloadMetadataFile(dataFolder,year,swathID,downloadLink):
    outputFile = os.path.join(dataFolder, 'Raw', str(year), 'Metadata', swathID + '_metadata.txt')
    r = requests.get(downloadLink)
    txt = r.text
    f=open(outputFile,'w')
    f.write(txt)
    f.close()

def downloadDataSet(dataFolder,swathIndices,years):
    print('Running download_level_2_data with the following parameters:')
    print('    dataFolder (-d)')
    print('        ' + dataFolder)
    print('    swathIndices (-i)')
    if len(swathIndices) == 81:
        print('        1-81 (Default: 1-81)')
    else:
        print('        ' + str(swathIndices)[1:-1] + ' (Default: 1-81)')
    print('    years (-y)')
    print('        ' + str(years)[1:-1] + ' (Default: 2016,2017,2018,2019)')

    createDirectoryStructure(dataFolder,years)

    dataLinks, metadataLinks, yearList, swathIDs = generateDownloadLinks(swathIndices,years)

    for dd in range(len(dataLinks)):
        print('Working on swath '+swathIDs[dd])
        print('    Downloading the data grid')
        downloadDataGrid(dataFolder,yearList[dd],swathIDs[dd],dataLinks[dd])
        print('    Downloading the metadata')
        downloadMetadataFile(dataFolder,yearList[dd],swathIDs[dd],metadataLinks[dd])

    print('Download Summary:')
    print('    Retrieved '+str(len(dataLinks))+' file(s)')
    print('    Files saved in '+dataFolder)
    print('    Requested years: '+str(years)[1:-1])
    print('    Requested indicies: '+str(swathIndices)[1:-1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #
    # Format for adding an argument:
    # parser.add_argument("-x", "--fullname", action="store", help="comment", default=default value, dest="variable_name",  type=datatype, required=T/F)
    #
    parser.add_argument("-d", "--dataFolder", action="store", help="(Required) Directory where data will be downloaded.", dest="dataFolder", type=str, required=True)

    parser.add_argument("-i", "--swathIndices", action="store",
                        help="(Optional) List of swath indices to download. See data availability map on github.com/NASA/glistin to choose indices of interest. "
                             "A value of -1 will choose all files. Default value is -1.", default=-1,
                        dest="swathIndices", type=int, nargs='+', required=False)

    parser.add_argument("-y", "--years", action="store", help="(Optional)  List of years to download. A value of -1 will choose all years (2016-2019 as available). "
                                                              "Default value is -1.", default=-1, dest="years", type=int, nargs='+',
                        required=False)

    args = parser.parse_args()

    dataFolder = args.dataFolder
    swathIndices = args.swathIndices
    years = args.years

    if swathIndices==-1 or -1 in swathIndices:
        swathIndices=np.arange(1,82)

    if years==-1 or -1 in years:
        years=[2016,2017,2018,2019]

    downloadDataSet(dataFolder,swathIndices,years)

