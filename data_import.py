import requests
import pandas as pd
from io import StringIO

base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

col_of_interest = ['name', 'address', 'type_id']
        
params =    [{ 
                "id": "library-branch-general-information",
                "type_id": 1,
                "col_name_transform": [
                    ('BranchName', col_of_interest[0]),
                    ('Address', col_of_interest[1]),
                ],
                "col_of_interest": [
                    'BranchName', 
                    'Address', 
                    'Website', 
                    'SquareFootage', 
                    'PublicParking',
                    'PublicWashroom',
                    'Hours',
                    ]}, 
            { 
                "id": "parks-and-recreation-facilities",
                "type_id": 2,
                "col_name_transform": [
                    ('ASSET_NAME', col_of_interest[0]),
                    ('ADDRESS', col_of_interest[1]),
                    ('TYPE', col_of_interest[2]),
                ],
                "col_of_interest": [
                    'ASSET_NAME',
                    'TYPE',
                    'ADDRESS',
                    'PHONE',
                    'URL',
                ]
            }]

def pull_data(param):
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
    return df

def format_data_for_db(param, df):
    # uses 'col_name_transform' to rename columns to match database model
    for i in range(len(param['col_name_transform'])):
        df.rename(columns={param['col_name_transform'][i][0]: param['col_name_transform'][i][1]}, inplace=True)

    if param['type_id'] == 2:
        df['type_id'] = df['type_id'].replace({'Park': 2, 'Community Centre': 3, 'Civic Centre': 4})
    else:
        df['type_id'] = param['type_id']

    return df[col_of_interest]   


