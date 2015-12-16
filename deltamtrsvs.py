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
        which there valid data is available, and the data in .JSON format. """

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
    """ Pass a list of models' data in .JSON fortmat, return model IDs &
        comparisons's data in .JSON format """

    modelIDs =[]
    for i in range(0, len(json_models)):
        for j in range(0, len(json_models[i])):
                modelID = str(json_models[i][j]['SolutionID'])
                modelIDs.append(modelID)

    comparisons =[]
    for i in range(0, len(modelIDs)-1, 2):
        comparison_endpt = comparison_url + modelIDs[i] + '/1/' + \
                           modelIDs[i+1] + '/1/'
        comparison = requests.get(comparison_endpt, headers=headers)
        comparisons.append(comparison)

    return (modelIDs, comparisons)
