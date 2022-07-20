import requests
import sys
import csv

# Okta API token and domain info
api_token = 'YOUR_API_TOKEN_HERE'
okta_domain = 'YOUR_OKTA_DOMAIN_HERE'

employee_attributes_file = 'YOUR_HRIS_ATTRIBUTE_FILE_NAME_HERE' 

# Set optional arg to push updates to Okta profiles
push_updates_to_okta = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'update_okta':
        push_updates_response = input('Attribute updates will be pushed to Okta, do you want to continue? (Y/N) ').lower()
        if push_updates_response == 'y':
            push_updates_to_okta = True
        else:
            print("Exiting script")
            sys.exit(1)

# [OPTIONAL] Add usernames to this list and the script will ignore them
users_to_ignore = []

# [OPTIONAL] Create lists of valid attributes to compare against with the 'is_valid_attribute' function. Example:
# valid_departments = [
#     'Finance',
#     'Information Systems',
#     'Marketing'
# ]


def is_valid_attribute(valid_attribute_list, attribute):
    if attribute in valid_attribute_list:
        return True
    else:
        print(f'"{attribute}" is not a valid attribute value')
        failed_records.append(f'{username} - "{attribute}" is not a valid attribute value')
        return False


def compare_attributes(okta_attribute_name, hris_attribute_value):
    okta_attribute_value = okta_user.get("profile").get(okta_attribute_name, "")
    if hris_attribute_value != okta_attribute_value:
        old_attributes[okta_attribute_name] = okta_attribute_value
        new_attributes[okta_attribute_name] = hris_attribute_value


def get_user(user):
    url = f"https://{okta_domain}/api/v1/users/{user}"
    try:
        response = session.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return None


def update_user(user, attribute_dict):
    url = f"https://{okta_domain}/api/v1/users/{user}"
    data = {
        "profile": attribute_dict
    }
    try:
        response = session.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error Code: {response.json()['errorCode']}")
        print(f"Error Code: {response.json()['errorSummary']}")
        return None


# User records with an error
failed_records = []

# Log all changed attributes for all users
diff_attributes_history = []

# Create requests session to speed up API calls to Okta
session = requests.session()
headers = {
    'Accept': 'application/json',
    'Content-type': 'application/json',
    'Authorization': f'SSWS {api_token}' 
}
session.headers.update(headers)


# Process each row in the CSV file
with open(employee_attributes_file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    records = list(csv_reader)
    print(f"Total records in file: {len(records)}")
    for i, row in enumerate(records):
        # if i == 1: # Uncomment to test with 1 record then stop
        #     break
        
        username = row['Email'] # [REQUIRED] Specify the column name with the Okta username #############################
        print(f"Processing {username}...")

        # Ignore certain users that you do not want to sync to Okta
        if username in users_to_ignore:
            print(f"{username} in ignore list, will not process")
            continue

        # Lookup user in Okta to compare attributes
        okta_user = get_user(username)
        if okta_user:
            if okta_user['status'] == 'DEPROVISIONED':
                failed_records.append(f'{username} - Deactivated in Okta')
            else:
                old_attributes = {}
                new_attributes = {}

                ###################################### How to compare attributes: #######################################
                # 1. Add 'compare_attributes' function for each set of attributes to compare
                #    a. Specify the Okta profile attribute name to compare
                #    b. Specify the CSV column name to compare
                # 2. [OPTIONAL] Use 'is_valid_attribute' function to validate attribute values against a pre-defined list              
                #########################################################################################################

                # [REQUIRED] Examples to compare Okta attributes to CSV rows: 
                # compare_attributes('title', row['Title'])
                # compare_attributes('organization', row['Organization'])
                # compare_attributes('manager', row['Manager'])

                # [OPTIONAL] Example to validate attributes against a pre-defined list before comparison:
                # if is_valid_attribute(valid_departments, row['Department']):
                #     compare_attributes('department', row['Department'])

                if len(new_attributes) > 0:
                    diff_attributes = { username: { 'old': old_attributes, 'new': new_attributes } }
                    diff_attributes_history.append(diff_attributes)

                    if push_updates_to_okta is True:
                        print(f'Pushing new attributes to Okta for {username}')
                        update_user(username, new_attributes)

        else:
            failed_records.append(f'{username} - Does not exist in Okta')
        

if len(diff_attributes_history) > 0:
    print()
    print(f"Diff Attributes ({len(diff_attributes_history)}/{len(records)}):")
    for user in diff_attributes_history:
        print(user)
else:
    print('No attribute diffs detected!')

if len(failed_records) > 0:
    print()
    print(f"Failed Records ({len(failed_records)}/{len(records)}):")
    for record in failed_records:
        print(record)
