#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import deltamtrsvs as dms_api
import amsaves as ams
import private as pvt
import types as tp
import pandas as pd
import re
from collections import defaultdict


headers = pvt.headers
properties_url = pvt.properties_url
model_url = pvt.model_url
comparison_url = pvt.comparison_url
audit_url = pvt.audit_url
sites = [pvt.FDL, pvt.HJSMS, pvt.Midlesboro]

def test_am_saves_results():
    """ Pass the results of get_model_comparisons to the am_saves_results 
        function, confirm DataFrame returned in requested results format for
        the 'America Saves!' program (write contents to .CSV file for review)
        """

    for site in sites:
        bldgIDs = dms_api.get_property_bldg_IDs(properties_url, site,
                                                headers)
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons) = dms_api.get_model_comparisons(comparison_url,
                                                                json_models,
                                                                headers)

        compLen = len(comparisons)
        usesDf = ams.am_saves_results(comparisons)

        fname = site+'-results.csv'
        with open(fname, 'wb') as outf:
            outcsv = usesDf.to_csv(fname)

    assert isinstance(usesDf, pd.DataFrame)
    assert usesDf.shape[1] == 7
    assert usesDf.shape[0] == compLen

def test_am_saves_audit():
    """ Pass the results of get_model_audits function, confirm DataFrame
        returned in requested results format for the 'America Saves!' program
        (write contents to .CSV file for review) """

    for site in sites:
        bldgIDs = dms_api.get_property_bldg_IDs(properties_url, site,
                                                headers)
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons) = dms_api.get_model_comparisons(comparison_url,
                                                                json_models,
                                                                headers)
        (refModelIDs, audits) = dms_api.get_model_audits(audit_url,
                                                           modelIDs, headers)

        combinedUsageDfs = ams.am_saves_audit(refModelIDs, audits)

        for refModelID in refModelIDs:
            df = pd.DataFrame(combinedUsageDfs[refModelID])
            fname = refModelID+'-audit.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

    assert isinstance(combinedUsageDfs, defaultdict)
    assert [isinstance(combinedUsageDf, pd.DataFrame) for combinedUsageDf in
            combinedUsageDfs]
