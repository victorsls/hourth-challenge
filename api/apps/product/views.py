import requests
import pandas as pd
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import date, datetime, timedelta

init_date = openapi.Parameter(
    'init_date', openapi.IN_QUERY,
    description="The start date",
    type=openapi.TYPE_STRING,
    required=True,

)

end_date = openapi.Parameter(
    'end_date', openapi.IN_QUERY,
    description="The end date",
    type=openapi.TYPE_STRING,
    required=True
)


class ProductListView(ListAPIView):
    # @swagger_auto_schema(manual_parameters=[init_date, end_date])
    def get(self, request, *args, **kwargs):
        data = requests.get(
            "https://mc3nt37jj5.execute-api.sa-east-1.amazonaws.com/default/hourth_desafio").json()
        products = self.convert_product_keys_str_to_date(
            products=data, keys=["consult_date", "product_url__created_at"])
        # start = datetime.strptime(dict(request.query_params)["init_date"][0], "%Y-%m-%d").date()
        # end = datetime.strptime(dict(request.query_params)["finish_date"][0], "%Y-%m-%d").date()

        return Response(self.get_products(products=products))

    @staticmethod
    def convert_product_keys_str_to_date(products: list, keys: list):
        for product in products:
            for key in keys:
                product[key] = datetime.strptime(
                    product[key], "%Y-%m-%d").date()
        return products

    def get_products(self, products):
        product_url_list = {i['product_url'] for i in products}
        data = {}
        for product_url in product_url_list:
            sales_by_date = []
            for product in products:
                if product["product_url"] == product_url:
                    sales_by_date.append(
                        {
                            str(product["consult_date"]): product["vendas_no_dia"],
                            "product_url__image": product["product_url__image"],
                            str("product_url__created_at"): product["product_url__created_at"]
                        }
                    )
            data[product_url] = sales_by_date
        response_data = []
        for key, value in data.items():
            product_data = {
                "product_url": key, 
                "total_sales": 0,
                # **self.get_dict_date_range(start=start, end=end)
            }

            for sales in value:
                product_data["total_sales"] += sales[list(sales.keys())[0]]
                product_data.update(sales)
            response_data.append(product_data)
        return response_data


    @staticmethod
    def get_dict_date_range(start: date, end):
        dates = [start + timedelta(n) for n in range(int((end - start).days))]
        dict_date_range = {}

        for date_ in dates:
            dict_date_range[str(date_)] = 0 
        return dict_date_range

