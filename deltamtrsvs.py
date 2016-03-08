#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@successionecological.com"
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
        bldgIDct[str(bldg['BuildingID'])] = bldg

    return bldgIDct


def get_bldg_models(model_url, bldgIDs, headers):
    """ Pass a list of building IDs; return a dictionary of with building IDs
        as keys and dictionaries containing model objects in .JSON format,
        having descriptive keys describing the model type contained within """ 

    bldgModelsDct = {}
    for bldgID in bldgIDs:
        model_endpt = model_url + bldgID
        models = requests.get(model_endpt, headers=headers)
        if requests.get(model_endpt, headers=headers):
            jsonModels = models.json()
            jsonModelsDct = {}
            for jsonModel in jsonModels:
                if 'Reference Model' in jsonModel['SolutionType']:
                    jsonModelsDct['Reference Model'] = jsonModel
                elif 'Proposed Model' in jsonModel['SolutionType']:
                    jsonModelsDct['Proposed Model'] = jsonModel
                else:
                    # TODO (eayoungs): Create & raise custom exception here
                    jsonModelsDct['Test'] = 'FAIL'
            bldgModelsDct[bldgID] = jsonModelsDct

    return bldgModelsDct


def get_model_comparisons(comparison_url, bldgModelsDct, headers):
    """ Pass a list of models' data in .JSON format, return model IDs &
        comparisons's data in .JSON format """

    modelIDs = []
    comparisonsDct = {}
    for key, value in bldgModelsDct.iteritems():
        jsonModelsDct = value
        refModel = str(jsonModelsDct['Reference Model']['SolutionID'])
        propModel = str(jsonModelsDct['Proposed Model']['SolutionID'])
        comparison_endpt = comparison_url + refModel +'/1/' + propModel + '/1/'
            # TODO (eayoungs): Add error msgs. & exception handling to account
            #                  for invalid comparisons
        comparison = requests.get(comparison_endpt, headers=headers)
        comparisonsDct[key] = comparison.json()

    return comparisonsDct 


def get_model_audits(audit_url, bldgModelsDct, headers):
    """ Pass a list of model IDs; return audit IDs and a list of audit data
        objects in .JSON format. """

    bldgModelsDct = {}
    for key, value in bldgModelsDct.iteritems():
        bldgID = key
        jsonModelsDct = value
        for key, value in jsonModelsDct.iteritems():
            bldgModelsDct[bldgID] = str(value['SolutionID'])

    audits = {}
    for key, value in bldgModelsDct:
        modelID = value
        audit_endpt = audit_url +modelID 
        audits[modelID] = requests.get(audit_endpt, headers=headers).json()
    # TODO (eayoungs): Revise function to return a single object

    return audits


def get_fv_charts(fv_charts_url, bldgIDs, headers):
    """ Pass a URL, a list of building ID's and required API header; return a
        list of FirstView chart objects """

    fvCharts = []
    for bldgID in bldgIDs:
        fv_chart_url = fv_charts_url + bldgID
        if requests.get(fv_chart_url, headers=headers):
            fvChart = requests.get(fv_chart_url, headers=headers)
            jsonFvChart = fvChart.json()
            fvCharts.append(jsonFvChart)

    return fvCharts


def get_bldg_meters(bldg_meters_url, bldgIDs, headers):
    """ Takes a list of building ID numbers; returns a dictionary with
        building IDs as keys and dictionaries of meter objects with the name
        of the fuel type (Electricity or Gas) as keys """

    meterReadingDct = {}
    bldgMeterDct = {}
    for bldgID in bldgIDs:
        bldg_meter_url = bldg_meters_url + bldgID
        bldgMeters = requests.get(bldg_meter_url, headers=headers)
        jsonBldgMeters = bldgMeters.json()

        for jsonBldgMeter in jsonBldgMeters:
            if jsonBldgMeter['MeterTypeID'] == 1:
                meterReadingDct['Electricity'] = jsonBldgMeter
            elif jsonBldgMeter['MeterTypeID'] == 2:
                meterReadingDct['Gas'] = jsonBldgMeter

        bldgMeterDct[bldgID] = meterReadingDct

    return bldgMeterDct


def get_meter_records(auditSpans, bldgMeterDct, meter_records_url, headers):
    """ Takes a dictionary of date ranges from amsaves_usage_range function
        and dictionary of meter objects from get_building_meters function;
        returns a dictionary of dictionaries containing meter readings for
        each fuel (electric & gas) with building IDs as keys """

    bldgMeterRecordsDct = {}
    for key, value in auditSpans.iteritems():
        elecBegin = value['E. Per. Begin']
        elecEnd = value['E. Per. End']
        if len(value) == 4:
            gasBegin = value['G. Per. Begin']
            gasEnd = value['G. Per. End']

        metersRecordsDct = {}
        for key, value in bldgMeterDct.iteritems():
            bldgID = key
            bldgMeter = value
            elecMeterID = str(bldgMeter['Electricity']['MeterID'])
            elecMeter_record_url = meter_records_url + elecMeterID + \
                                   '?start=' + elecBegin + '&end=' + elecEnd
            elecMeterRecords = requests.get(elecMeter_record_url, \
                                            headers=headers)
            metersRecordsDct['Elec. Meter Records'] = elecMeterRecords.json()
            if len(bldgMeter) == 2:
                elecMeterID = str(bldgMeter['Gas']['MeterID'])
                gasMeter_record_url = meter_records_url + elecMeterID + '\
                                          start=' + gasBegin + '&end=' + gasEnd
                gasMeterRecords = requests.get(gasMeter_record_url, \
                                               headers=headers)
                metersRecordsDct['Gas Meter Records'] = gasMeterRecords.json()
            bldgMeterRecordsDct[bldgID] = metersRecordsDct

    return bldgMeterRecordsDct
