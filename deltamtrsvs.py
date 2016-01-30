#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
        Services API * deltameterservices.com * """


import requests


def get_property_bldg_IDs(properties_url, site, headers):
    """ Pass an API URL, property ID; return a list of building IDs for the property """

    properties_endpt = properties_url + site
    bldgs = requests.get(properties_endpt, headers=headers).json()
    bldgIDs = [str(bldg['BuildingID']) for bldg in bldgs]

    return bldgIDs

def get_bldg_models(model_url, bldgIDs, headers):
    """ Pass a list of building IDs; return a list of building IDs for
        which valid data is available, and the data in .JSON format. """

    json_models = []
    valBldgIDs = []
    for bldgID in bldgIDs:
        model_endpt = model_url + bldgID
        models = requests.get(model_endpt, headers=headers)
        if requests.get(model_endpt, headers=headers):
                json_models.append(models.json())
                valBldgIDs.append(str(bldgID))

    return (json_models, valBldgIDs)

def get_model_comparisons(comparison_url, json_models, headers):
    """ Pass a list of models' data in .JSON format, return model IDs &
        comparisons's data in .JSON format """
    # TODO (eayoungs): Create a new function for this code block to be called
    #                  seperately; pass only modelIDs to this function
    bldgDct = {}
    jModDct = {}
    for i in range(0, len(json_models)):
        modelDct = {}
        for j in range(0, len(json_models[i])):
            bldgID = json_models[i][j]['BuildingID']
            modelID = str(json_models[i][j]['SolutionID'])
            modelDesc = json_models[i][j]['SolutionType']
            # TODO (eayoungs): Add error handling here: Else, cond not found
            if 'Reference Model' in modelDesc:
                modelType = 'Reference Model'
            elif 'Proposed Model' in modelDesc:
                modelType = 'Proposed Model'
            modelDct[modelType] = modelID
        bldgDct[bldgID] = modelDct
        jModDct[bldgID] = json_models[i]

    modelIDs = []
    compDct = {}
    for key, value in bldgDct.items():
        refModel = bldgDct[key]['Reference Model']
        propModel = bldgDct[key]['Proposed Model']
        comparison_endpt = comparison_url + refModel +'/1/' + propModel + '/1/'
        # TODO (eayoungs): Add error msgs. & exception handling to account for
        # invalid comparisons
        comparison = requests.get(comparison_endpt, headers=headers)
        compDct[key] = comparison

        modelIDs.append(refModel)
        modelIDs.append(propModel)

    return (modelIDs, compDct, jModDct)

def get_model_audits(audit_url, modelIDs, headers):
    """ Pass a list of model IDs; return audit IDs and a list of audit data
        objects in .JSON format. """
    # TODO (eayoungs): Create a more explicit selection process to select
    #                  models by type (ie 'Reference', or 'Proposed').
    refModelIDs = modelIDs[::2]

    audits = []
    for refModelID in refModelIDs:
        audit_endpt = audit_url + refModelID
        audits.append(requests.get(audit_endpt, headers=headers))

    return (refModelIDs, audits)

def get_fv_charts(fv_charts_url, bldgIDs, headers):
    """ Pass a URL, a list of building ID's and required API header; return a
        list of FirstView chart objects """

    fvCharts = []

    for bldgID in bldgIDs:
        fv_chart_url = fv_charts_url + bldgID
        fvChart = requests.get(fv_chart_url, headers=headers)
        jsonFvChart = fvChart.json()
        fvCharts.append(jsonFvChart)

    return fvCharts
