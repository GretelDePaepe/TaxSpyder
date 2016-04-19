# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 08:42:34 2016

@author: Gretel_MacAir
"""
# %% Import libs


from pyPdf import PdfFileReader
import re
import os
import pandas as pd

# %% Define Functions

# Reading the PDFs


def read_PDF(pdf):
    '''
    Grabs all the text of a pdf
    '''
    pdfOpen = open(pdf, "r")
    pdfRead = PdfFileReader(pdfOpen)
    pdfText = ''
    for page in pdfRead.pages:
        pdfText += page.extractText()
    return pdfText

# Scraping of the Property Tax Bill PDFs


def read_PTBtaxPDF(pdf):
    '''
    Parses following tax information from a Property Tax Bill (PTB) PDF:
    -previous charges
    -current charges
    -new charges
    -outstanding charges
    '''
    building = pdf[3:-4]
    pdfText = read_PDF(pdf)
    if pdfText[0:8] == 'Previous':
        previousCharges = pdfText.split(
            'Previous charges$')[1].split('Amount paid$')[0]
        previousCharges = float(re.sub(',', '', previousCharges))
        currentCharges = pdfText.split(
            'Current charges$')[1].split('Total amount due')[0]
        currentCharges = float(re.sub(',', '', currentCharges))
    else:
        previousCharges = 0.00
        currentCharges = 0.00
    if pdfText[0:6] == '001400':
        outstandingCharges = pdfText.split(
            'Outstanding Charges$')[1].split('New Charges$')[0]
        outstandingCharges = float(re.sub(',', '', outstandingCharges))
        newCharges = pdfText.split('New Charges$')[1].split('Amount Due$')[0]
        newCharges = float(re.sub(',', '', newCharges))
    else:
        outstandingCharges = 0.00
        newCharges = 0.00
    return building, previousCharges, currentCharges, outstandingCharges, newCharges


def get_PTBData():
    taxDict = {}
    buildingList = []
    previousChargesList = []
    currentChargesList = []
    outstandingChargesList = []
    newChargesList = []
    path = os.getcwd()
    for pdf in os.listdir(path):
        if pdf.startswith('PTB'):
            try:
                result = read_PTBtaxPDF(pdf)
                buildingList.append(result[0])
                previousChargesList.append(result[1])
                currentChargesList.append(result[2])
                outstandingChargesList.append(result[3])
                newChargesList.append(result[4])
            except:
                pass
    taxDict['building'] = buildingList
    taxDict['previousCharges'] = previousChargesList
    taxDict['currentCharges'] = currentChargesList
    taxDict['outstandingCharges'] = outstandingChargesList
    taxDict['newCharges'] = newChargesList
    taxDf = pd.DataFrame(taxDict)
    return taxDf


def cats_Start(pdfText):
    '''
    Arranges the categories in order they appear in the pdf
    '''
    try:
        startLast1 = pdfText.index('Factors Used By Finance')
    except:
        startLast1 = 99999999
    try:
        startLast2 = pdfText.index('Ifyoubelieve')
    except:
        startLast2 = 99999999
    catStartList = []
    cats = ['NumberofBuildings:',
            'GrossSquareFootage:',
            'NumberofStories:',
            'NumberofResidentialUnits:',
            'StructureType:',
            'GrossResidentialSquareFootage:',
            'Grade:',
            'NumberofCommercialUnits:',
            'ConstructionType:',
            'GrossCommercialSquareFootage:',
            'PrimaryZoning:',
            'YearBuilt:']
    for cat in cats:
        start = pdfText.index(cat)
        catStartList.append(start)
    cats.append('Factors Used By Finance')
    catStartList.append(startLast1)
    cats.append('Ifyoubelieve')
    catStartList.append(startLast2)
    return [cat for (st, cat) in sorted(zip(catStartList, cats))][:-1]

# Scraping of the New Property Value PDFs


def get_NPVData():
    '''
    Parses all the values for the categories in cats
    from the New Property Value PDFs for for all
    O4 (Office buildings) buildings
    '''
    path = os.getcwd()

    buildingDict = {}
    buildingList = []
    classList = []
    ownerList = []

    buildingListO = []
    NumberofBuildingsList = []
    GrossSquareFootageList = []
    NumberofStoriesList = []
    NumberofResidentialUnitsList = []
    StructureTypeList = []
    GrossResSquareFootageList = []
    GradeList = []
    NumberofCommercialUnitsList = []
    ConstructionTypeList = []
    GrossCommSquareFootageList = []
    PrimaryZoningList = []
    YearBuiltList = []

    catDict = {'building': buildingListO,
               'NumberofBuildings': NumberofBuildingsList,
               'GrossSquareFootage': GrossSquareFootageList,
               'NumberofStories': NumberofStoriesList,
               'NumberofResidentialUnits': NumberofResidentialUnitsList,
               'StructureType': StructureTypeList,
               'GrossResidentialSquareFootage': GrossResSquareFootageList,
               'Grade': GradeList,
               'NumberofCommercialUnits': NumberofCommercialUnitsList,
               'ConstructionType': ConstructionTypeList,
               'GrossCommercialSquareFootage': GrossCommSquareFootageList,
               'PrimaryZoning': PrimaryZoningList,
               'YearBuilt': YearBuiltList}

    for pdf in os.listdir(path):
        building = pdf[3:-4]
        if pdf.startswith('NPV'):
            try:
                pdfText = read_PDF(pdf)
                buildingClass = pdfText.split(
                    'BUILDING CLASS:')[1].split('UNITS:')[0]
                owner = pdfText.split(
                    'OWNER NAME')[1].split('PROPERTY ADDRESS')[0]
                classList.append(buildingClass)
                ownerList.append(owner)
                buildingList.append(building)
                cats = cats_Start(pdfText)
                type = ['  O4 (Office buildings)',
                         '  D4 (Elevator apartments)']
                cl = pdfText.split('BUILDING CLASS:')[1].split('UNITS:')[0]
                if cl in type:
                    catDict['building'].append(building)
                    for i in range(12):
                        cat = cats[i][:-1]
                        catValue = pdfText.split(
                            cats[i])[1].split(cats[i+1])[0]
                        catDict[cat].append(catValue)

            except:
                pass

            buildingDict['building'] = buildingList
            buildingDict['buildingClass'] = classList
            buildingDict['owner'] = ownerList
            buildingDf = pd.DataFrame(buildingDict)

            catDf = pd.DataFrame(catDict)
            NPV_Df = buildingDf.merge(catDf, on='building', how='left')
    return NPV_Df

# %%  Calls the main function


def main():
    PTB_Df = get_PTBData()
    NPVData = get_NPVData()
    data = PTB_Df.merge(NPVData, on='building', how='outer')
    writer = pd.ExcelWriter('NYC Tax scraping.xlsx')
    data.to_excel(writer, sheet_name='Data')
    writer.save()

if __name__ == "__main__":
    main()
