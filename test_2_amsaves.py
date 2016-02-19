#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@Successionecological.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import datetime
import types as tp
import pandas as pd
import re
import deltamtrsvs as dms_api
import amsaves as ams
import private as pvt


headers = pvt.headers
properties_url = pvt.properties_url
model_url = pvt.model_url
comparison_url = pvt.comparison_url
audit_url = pvt.audit_url
sites = [pvt.Middlesboro, pvt.FDL, pvt.HJSMS]

def test_amsaves_results():
    """ Pass the results of get_model_comparisons to the amsaves_results 
        function, confirm DataFrame returned in requested results format for
        the 'America Saves!' program (write contents to .CSV file for review)
        """

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, compDct, jModDct) = dms_api.get_model_comparisons(
                                                                comparison_url,
                                                                json_models,
                                                                headers)

        # compLen = len(comparisons)
        usesDf = ams.amsaves_results(compDct, jModDct, bldgIDct)

        fname = site+'-results.csv'
        with open(fname, 'wb') as outf:
            outcsv = usesDf.to_csv(fname)

    assert isinstance(usesDf, pd.DataFrame)
    assert usesDf.shape[1] == 13
    # assert usesDf.shape[0] == compLen

def test_am_saves_audit():
    """ Pass the results of get_model_audits function, confirm DataFrame
        returned in requested results format for the 'America Saves!' program
        (write contents to .CSV file for review) """

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
        (refModelIDs, audits) = dms_api.get_model_audits(audit_url, modelIDs,
                                                         headers)

        combinedUsageDct = ams.am_saves_audit(refModelIDs, audits)

        assert isinstance(combinedUsageDct, dict)

        for refModelAdtID in refModelIDs:
            df = combinedUsageDct[refModelAdtID]
            # span = datetime.date.datefromtimestamp(df['Per. Start'])
            # print(span.max)
            fname = refModelAdtID + '-audit.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

            assert isinstance(combinedUsageDct[refModelAdtID], pd.DataFrame)

def test_amsaves_flags():
    """ """

    for site in sites:
        bldgIDct = dms_api.get_property_bldgs(properties_url, site, headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        fvCharts = dms_api.get_fv_charts(pvt.fv_charts_url, valBldgIDs,
                                         headers)
        flags = ams.amsaves_flags(fvCharts)
        # TODO (eayoungs): Needs more robust assertions
        assert [type(flag)==tp.StringType for flag in flags]

        siteFlags = []
        for flag in flags:
            bldgFlags = []
            if flag['Occupant Load'][0] == 'A' or \
                flag['Occupant Load'][0] == 'B' or \
                flag['Occupant Load'][0] == 'C':
                intrnElec = flag['Occupant Load'][0]
                ultrHighIntExt = ''
            elif flag['Occupant Load'][0] == 'O' or \
                flag['Occupant Load'] == 'P':
                ultrHighIntExt = flag['Occupant Load'][0]
                intrnElec = ''
            if flag['Summer Gas Use'][1] == "High":
                highGasBaseLd = "M"
            else: highGasBaseLd = ""

            bldgFlags = [intrnElec, ultrHighIntExt,
                         flag['Controls Heating'][0],
                         flag['Shell Ventilation'][0],
                         flag['Controls Cooling'][0],
                         flag['Cooling Efficiency'][0],
                         flag['Data Consistency'][0],
                         highGasBaseLd]

            siteFlags.append(bldgFlags)
            assert len(bldgFlags) == 8
            assert [type(bldgFlag) == tp.StringType for bldgFlag in bldgFlags]
            assert [len(bldgFlag) == 1 for bldgFlag in bldgFlags]
    
            colNms = ['Int. Elec.', 'Ultra-High Elec.', 'Excessive Htg.',
                      'Shell & Vent.', 'Excessive Clg', 'Inefficient Clg',
                      'Erratic Operation', 'High Gas Eqp.']
            df = pd.DataFrame(data=siteFlags, columns=colNms)

            fname = site+'-flags.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

    assert len(siteFlags) == len(flags)
    assert len(fvCharts) == len(bldgIDs)

def test_amsaves_usage_range():
    """ """
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
        (refModelIDs, audits) = dms_api.get_model_audits(audit_url, modelIDs,
                                                         headers)

        combinedUsageDct = ams.am_saves_audit(refModelIDs, audits)

        assert isinstance(combinedUsageDct, dict)
