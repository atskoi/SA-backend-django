import json
import logging
from rest_framework.response import Response
from pac.helpers.connections import pyodbc_connection
from core.schemas import DashboardRequestSchema, buildFilterSchema
from core.base_class.app_view import AppView


class PickupDeliveryView(AppView):
    PRIMARY_TABLE = 'BrokerContractCost'
    PRIMARY_KEY = 'bcc.BrokerContractCostID'
    AUDIT_COLUMNS = ['Cost', 'RateBase', 'RateMax', 'PickupDeliveryCount', 'BrokerContractCostID']
    AUDIT_FKS = [
        {"fkCol": "SubServiceLevelID", "sourceCol": 'SubServiceLevelID', "sourceTable": "SubServiceLevel",
            "destCol": "SubServiceLevelVersionID", "histCol": "SubServiceLevelVersionID"},
        {"fkCol": "TerminalID", "sourceCol": 'TerminalID', "sourceTable": "Terminal",
                    "destCol": "TerminalVersionID", "histCol": "TerminalVersionID"},
            ]
    COLUMN_MAPPING = {
        "TerminalCode": {"filterType": "textFilters", "sortColumn": 'T.Description', "filter": " AND T.Description LIKE '%{0}%' "},
        "RegionCode": {"filterType": "textFilters","sortColumn": 'R.RegionCode', "filter": " AND R.RegionCode LIKE '%{0}%' "},
        "StatusID": {"filterType": "idFilters", "sortColumn": 'bcc.IsActive',
            "filter": """ AND (CASE WHEN bcc.IsInactiveViewable = 0 THEN 3 ELSE CASE WHEN bcc.IsActive = 0 THEN 2 ELSE 1 END
                END) IN ({0}) """},
        "SubServiceLevelID": {"filterType": "idFilters", "sortColumn": '',
                                         "filter": """ AND bcc.SubServiceLevelID IN ({0}) """},
        "SubServiceLevelCode": {"filterType": "sortOnly", "sortColumn": "ssl.SubServiceLevelCode"},
        "UpdatedOn": {"sortColumn": "bcch.UpdatedOn", "filter": " "},
        "PickupDeliveryCount": {"sortColumn": "bcc.PickupDeliveryCount", "filter": " "},
    }

    schema = buildFilterSchema(COLUMN_MAPPING)
    GET_FILTERED_QUERY = """{{opening_clause}}
    SELECT bcc.*, bcch.UpdatedOn, ssl.SubServiceLevelCode, sl.ServiceOfferingID,
        T.Description TerminalCode, T.TerminalName, R.RegionName, R.RegionCode, co.CountryName,
        CASE WHEN bcc.IsInactiveViewable = 0 THEN 'Deleted'
            ELSE CASE WHEN bcc.IsActive = 0 THEN 'Disabled' ELSE 'Enabled' END
        END AS Status
        FROM dbo.BrokerContractCost bcc
        INNER JOIN dbo.BrokerContractCost_History bcch ON bcch.BrokerContractCostID = bcc.BrokerContractCostID
            AND bcch.IsLatestVersion = 1
        INNER JOIN dbo.SubServiceLevel ssl ON ssl.SubServiceLevelID = bcc.SubServiceLevelID
        INNER JOIN dbo.ServiceLevel sl ON sl.ServiceLevelID = SSL.ServiceLevelID
        INNER JOIN dbo.Terminal t ON t.TerminalID = bcc.TerminalID
        INNER JOIN dbo.V_LocationTree lt ON lt.ID = t.TerminalID AND lt.PointTypeName = 'Terminal'
        INNER JOIN dbo.Province p ON p.ProvinceID = lt.ProvinceID
        INNER JOIN dbo.Region r ON r.RegionID = lt.RegionID
        INNER JOIN dbo.Country co ON co.CountryID = lt.CountryID
        WHERE bcc.IsInactiveViewable = 1 AND sl.ServiceOfferingID = {service_offering_id}
        {{where_clauses}}
        {{sort_clause}}
        {{page_clause}}
        {{closing_clause}}"""

    SKIP_AUDIT = False

    UPDATE_FIELDS = [
        {'fieldName': 'Cost', 'type': 'string'},
        {'fieldName': 'RateBase', 'type': 'number'},
        {'fieldName': 'RateMax', 'type': 'number'}
    ]
    INSERT_FIELDS = [
        {'fieldName': 'TerminalID', 'type': 'number'},
        {'fieldName': 'SubServiceLevelID', 'type': 'number'},
        {'fieldName': 'Cost', 'type': 'string'}
    ]

    def prepare_filter(self, data, kwargs):
        service_offering_id = kwargs.get("service_offering_id")
        self.GET_FILTERED_QUERY = self.GET_FILTERED_QUERY.format(service_offering_id=service_offering_id)
        return data

    def prepare_bulk_update(self, data, kwargs):
        update_rows = data.get('records')
        cleaned_rows = []
        if len(update_rows) > 0:
            for row in update_rows:
                values = row.get('data')
                costs = {}
                rateBase = 0
                rateMax = 0
                for fieldName in values:
                    if fieldName == 'RateBase':
                        rateBase = values.get(fieldName)
                    elif fieldName == 'RateMax':
                        rateMax = values.get(fieldName)
                    else:
                        costs[fieldName] = values.get(fieldName)
                row['data'] = {'Cost': json.dumps(costs), 'RateBase': rateBase, 'RateMax': rateMax}
        data['records'] = update_rows
        return data

    GET_SINGLE_QUERY = """SELECT
        bcch.BrokerContractCostID,
        bcch.BrokerContractCostVersionID,
        bcch.VersionNum,
        bcch.UpdatedOn,
        bcch.IsLatestVersion,
        bcch.Cost,
        th.TerminalID,
        th.TerminalCode,
        sslh.SubServiceLevelID,
        sslh.SubServiceLevelCode
        FROM dbo.BrokerContractCost_History bcch
        INNER JOIN dbo.Terminal_History th ON th.TerminalVersionID = bcch.TerminalVersionID
        INNER JOIN dbo.SubServiceLevel_History sslh ON sslh.SubServiceLevelVersionID = bcch.SubServiceLevelVersionID
        WHERE bcch.BrokerContractCostID = {primary_key_value}
        ORDER BY bcch.VersionNum DESC;
    """
