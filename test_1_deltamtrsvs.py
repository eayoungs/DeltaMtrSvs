#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@successionecological.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import json
import types as tp
import re
import deltamtrsvs
import amsaves as ams
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
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site, headers)
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
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        for key in modelsJsonDct:
            assert type(modelsJsonDct) == tp.DictType
            assert type(key)==tp.StringType 
            assert re.match('\d{4}', key)


def test_get_model_comparisons():
    """ Pass a list of models' data, confirm the fuction returns the expected
        model IDs """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                    headers)
        modelIDs = []
        for key in modelsJsonDct:
            modelIDs.append(str(key))

        (modelIDs, comparisons, jModDct) = deltamtrsvs.get_model_comparisons(
                                                                comparison_url,
                                                                modelsJsonDct,
                                                                headers)
        assert type(modelIDs) == tp.ListType
        # assert len(modelIDs) >= len(valBldgIDs)
        assert [type(modelID)==tp.StringType for modelID in modelIDs]
        assert [re.match('\d{4}', modelID) for modelID in modelIDs]


def test_get_model_audits():
    """ Pass a list of model IDs; confirm the funciton returns valid audit IDs
        and the expected audit data """ 

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                    headers)
        valBldgIDs = []
        for key in modelsJsonDct:
            valBldgIDs.append(str(key))

        (refModels, audits) = deltamtrsvs.get_model_audits(audit_url,
                                                           valBldgIDs, headers)
    type(refModels) == tp.ListType
    assert [type(refModel)==tp.StringType for refModel in refModels]
    assert [re.match('\d{4}', refModel) for refModel in refModels] 


def test_get_fv_charts():
    """ Pass a URL, a list of moddle ID's and required API header; return a
        list of FirstView chart objects """

    diagnMsgCodes =[]
    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        fvCharts = deltamtrsvs.get_fv_charts(pvt.fv_charts_url, bldgIDs,
                                             headers)
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

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        bldgMeterDct = deltamtrsvs.get_bldg_meters(pvt.bldg_meters_url, bldgIDs
                                                   , headers)
        assert type(bldgMeterDct) == tp.DictType
        for key, value in bldgMeterDct.iteritems():
            assert type(key) == tp.StringType
            assert type(value) == tp.DictType
            assert len(value) <= 2
        
def test_get_meter_records():
    """ Pass a dictionary of *audit* spans from amsaves_usage_range with
        reference model IDs from the amsaves_usage_range function as keys and
        a list of meter IDs from get_bldg_meters function  """

    #for site in sites:
    bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, '43',
                                              headers)
    bldgIDs = []
    for key in bldgIDct:
        bldgIDs.append(str(key))

    modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                        headers)
    (modelIDs, comparisons, jModDct) = deltamtrsvs.get_model_comparisons(
                                                            comparison_url,
                                                            modelsJsonDct,
                                                            headers)
    (refModelIDs, audits) = deltamtrsvs.get_model_audits(audit_url,
                                                         modelIDs, headers)
    auditSpans = ams.amsaves_usage_range(refModelIDs, audits)
    bldgMeterDct = deltamtrsvs.get_bldg_meters(pvt.bldg_meters_url, bldgIDs
                                               , headers)
    metersRecordsDct = deltamtrsvs.get_meter_records(auditSpans, bldgMeterDct,
                                            pvt.meter_records_url, headers)
    assert metersRecordsDct
    for key, value in metersRecordsDct.iteritems():
        assert type(key) == tp.StringType
        assert type(value) == tp.DictType
        assert len(value) <= 2
        elecMtrVals = value['Elec. Meter Records']
        assert type(elecMtrVals) == tp.ListType
        assert [type(elecMtrVal) == tp.DictType for elecMtrVal in elecMtrVals]
