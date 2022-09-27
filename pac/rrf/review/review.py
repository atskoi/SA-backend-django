from core.base_class.app_view import AppView
from pac.helpers.connections import pyodbc_connection, getQueryRowResult

# Get rows of Review Feature
class ReviewAPI(AppView):
    PRIMARY_TABLE = 'Review'
    PRIMARY_KEY = 'r.ReviewID'
    GET_SINGLE_QUERY = """SELECT * FROM Review r
                            WHERE r.IsActive = 1 AND r.IsInactiveViewable = 1
                            AND r.ReviewID = {review_id}
                            ORDER BY r.ReviewID"""

    GET_ALL_QUERY = """SELECT (SELECT r.*, SalesIncentiveType,
                    (SELECT rh.* FROM RevenueHistory rh INNER JOIN Review ON rh.ReviewID = Review.ReviewID FOR JSON AUTO) AS RevenueHistory,
                    (SELECT rb.* FROM RevenueBreakdown rb INNER JOIN Review ON rb.ReviewID = Review.ReviewID FOR JSON AUTO) AS RevenueBreakdown,
                    (SELECT pls.*, LaneType.LaneTypeName from ProfitLossSummary pls 
                    INNER JOIN Review ON pls.ReviewID = Review.ReviewID 
                    INNER JOIN LaneType ON pls.LaneTypeID = LaneType.LaneTypeID FOR JSON PATH) AS ProfitLossSummary
                    FROM Review r 
                    INNER JOIN SalesIncentive ON r.SalesIncentiveID = SalesIncentive.SalesIncentiveID
                    WHERE r.RequestID = {request_id} AND r.IsActive = 1 AND r.IsInactiveViewable = 1 FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) As Review"""

    COLUMN_MAPPING = {}
    UPDATE_FIELDS = [
        {'fieldName': 'PricingRateChangeDol', 'type': 'string'},
        {'fieldName': 'PricingRateChangePer', 'type': 'string'},
        {'fieldName': 'SalesRateChangeDol', 'type': 'string'},
        {'fieldName': 'SalesRateChangePer', 'type': 'string'},
        {'fieldName': 'AverageShipmentSize', 'type': 'number'},
        {'fieldName': 'AverageShipmentDensity', 'type': 'number'},
        {'fieldName': 'MonthlyShipmentValue', 'type': 'number'},
        {'fieldName': 'SalesIncentiveID', 'type': 'number'}]

    INSERT_FIELDS = [
        {'fieldName': 'RequestID', 'type': 'number'},
        {'fieldName': 'ReviewEffDate', 'type': 'current_datetime'},
        {'fieldName': 'ReviewType', 'type': 'string'},
        {'fieldName': 'SalesIncentiveID', 'type': 'number', 'default': 1},
        {'fieldName': 'ReviewExpDate', 'type': 'current_datetime'}]

    def prepare_get(self, kwargs, request):  # function to call in preparation for running the default GET behavior
        review_id = kwargs.get("ReviewID", None)
        request_id = kwargs.get("RequestID")
        if review_id:
            self.GET_SINGLE_QUERY = self.GET_SINGLE_QUERY.format(review_id=review_id)
        else:
            self.GET_ALL_QUERY = self.GET_ALL_QUERY.format(request_id=request_id)

    def prepare_bulk_update(self, data, kwargs):  # optional function to prepare the class or data before bulk_update
        if not hasattr(self, 'conn'):
            self.conn = pyodbc_connection()  # open a new connection and a transaction
        return data

    def prepare_bulk_insert(self, data, kwargs):
        if not hasattr(self, 'conn') or self.conn == None:
            self.conn = pyodbc_connection()  # open a new connection and a transaction

        cursor = self.conn.cursor()
        for row in data:
            row_data = row['data']
            request_id = row_data['RequestID']
            if request_id is None:
                return []  # cannot complete without request_id
            request = getQueryRowResult(cursor,
                                        f'SELECT * FROM dbo.Request WHERE RequestID = {request_id}')
            if request['UniType'] == 'Annual Review Tariff':
                row_data['ReviewType'] = 'Annual'
            row['data'] = row_data
        return data
