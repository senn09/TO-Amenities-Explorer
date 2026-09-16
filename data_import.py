import requests
import pandas as pd
from io import StringIO

base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
	
params = [{ 
            "id": "library-branch-general-information",
            "col": [
                'BranchName', 
                'Address', 
                'Website', 
                'SquareFootage', 
                'PublicParking',
                'PublicWashroom',
                'Hours',
                ]}, { 
            "id": "parks-and-recreation-facilities",
            "col": [
                'ASSET_NAME',
                'TYPE',
                'ADDRESS',
                'PHONE',
                'URL',
            ]}
]

for param in params:
    print(f'retreving {param['id']} ...')
    url = base_url + "/api/3/action/package_show"
    package = requests.get(url, params = param).json()

    # To get resource data:
    for idx, resource in enumerate(package["result"]["resources"]):

        # for datastore_active resources:
        if resource["datastore_active"]:

            # To get all records in CSV format:
            url = base_url + "/datastore/dump/" + resource["id"]
            resource_dump_data = requests.get(url).text
            df = pd.read_csv(StringIO(resource_dump_data))
            print(df[param['col']])

