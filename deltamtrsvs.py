#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com *
    Each function is intended to encapsulate one & only one API end-point.
    Args:
        Each function takes at minimum; an API URL, headers and either a list
        of object IDs, or a dictionary of objects with IDs as keys
    Returns:
        Each function will return a single data structure containing objects
        and IDs; typically a dictionary with IDs as keys """

import requests


def get_property_bldgs(properties_url, site, headers):
    """ Pass an API URL, property ID; return a list of building IDs for the
        property """
    
    bldgIDct = {}

    properties_endpt = properties_url + site
    bldgs = requests.get(properties_endpt, headers=headers).json()
    for bldg in bldgs:
        bldgIDct[bldg['BuildingID']] = bldg

    return bldgIDct

def get_bldg_models(model_url, bldgIDs, headers):
    """ Pass a list of building IDs; return a list of building IDs for
        which valid data is available, and the data in .JSON format. """

    modelsJsonDct = {}
    valBldgIDs = []
    for bldgID in bldgIDs:
        model_endpt = model_url + bldgID
        models = requests.get(model_endpt, headers=headers)
        if requests.get(model_endpt, headers=headers):
                modelsJsonDct[bldgID] = models.json()

    return modelsJsonDct 


def get_model_comparisons(comparison_url, modelsJsonDct, headers):
    """ Pass a list of models' data in .JSON format, return model IDs &
        comparisons's data in .JSON format """
    # TODO (eayoungs): Create a new function for this code block to be called
    #                  seperately; pass only modelIDs to this function
    json_models = []
    for key, value in modelsJsonDct.iteritems():
        json_models.append(value)
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
    # TODO (eayoungs): Revise function to return a single object
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

def get_bldg_meters(bldg_meters_url, bldgIDs, headers):
    """ """
    bldgMeterDct = {}
    bldgMetersList = []
    for bldgID in bldgIDs:
        bldg_meter_url = bldg_meters_url + bldgID
        bldgMeters = requests.get(bldg_meter_url, headers=headers)
        jsonBldgMeters = bldgMeters.json()
        bldgMeterDct[bldgID] = jsonBldgMeters
        bldgMetersList.append(bldgMeterDct)

    return bldgMetersList

def get_energy_rates(bldgMetersList, auditSpans, meter_records_url,
                         headers):
    """ Takes the dictionary of date ranges from amsaves_usage_range function
        and building meter IDs from get_building_meters function returns
        energy cost rate for both (electric & gas) common fuels"""

    i = 0
    for key, value in auditSpans.iteritems():
        elecBegin = auditSpans[key]['E. Per. Begin']
        elecEnd = auditSpans[key]['E. Per. End']
        gasBegin = auditSpans[key]['G. Per. Begin']
        gasEnd = auditSpans[key]['G. Per. End']
        meterID = bldgMetersList[i]
        elecMeter_record_url = pvt.meter_records_url + meterID + \
                               '?start=' + elecBegin + '&end=' + elecEnd
        elecMeterRecords = requests.get(meter_record_url, headers=headers)
        gasMeter_record_url = pvt.meter_records_url + meterID + \
                              '?start=' + gasBegin + '&end=' + gasEnd
        gasMeterRecords = requests.get(meter_record_url, headers=headers)
        i=i+1
