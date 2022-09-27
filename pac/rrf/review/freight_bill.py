from core.base_class.app_view import AppView


# Get rows of Freight Bills Warning
class FreightBillWarningAPI(AppView):
    PRIMARY_TABLE = 'FreightBillWarning'
    PRIMARY_KEY = 'fb.FreightBillWarningID'

    GET_ALL_QUERY = """SELECT * FROM FreightBillWarning fb
                        ORDER BY fb.FreightBillWarningID"""
