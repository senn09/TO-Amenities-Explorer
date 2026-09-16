import requests
import pandas as pd
from io import StringIO

base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
        
params =    [{ 
                "id": "library-branch-general-information",
                "type_id": 1,
                "col_name_transform": [
                    ('BranchName', 'name'),
                    ('Address', 'address'),
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
                    ('ASSET_NAME', 'name'),
                    ('ADDRESS', 'address'),
                    ('TYPE', 'type_id'),
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

    # there is only two columns atm but I think doing this systematically would be good practice down the line
    col_of_interest = [pair[1] for pair in param['col_name_transform']]
    if param['type_id'] == 2:
        df['type_id'].replace({'Park': 2, 'Community Centre': 3, 'Civic Centre': 4})
    else:
        df['type_id'] = param['type_id']

    print(f'formatted {param['id']}')
    return df[col_of_interest]   


