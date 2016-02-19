#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import types as tp
import re
import deltamtrsvs as dms_api
import private as pvt


headers = pvt.headers
properties_url = pvt.properties_url
model_url = pvt.model_url
comparison_url = pvt.comparison_url
audit_url = pvt.audit_url
sites = [pvt.FDL, pvt.HJSMS, pvt.Middlesboro]

def test_get_property_bldgs():
    """ Pass an API URL, property id & header; confirm the fuction returns the
        expected bldg IDs """
    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
    
        assert type(bldgIDs) == tp.ListType
        # assert len(bldgIDs) > 0
        assert [type(bldgID)==tp.StringType for bldgID in bldgIDs]
        assert [re.match('\d{4}', bldgID) for bldgID in bldgIDs]

def test_get_bldg_models():
    """ Pass a list of bldg ids & header, confirm the fuction returns the
        expected valid bldg IDs """

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)

        assert type(valBldgIDs) == tp.ListType
        # assert len(valBldgIDs) <= len(bldgIDs)
        assert [type(valBldgID)==tp.StringType for valBldgID in valBldgIDs]
        assert [re.match('\d{4}', valBldgID) for valBldgID in valBldgIDs]

def test_get_model_comparisons():
    """ Pass a list of models' data, confirm the fuction returns the expected
        model IDs """

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons, jModDct) = dms_api.get_model_comparisons(
                                                                comparison_url,
                                                                json_models,
                                                                headers)

        assert type(modelIDs) == tp.ListType
        # assert len(modelIDs) >= len(valBldgIDs)
        assert [type(modelID)==tp.StringType for modelID in modelIDs]
        assert [re.match('\d{4}', modelID) for modelID in modelIDs]

def test_get_model_audits():
    """ Pass a list of model IDs; confirm the funciton returns valid audit IDs and the expected audit data """ 

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)

        auditsDct = dms_api.get_model_audits(audit_url, valBldgIDs, headers)
        refModels = auditsDct.keys()

    type(refModels) == tp.ListType
    assert [type(refModel)==tp.StringType for refModel in refModels]
    assert [re.match('\d{4}', refModel) for refModel in refModels] 

def test_get_fv_charts():
    """ Pass a URL, a list of moddle ID's and required API header; return a
        list of FirstView chart objects """

    diagnMsgCodes =[]

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        fvCharts = dms_api.get_fv_charts(pvt.fv_charts_url, bldgIDs, headers)
        for fvChart in fvCharts:
            # TODO (eayoungs): Repeat selections & attribute assertions for
            #                  remaining fields
            diagnstcs = fvChart['Diagnostics']
            msgCode = [diagnstc['MessageCode'] for diagnstc in diagnstcs]
            diagnMsgCodes.append(msgCode)

            assert len(msgCode) == 10
            assert [type(diagnstc['MessageCode'])==tp.StringType for diagnstc
                    in diagnstcs]

        assert len(fvCharts) == len(bldgIDs)

def test_get_bldg_meters():
    """ Pass a single building ID number; return a list of meter objects in
        .JSON format associated with the given building """

    bldgIDct = dms_api.get_property_bldgs(properties_url, '43', headers)
    bldgIDs = []
    for key in bldgIDct:
        bldgIDs.append(str(key))

    bldgMeters = dms_api.get_bldg_meters(pvt.bldg_meters_url, bldgIDs, headers)

    for bldgMeter in bldgMeters:
        for bldgID in bldgIDs:
            assert type(bldgMeter[bldgID]) == tp.ListType
            assert len(bldgMeter[bldgID]) <= 2
            if bldgMeter[bldgID] > 1:
                if bldgMeter[bldgID][0]["MeterTypeID"] == 1:
                    assert bldgMeter[bldgID][1]["MeterTypeID"] != 1
                else:
                    if bldgMeter[bldgID][0]["MeterTypeID"] == 1:
                        assert bldgMeter[bldgID][1]["MeterTypeID"] != 1
                if bldgMeter[bldgID][0]["MeterTypeID"] == 2:
                    assert bldgMeter[bldgID][1]["MeterTypeID"] != 2
                else:
                    if bldgMeter[bldgID][1]["MeterTypeID"] == 2:
                        assert bldgMeter[bldgID][0]["MeterTypeID"] != 2
