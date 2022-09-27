from django.urls import path
from rest_framework import routers

import pac.pre_costing.views as views
import pac.pre_costing.line_haul_costs.line_haul as line_hauls
import pac.pre_costing.terminal_costs.terminal_api as terminal_costs
import pac.pre_costing.speed_sheets.speed_sheets_api as speed_sheets
import pac.pre_costing.extra_miles.terminal_service_point_api as terminal_service_point_api
import pac.pre_costing.currency_exchange_views as ce_views
import pac.pre_costing.pickup_delivery.pickup_delivery as pickup_del
import pac.pre_costing.accessorials.accessorials as accessorials
import pac.pre_costing.spotquote_margin.spotquote_margin as spotquote_margin
import pac.pre_costing.line_haul_routes.line_haul_routes as line_haul_routes
import pac.pre_costing.cross_dock.cross_dock_routes as cross_dock
import pac.pre_costing.weight_breaks.weight_breaks as weight_breaks

router = routers.DefaultRouter()
router.register(r'terminalcost', views.TerminalCostViewSet,
                basename='terminal-cost')
router.register(r'dockroute', views.DockRouteViewSet,
                basename='dock-route')
router.register(r'laneroute', views.LaneRouteViewSet,
                basename='lane-route')
router.register(r'lanecost', views.LaneCostViewSet,
                basename='lane-cost')
router.register(r'legcost', views.LegCostViewSet,
                basename='leg-cost')
router.register(r'brokercontractcost', views.BrokerContractCostViewSet,
                basename='broker-contract-cost')
router.register(r'speedsheet', views.SpeedSheetViewSet,
                basename='speed-sheet')
router.register(r'terminalservicepoint', views.TerminalServicePointViewSet,
                basename='terminal-service-point')
router.register(r'weightbreakheader', views.WeightBreakHeaderViewSet,
                basename='weight-break-header')

