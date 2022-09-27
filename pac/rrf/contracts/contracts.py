import functools
import json
import logging
import requests
from rest_framework import generics, mixins, status, views
from rest_framework.response import Response
from rest_framework.renderers import BaseRenderer
from pac.helpers.connections import pyodbc_connection
# from pac.rrf.tabs.request_profile import RequestProfileView
from pac.rrf.views import GetRequestLanesPyodbcView
from pac.rrf.models import Request, ServiceLevel
import pac.rrf.accessorials.custom_terms as custom_terms
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import View
from xhtml2pdf import pisa

class GeneratePdf(views.APIView):

    def _get_accessorials(self, request_id):
        accessorials_query = """
            Select
                ao.SubServiceLevelID,
                sl.ServiceLevelName,
                ssl.SubServiceLevelName,
                ssl.SubServiceLevelCode,
                ao.AccRateFactorID Change,
                ao.AccRateShippingInstructionID ShippingInstruction,                                                           
                ao.AllowBetween,
                ao.UsagePercentage,
                ao.IsWaive,
                ao.OriginTypeID, lto.PointTypeName OriginType, ao.OriginID, 
                lto.Code OriginCode,   lto.Name OriginName,
                ao.DestinationTypeID, ltd.PointTypeName DestinationType, ao.DestinationID, 
                ltd.Code DestinationCode, ltd.Name DestinationName,
                COALESCE(ao.AccRateMaxCharge, ad.AccRateMaxCharge) AccRateMaxCharge,
                COALESCE(ao.AccRateMinCharge, ad.AccRateMinCharge) AccRateMinCharge,
                COALESCE(ao.MinStdCharge, ad.MinStdCharge) MinStdCharge                                
            from dbo.AccessorialOverride ao
            left join dbo.AccessorialDetail ad
                on ao.AccHeaderID = ad.AccHeaderID and 
                ao.originID = ad.originID and
                ao.originTypeID=ad.originTypeID and
                ao.destinationID=ad.destinationID and 
                ao.destinationTypeID=ad.destinationTypeId and
                ao.SubServiceLevelID = ad.SubServiceLevelID and
                ao.IsActive=1 and ao.IsInactiveViewable=1 and
                ad.IsActive=1 and ad.IsInactiveViewable=1
            left join SubServiceLevel ssl on ao.SubServiceLevelID = ssl.SubServiceLevelID
            left join ServiceLevel sl on ssl.ServiceLevelID = sl.ServiceLevelID
            left JOIN dbo.V_LocationTree lto ON lto.PointTypeID = ao.OriginTypeID AND lto.ID = ao.OriginID
            left JOIN dbo.V_LocationTree ltd ON ltd.PointTypeID = ao.DestinationTypeID AND ltd.ID = ao.DestinationID;
        """
        cnxn = pyodbc_connection()
        cursor = cnxn.cursor()
        cursor.execute(accessorials_query)
        columns = [column[0] for column in cursor.description]
        accessorials = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return accessorials

    def _get_custom_terms(self, request, *args, **kwargs):
        terms_api = custom_terms.TermsAPI()
        response = terms_api.get(request, *args, **kwargs)
        if not response.status_code == 200:
            raise
        return response.data

    def _get_language_text(self, language):
        lt =dict(
            EN = {
                'ACCESSORIAL OVERRIDES': 'ACCESSORIAL OVERRIDES',
                'ACCEPTED BY': 'ACCEPTED BY',
                'ADDRESS': 'ADDRESS',
                'AVERAGE DENSITY':'AVERAGE DENSITY',
                'AVERAGE SIZE OF SHIPMENTS': 'AVERAGE SIZE OF SHIPMENTS',
                'AVERAGE VOLUME PER MONTH': 'AVERAGE VOLUME PER MONTH',
                'Between': 'Between',
                'BETWEEN': 'BETWEEN',
                'Change': 'Change',
                'COMMODITY': 'COMMODITY',
                'CUSTOMER': 'CUSTOMER',
                'CUSTOMER INFORMATION PROFILE': 'CUSTOMER INFORMATION PROFILE',
                'CUSTOM TERMS': 'CUSTOM TERMS',
                'CUSTOM TERMS AND CONDITIONS': 'CUSTOM TERMS AND CONDITIONS',
                'DRAFT COPY - NOT FOR DISTRIBUTION': 'DRAFT COPY - NOT FOR DISTRIBUTION',
                'DATE': 'DATE',
                'Destination': 'Destination',
                'DESTINATION': 'DESTINATION',
                'Destination Type': 'Destination Type',
                'D&R ACCT': 'D&R ACCT',
                'EFFECTIVE': 'EFFECTIVE',
                'EXPIRY': 'EXPIRY',
                'FAX': 'FAX',
                'ISSUE DATE': 'ISSUE DATE',
                'LOCALITIES': 'LOCALITIES',
                'Maximum Change': 'Maximum Change',
                'Minimum Change': 'Minimum Change',
                'Maximum Shipment Value': 'Maximum Shipment Value',
                'Minimum Shipment Value': 'Minimum Shipment Value',
                'Minimum Standard Change': 'Minimum Standard Change',
                'of': 'of',
                'Origin': 'Origin',
                'Origin Type': 'Origin Type',
                'ORIGIN': 'ORIGIN',
                'PRESENTED BY': 'PRESENTED BY',
                'PRICING OFFICIAL': 'PRICING OFFICIAL',
                'Range Type': 'Range Type',
                'Section': 'Section',
                'Service Level': 'Service Level',
                'SERVICE LEVEL': 'SERVICE LEVEL',
                'Shipping Instruction': 'Shipping Instruction',
                'SIGNATURE': 'SIGNATURE',
                'TELEPHONE': 'TELEPHONE',
                'TERMS AND CONDITIONS': 'TERMS AND CONDITIONS',
                'TITLE': 'TITLE',
                'Usage': 'Usage',
        },
            FR = {
                 'ACCESSORIAL OVERRIDES': 'ACCESSORIAL OVERRIDES',
                 'ACCEPTED BY': 'ACCEPTÉ PAR',
                 'ADDRESS': 'ADRESSE',
                 'AVERAGE DENSITY': 'DENSITÉ MOYENNE',
                 'AVERAGE SIZE OF SHIPMENTS': 'EXPÉDITION MOYENNE',
                 'AVERAGE VOLUME PER MONTH': 'VOLUME MENSUEL MOYEN',
                 'Between': 'Between',
                 'BETWEEN': 'ENTRE',
                 'Change': 'Change',
                 'COMMODITY': 'COMMODITÉ',
                 'CUSTOMER': 'CLIENT',
                 'CUSTOMER INFORMATION PROFILE': "PROFIL D'INFORMATION DU CLIENT'",
                 'CUSTOM TERMS': 'CUSTOM TERMS',
                 'CUSTOM TERMS AND CONDITIONS': 'CUSTOM TERMES ET CONDITIONS',
                 'DRAFT COPY - NOT FOR DISTRIBUTION': 'DRAFT COPY - NOT FOR DISTRIBUTION',
                 'DATE': 'DATE',
                 'Destination': 'Destination',
                 'DESTINATION': 'DESTINATION',
                 'Destination Type': 'Destination Type',
                 'D&R ACCT': 'NUMÉRO DE COMPTE',
                 'EFFECTIVE': 'ENTRÉE EN VIGUEUR',
                 'EXPIRY': 'EXPIRATION',
                 'FAX': 'TÉLÉCOPIEUR',
                 'ISSUE DATE': 'ÉMISSION',
                 'LOCALITIES': 'LOCALITÉS',
                 'Maximum Change': 'Maximum Change',
                 'Minimum Change': 'Minimum Change',
                 'Maximum Shipment Value': 'Maximum Shipment Value',
                 'Minimum Shipment Value': 'Minimum Shipment Value',
                 'Minimum Standard Change': 'Minimum Standard Change',
                 'of': 'de',
                 'Origin': 'Origin',
                 'ORIGIN': 'ORIGINE',
                 'Origin Type': 'Origin Type',
                 'PRESENTED BY': 'PRÉSENTÉ PAR',
                 'PRICING OFFICIAL' : 'RESPONSABLE DE LA',
                 'Range Type': 'Range Type',
                 'Section': 'Section',
                 'Service Level': 'Niveau De Service',
                 'SERVICE LEVEL': 'NIVEAU DE SERVICE',
                 'Shipping Instruction' : 'Shipping Instruction',
                 'SIGNATURE': 'SIGNATURE',
                 'TELEPHONE': 'TÉLÉPHONE',
                 'TERMS AND CONDITIONS': 'TERMES ET CONDITIONS',
                 'TITLE': 'FONCTION',
                 'Usage': 'Usage',
            }
        )
        return lt.get(language, lt.get('EN'))

    def _get_sections(self, request, *args, **kwargs):

        # weight break column name comparison function
        def col_cmp(x,y):
            if x.isdigit() and y.isdigit(): #sort digit columns as ints
                return int(x) - int(y)
            elif not x.isdigit() and not y.isdigit(): #compare strings directly
                return 1 if x > y else -1
            else: #alpha before digits
                return -1 if x.isdigit() else 1

        request_lanes_view = GetRequestLanesPyodbcView()
        response = request_lanes_view.get(request, *args, **kwargs)
        if not response.status_code == 200:
            raise
        sections = {}
        for lane in response.data:
            request_section_lane_id = lane['RequestSectionLaneID']
            lane_costs = json.loads(lane['Cost'])
            if not (request_section_lane_id in sections):
                lane_cols = [k for k in lane_costs.keys() if k != 'null']
                lane_cols = sorted(lane_cols, key=functools.cmp_to_key(col_cmp))
                sections[request_section_lane_id] = dict(lane_cols=lane_cols, lanes=[])
            lane = dict(origin=lane['OriginCode'], destination=lane['DestinationCode'],
                        RequestSectionLaneID=request_section_lane_id)
            lane.update(lane_costs)
            sections[request_section_lane_id]['lanes'].append(lane)
        return sections

    def _get_request_header(self, request, *args, **kwargs):
        request_id = kwargs.get('RequestID')
        relative_url = f'request/header/{request_id}/'
        request_header = self._get_url(request, relative_url)
        return request_header

    def _get_request_info(self, request, *args, **kwargs):
        request_id = kwargs.get('RequestID')
        relative_url = f'request-information/id/{request_id}/'
        request_header = self._get_url(request, relative_url)
        return request_header

    def _get_review_data(self, request, request_id, *args, **kwargs):
        def reducer(acc, wn):
            w = wn[0]
            n = wn[1]
            acc[0] += n * w
            acc[1] += w
            return acc

        def weigthedAverage(nums, weights):
            if not nums or not weights:
                return
            result = functools.reduce(reducer, zip(weights, nums), [0, 0])
            total = result[0]
            weight_total = result[1]
            return total / weight_total

        relative_url = f'request/{request_id}/review/'
        request_review_data = self._get_url(request, relative_url)

        if request_review_data and request_review_data[0].get('Review', None):
            review_data = json.loads(request_review_data[0]['Review'])

            for review_item in review_data['RevenueHistory']:
                profit = review_item['MonthlyRevenue'] - review_item['TotalCosts']
                review_item.update(dict (
                    ProfitLossAmount=profit,
                    ProfitLossMargin=round((profit / review_item['MonthlyRevenue']) * 100)
                ))

            total_bill_weight = sum([item['BilledWeight'] for item in review_data['RevenueHistory'] ])
            avg_shipment_size = total_bill_weight / len(review_data['RevenueHistory'])
            avg_density = weigthedAverage([i['AverageDensity'] for i in review_data['RevenueHistory']],
                                          [i['NumPickups'] for i in review_data['RevenueHistory']])
            avg_monthly_volume = weigthedAverage([i['AverageWeight'] for i in review_data['RevenueHistory']],
                                          [i['NumPickups'] for i in review_data['RevenueHistory']])

            review_data = dict(avg_shipment_size=avg_shipment_size,
                               avg_density=avg_density,
                               avg_monthly_volume=avg_monthly_volume)
        else:
            review_data = dict(avg_shipment_size='',
                               avg_density='',
                               avg_monthly_volume='')

        return review_data

    def _get_terms(self, request_id):
        terms =[dict(title='Appointment Deliveries',
                     text="""When customer requests via the bill of lading or other means to establish a time and date specific Appointment, or Call and
                            Notify the consignee as a condition before attempting delivery, a charge of $30.00 per shipment shall be assessed to the
                            payer of the freight charges."""),
                dict(title='After Hour Service',
                     text="""Shipments requiring any of the following services: pick up, delivery, interchange, or transfer prior to 8:00 am or after 5:00 pm
                            during a normal working day will be subject to a surcharge $125. This surcharge is applicable only to the metropolitan city
                            areas of our terminal locations. Points outside these metropolitan localities will be subject to a surcharge of $250.00"""),
                dict(title='Dangerous Goods',
                     text="""Rates heren will not be subject to a surcharge for Dangerous Goods.."""),
                dict(title='Detention Without Power',
                     text="""Spotting of a trailer without power unit will be offered free of charge for the first 24 hours. For the first two 24hr periods
                            thereafter, a fee of $95.00/day $125.00/day for reefer) will apply. For the third and each succeeding 24 hr period, a charge of
                            $125.00/day $155.00/day for reefer) will apply."""),
                dict(title='Discounts Off FAK',
                     text="""A 30% discount will apply from FAK rates as published in DR1997 and reissues thereof between other direct service points
                            of Day & Ross Inc. This discount also applies on per shipment charges with the exception that movements within the Maritime provinces
                            and/or within Newfoundland will be subject to a minimum charge of $30.00 per shipment."""),
                dict(title='Online Pick ups / Deliveries',
                     text="""or truckload shipments a surcharge of $75.00 will apply for enroute pick ups. A surcharge of $75.00 will apply for enroute
                            deliveries. Offline miles will be assessed at $1.95 per mile."""),
                dict(title='Power Tailgate',
                     text="""For power tailgate pick ups a surcharge of $1.84 cwt, minimum $78.68 will apply when tailgate service is available. For
                            power tailgate deliveries a surcharge of $1.84 cwt, minimum $78.68 will apply when tailgate service is available.
                            EXCEPTION: Within the Toronto metro area, a surcharge of $1.84 cwt (min $89.17) will apply"""),
                dict(title='Private Residence/Limited Access Deliveries',
                     text="""Shipments requiring deliveries to premises without a designated dock or receiving area at Private Residences or locations
                            with limited access such as farms, ranches, dormitories, churches, or schools, will be subject to a surcharge of $50.00 ."""),
                dict(title='Private Residence/Limited Access Pickups',
                     text="""Shipments requiring pickups at premises without a designated dock or receiving area at Private Residences or locations
                            with limited access such as farms, ranches, dormitories, churches, or schools, will be subject to a surcharge of $50.00 ."""),
                dict(title='Protective Service',
                     text="""Subject to a surcharge of 18.00 % of the freight charge but not less than $30.00 per shipment. LTL refrigerated service is
                            not available."""),
                dict(title='Reconsignment / Diversion',
                     text="""For all locations, a surcharge of $3.00 cwt (min $40.00 / max $175.00) will apply in addition to all other linehaul freight
                            charges. See master tariff rules for different scenarios.
                            If a re-delivery is required to same address due to shipper / consignee error or request, the above applicable charges will
                            apply.
                            """),
                dict(title='Storage Fees',
                     text="""Dry freight will be subject to a surcharge of $1.25 cwt, minimum $30.00/day and freight requiring protective service will be
                            subject to $2.00 cwt, minimum $50.00/day."""),
                dict(title='Payment Terms',
                     text="""Freight charges are to paid within 30 days from date of invoicing. Contras on account for cargo claims will not be accepted.
                            """),
                dict(title='Tradeshow Pick Ups / Deliveries',
                     text="""Pick ups and or deliveries will be subject to a surcharge of $0.88 cwt, minimum of $157.35 .
                            """),
                dict(title='Valuation',
                     text="""A surcharge of 2.00% will be calculated based on the actual weight for a declared value in excess of $2.00 per lb Cdn
                            funds. Declared value shipments are accepted subject to approval of valuation limit, commodity and packaging. Standard
                            liability is based on $2.00 per lb Cdn funds on the actual weight of the shipment. Subject to the limitations of liability
                            contained in Carriers Bill of Lading, Carrier will not be held liable for any miscellaneous charges or costs assessed by either
                            shipper, consignee or any third party which do not directly relate to the value of the goods transported, as determined at the
                            time and place of shipment. Examples of non-claimable charges or costs include, but are not limited to the following:
                            penalities levied against shipper, carrier or a third party for late delivery, missed appointment, split deliveries, shortages
                            and/or damages.
                            """),
                dict(title='Weekend & Holiday Pick Ups / Deliveries',
                     text="""Pick ups / deliveries will be subject to a surcharge of $65.00/hr, min four (4) hours (min $260.00).
                            """),
                dict(title='Weight Restriction',
                     text="""Rates herein are subject to a minimum weight restriction of 10.00 lbs per cu ft up to 10.00 feet of trailer space; thereafter
                            shipments move at 1000 lbs per linear ft of trailer space occupied."""),
                dict(title='INSIDE PICKUP OR DELIVERY AND OTHER THAN GROUND FLOOR PICKUP OR DELIVERY',
                     text="""Inside pick up or delivery surcharge of $4.50 cwt, Minimum $50.00, Maximum $400.00, will be applicable when one or more
                            of the following criteria is met. The driver is required to go beyond the immediate area of the receiving door to pick up or
                            deliver the freight. The requested pick up or delivery location is other than the ground floor. The handling unit (s) of the
                            freight exceeds the width and or height of the receiving door and the driver must break down the unit(s)to complete the pick
                            up or delivery, where the actual weight of any individual piece exceeds 75lbs or the actual weight of the total shipment
                            exceeds 300lbs."""),
                dict(title='Fuel Surcharge',
                     text="""Rates herein are subject to 100.00% of the Day & Ross Fuel LTL road; and 100.00% of the Day & Ross Fuel TL road;
                            100% for heavy TL over 54999lbs & 100.00% for intermodal fuel.
                            """),
                dict(title='Notes',
                     text="""Rates herein are subject to all rules, regulations and accessorial charges as published in DR1997 and reissues thereof.
                            This tariff is valid for 30 days; if freight movements do not commence within 30 days of presentation this tariff becomes null
                            & void.
                            COST RECOVERY FERRY SURCHARGE - LTL
                            Shipments between Newfoundland and other Canadian provinces or territories will be subject to a surcharge of $22.91 with
                            shipment or volume weights less than 7500 LBS. The rate is subject to change based on rate increases from Marine
                            Atlantic, which are typically announced for an April effective date."""),
                dict(title='COST RECOVERY FERRY SURCHARGE - TL',
                     text="""Shipments between Newfoundland and other Canadian provinces or territories will be subject to a surcharge of $116.44 with
                            shipment or volume weights of 7500 LBS to 39999lbs. The rate is subject to change based on rate increases from Marine
                            Atlantic, which are typically announced for an April effective date."""),
                dict(title='Notes',
                     text="""These Terms and Conditions shall take the place of and entirely supersedes any oral or written contracts or agreements
                            that deal with the same subject matter as referenced herein. Except as otherwise specifically stated, no modification hereto
                            shall be of any force or effect unless reduced to writing and signed by both parties and expressly referred to as being
                            modifications of these Terms and Conditions. The Customer also recognizes and acknowledges the competitive value and
                            proprietary nature of the rates and Terms and Conditions ("Rates") provided by Day & Ross, and therefore the Customer
                            shall not disclose said Rates to any third parties without the prior written consent of Day & Ross."""),
                dict(title='COST RECOVERY FERRY SURCHARGE - TL',
                     text="""Shipments from Newfoundland to other Canadian provinces or territories will be subject to a surcharge of $202.36 with
                            shipment or volume weights of 40000 LBS & greater. The rate is subject to change based on rate increases from Marine
                            Atlantic, which are typically announced for an April effective date."""),
                dict(title='COST RECOVERY FERRY SURCHARGE - TL',
                     text="""Shipments to Newfoundland from other Canadian provinces or territories will be subject to a surcharge of $402.72 with
                            shipment or volume weights of 40000 LBS & greater. The rate is subject to change based on rate increases from Marine
                            Atlantic, which are typically announced for an April effective date.
                            """),
                dict(title='Extra Labour Services, including Lumper (aka Swamper) Fees',
                     text="""When a pickup or delivery requires the services of more than one person due to shipment size, shape, location or driver
                            safety the charge shall be $50.00 per person, per hour subject to a minimum of $200.00 per person required.
                            In the event a delivery requires the carrier to use and pay a Lumper (aka Swamper) Service, the Lumper Fee shall be
                            prorated to all delivered shipments on the trailer based on individual shipment weight subject to a minimum of $35.00 per
                            shipment."""),
                dict(title='Expedited Service for Monday delivery',
                     text="""Regular service for Friday pickups in Woodstock (ON) and Toronto destined to direct service locations in Vancouver,
                            Calgary, Edmonton, Saskatoon & Regina is delivery by Tuesday. Regular service for Friday pickups in Montreal,
                            Drummondville, and Ottawa destined to direct service locations in Calgary, Edmonton, Saskatoon & Regina is delivery by
                            Tuesday. Expedited Service for Monday delivery* is available at $38.00 per shipment. If Expedited is selected, customer
                            must clearly indicate that on the BOL by either checking Expedited (under “Level of Service”) or stating Expedited (in the
                            “Routing or Special Instructions” field). *Excludes Quebec to British Columbia."""),
        ]
        return terms

    def _get_url(self, request, relative_url):
        token_str = request.META.get('HTTP_X_CSRFTOKEN', '')
        current_url = request.build_absolute_uri()
        url_parts = current_url.split('/api/')
        url = url_parts[0] + '/api/' + relative_url
        try:
            response = requests.get(url,
                                    headers={"X-CSRFToken": token_str}, timeout=90)  # 5 second timeout
        except Exception as rest_errors:
            raise Exception(f'The Rest Request to {url} Failed')

        response_data = response.json()
        return response_data

    def get(self, request, *args, **kwargs):
        request_id = kwargs.get('RequestID')
        language = kwargs.get('language')
        if not language in ['EN','FR']:
            return Response({"status": "Failure"}, status=status.HTTP_400_BAD_REQUEST)
        language_text = self._get_language_text(language)
        request_id = Request.objects.filter(request_id=request_id).first().request_id
        kwargs.update(dict(RequestID=request_id))
        custom_terms = self._get_custom_terms(request, *args, **kwargs)
        accessorials = self._get_accessorials(request_id)
        sections = self._get_sections(request, *args, **kwargs)
        request_header = self._get_request_header(request, *args, **kwargs)
        request_info = self._get_request_info(request, *args, **kwargs)
        request_review_data = self._get_review_data(request, request_id, *args, **kwargs)
        terms = self._get_terms(request_id)
        service_level_name = ServiceLevel.objects.filter(service_level_id=request_header.get('service_level_id')).first().service_level_name
        context = dict(context=dict(accessorials=accessorials,
                customer=json.loads(request_info.get('customer')),
                custom_terms= custom_terms,
                language_text=language_text,
                request_header=request_header,
                request_info = json.loads(request_info.get('request_information')),
                request_review_data = request_review_data,
                sections=sections,
                service_level=service_level_name,
                terms=terms,
            )
        )
        template = get_template("contracts.html")
        html = template.render(context)
        result = BytesIO()
        pisa_status = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
        if not pisa_status.err:
            try:
                response = HttpResponse(result.getvalue(),
                                        content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="customer_contract.pdf"'
                return response
            except Exception as rest_errors:
                raise Exception(rest_errors)
        else:
            return Response({"status": "Failure"}, status=status.HTTP_400_BAD_REQUEST)