urlpatterns = [
    path(
        'country/revert/<str:country_id>/<int:version_num>/',
        views.CountryRevertVersionView.as_view(),
        name='country-revert'
    ),
    path(
        'province/revert/<str:province_id>/<int:version_num>/',
        views.ProvinceRevertVersionView.as_view(),
        name='province-revert'
    ),
    path(
        'authentication_demo/',
        views.authentication_demo,
        name='authentication-demo'
    ),
    path(
        'dockcosts/dashboard/<int:service_offering_id>/',
        terminal_costs.TerminalCostAPI.as_view(),
        name='dockcosts-dashboard'
    ),
    path(
        'dockcosts/detail/<int:terminal_cost_id>/',
        views.DockCostsDetailPanelView.as_view(),
        name='dockcosts-panel'
    ),
    path(
        'dockcosts/toggle-status/<int:TerminalCostID>/',
        terminal_costs.TerminalCostAPI.as_view(http_method_names = ['delete']),
        name='dockcosts-toggle-status'
    ),
    path(
        'dockcosts/dashboard/batch-update/',
        terminal_costs.TerminalCostAPI.as_view(),
        name='dockcosts-dashboard-batch-update'
    ),
    path(
        'cross-dock/dashboard/<int:service_offering_id>/',
        cross_dock.CrossDockAPI.as_view(),
        name='dock-route-dashboard'
    ),
    path(
        'cross-dock/<int:DockRouteID>/',
        cross_dock.CrossDockAPI.as_view(),
        name='dock-route-dashboard'
    ),
    path(
        'cross-dock/',
        cross_dock.CrossDockAPI.as_view(),
        name='dock-route-dashboard'
    ),
    path(
        'dockroute/dashboard/batch-update/',
        views.DockRoutesBatchUpdateView.as_view(),
        name='dock-route-dashboard-batch-update'
    ),
    path(
        'laneroute/dashboard/<int:service_offering_id>/',
        views.LinehaulLaneRoutesDashboardPyodbcView.as_view(),
        name='lane-route-dashboard'
    ),
    path(
        'laneroute/dashboard/batch-update/',
        views.LaneRoutesBatchCreateUpdateView.as_view(),
        name='lane-route-dashboard-batch-update'
    ),
    path(
        'laneroute/detail/<int:lane_route_id>/',
        views.LinehaulLaneRoutesDetailPanelView.as_view(),
        name='lane-route-panel'
    ),
      path(
          'line-haul-routes/dashboard/<int:service_offering_id>/',
          line_haul_routes.LineHaulRoutesView.as_view(),
          name='line-haul-routes-dashboard'
      ),
    path(
        'linehaul/dashboard/<int:service_offering_id>/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['get']),
        name='linehaul-dashboard'
    ),
    path(
        'lanecost/dashboard/<int:service_offering_id>/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['put']),
        name='lane-cost-reduced-dashboard'
    ),
    path(
        'lanecost/toggle-status/<int:LaneCostID>/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['delete']),
        name='lane-cost-reduced-dashboard'
    ),
    path(
        'legcost/toggle-status/<int:LegCostID>/',
        line_hauls.LegCostsAPI.as_view(http_method_names = ['delete']),
        name='lane-cost-reduced-dashboard'
    ),
    path(
        'linehaul/lanecosts/batch-update/',
        line_hauls.LaneCostsAPI.as_view(http_method_names = ['put', 'post']),
        name='lanecosts-dashboard-batch-update'
    ),
    path(
        'linehaul/legcosts/batch-update/',
        line_hauls.LegCostsAPI.as_view(),
        name='lanecosts-dashboard-batch-update'
    ),

    path(
        'legcost/dashboard/<int:service_offering_id>/',
        line_hauls.LegCostsAPI.as_view(),
        name='leg-cost-dashboard'
    ),
    path(
        'linehaul/dashboard/',
        views.LinehaulLaneLegCostBatchCreateUpdateView.as_view(),
        name='linehaul-batch-create-update'
    ),
    path(
        'lanecost/detail/<int:lane_cost_id>/',
        views.LinehaulLaneCostsDetailPanelView.as_view(),
        name='lane-cost-panel'
    ),
    path(
        'legcost/detail/<int:leg_cost_id>/',
        views.LinehaulLegCostsDetailPanelView.as_view(),
        name='leg-cost-panel'
    ),
    path(
        'legsforroutes/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LegsForRoutesPyodbcView.as_view(),
        name='legs-for-routing'
    ),
    path(
        'lanecost/destination/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LaneDestinationTerminalsPyodbcView.as_view(),
        name='lane-cost-destination'
    ),
    path(
        'legcost/origin/<int:service_level_id>/',
        views.LegCostOriginTerminalView.as_view(),
        name='leg-cost-origin'
    ),
    path(
        'legcost/destination/<int:service_level_id>/<int:origin_terminal_id>/',
        views.LegCostDestinationTerminalView.as_view(),
        name='leg-cost-destination'
    ),
    path(
        'pickup-delivery/dashboard/<int:service_offering_id>/',
        pickup_del.PickupDeliveryView.as_view(),
        name='broker-contract-cost-dashboard'
    ),
    path(
        'brokercontractcost/detail/<int:BrokerContractCostID>/',
        pickup_del.PickupDeliveryView.as_view(),
        name='broker-contract-cost-panel'
    ),
    path(
        'currencyexchange/dashboard/',
        ce_views.CurrencyExchangeDashboardView.as_view(http_method_names = ['get']),
        name='currency-exchange-dashboard'
    ),
    path(
        'currencyexchange/update/',
        ce_views.CurrencyExchangeDashboardView.as_view(http_method_names = ['put']),
        name='currency-exchange-update'
    ),
    path(
        'speedsheet/dashboard/<int:service_offering_id>/',
        speed_sheets.SpeedSheetAPI.as_view(),
        name='speed-sheet-dashboard'
    ),
    path(
        'speedsheet/dashboard/batch-update/',
        speed_sheets.SpeedSheetAPI.as_view(),
        name='speed-sheet-batch-update'
    ),
    path(
        'terminalservicepoint/dashboard/',
        terminal_service_point_api.TerminalServicePointAPI.as_view(),
        name='terminal-service-point-dashboard'
    ),
    path(
        'terminalservicepoint/batch-update/',
        terminal_service_point_api.TerminalServicePointAPI.as_view(),
        name='terminal-service-point-batch-update'
    ),
    path(
        'terminalservicepoint/detail/<int:terminal_service_point_id>/',
        views.PointsExtraMilesDetailPanelView.as_view(),
        name='terminal-service-point-panel'
    ),
    path(
        'weightbreakheader/detail/<int:weight_break_header_id>/',
        views.WeightBreakHeaderDetailPanelView.as_view(),
        name='weight-break-header-panel'
    ),
    path(
        'weightbreakheader/dashboard/<int:service_offering_id>/',
        views.WeightBreakHeadersDashboardPyodbcView.as_view(),
        name='weight-break-header-dashboard'
    ),
    path(
        'weightbreakheader/dashboard/level/<int:service_level_id>/',
        views.WeightBreakHeadersLevelPyodbcView.as_view(),
        name='weight-break-header-level'
    ),
    path(
        'weightbreakheader/',
        weight_breaks.WeightBreakHeadersAPI.as_view(http_method_names=['put']),
        name='weight-break-header-toggle'
    ),
    path(
        'dockroute/create/',
        views.post_dockroute_pyodbc,
        name='dockroute-create'
    ),
    path(
        'terminalcostweightbreaklevel/batch-update/',
        views.post_terminal_cost_weight_break_level_pyodbc,
        name='terminalcostweightbreaklevel-batch-update'
    ),
    path(
        'accountsearch/<int:service_level_id>/<str:account_name>/',
        views.account_search_by_name_pyodbc.as_view(),
        name='account-search-by-name'
    ),
    path(
        'citysearch/<int:province_id>/<str:city_name>/',
        views.city_search_by_name_pyodbc.as_view(),
        name='city-search-by-name'
    ),
    path(
        'servicepointsearch/<int:service_offering_id>/<str:service_point_name>/',
        views.service_point_search_by_name_pyodbc.as_view(),
        name='service-point-search-by-name'
    ),
    path(
        'gri-review/',
        views.GriReviewView.as_view(),
        name='gri-view'
    ),
    path(
        'gri-review/<int:gri_review_id>/',
        views.GriReviewView.as_view(),
        name='gri-view'
    ),
    path(
        'accessorial_header/',
        accessorials.AccessorialHeaderAPI.as_view(http_method_names=['get', 'put']),
        name='precosting-accessorial-header-list'
    ),
    path(
        'accessorial_details/<int:AccHeaderID>/behavior/<str:TMChargeBehaviorCode>/',
        accessorials.AccessorialDetailsAPI.as_view(http_method_names=['put']),
        name='precosting-accessorial-business-standard-charge-view'
    ),
    path(
        'spotquote_margin/',
        spotquote_margin.SpotQuoteMarginAPI.as_view(http_method_names=['get', 'post', 'put']),
        name='precosting-spotquote-margin-list'
    ),
    path(
        'spotquote_margin/<int:SpotQuoteMarginID>/',
        spotquote_margin.SpotQuoteMarginAPI.as_view(http_method_names=['get']),
        name='precosting-spotquote-margin'
    ),

]
urlpatterns += router.urls
