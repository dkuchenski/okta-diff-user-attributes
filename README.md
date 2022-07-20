## Purpose

This script will diff user attributes from a CSV file to Okta user profiles. Although Okta already has HR-as-a-Master functionality that syncs user attributes, sometimes this isn't possible to use for a variety of reasons (you have an unsupported HRIS system, or you don't have HRaaM licensing) OR maybe you want more control over attribute syncing. This script allows you to choose the exact attributes to sync, validate the attribute against a pre-defined list before syncing, or even ignore certain users.

By default, when the script is run it will only output any differences from the CSV file and the Okta user profile for the configured attributes. This allows you to see the differences before making any changes. You can then run the script again, adding `update_okta` to the command and the script will also update the Okta user profile.

## Requirements

1. Have python3 installed
2. Have the requests library installed (pip install requests)

## Setup

1. There are several variables needed to connect to your Okta account. To start, you'll need to provide the following in the script:

    ```
    api_token = 'YOUR_API_TOKEN_HERE'
    okta_domain = 'YOUR_OKTA_DOMAIN_HERE'
    ```
    The required API permissions are simple. If you are just using the script to diff attributes, it only needs read-only access to Okta user profiles. In order to use `update_okta` and write attributes to Okta, the API key needs write permissions to Okta user profiles.

2. Next, provide the name of the CSV file with the correct attributes (usually an export from your HRIS system):

    ```
    employee_attributes_file = 'YOUR_HRIS_ATTRIBUTE_FILE_NAME_HERE.csv'
    ```
3. Specify the column name used to identify the Okta user for the *username* variable. By default, it is set as 'Email', but this should be replaced with whatever your column name is (case sensitive):
    ```
    username = row['Email']
    ```
4. Finally, specify which CSV attributes should be compared to which Okta attributes using the *compare_attributes* function:
    ```
    # This compares the Okta 'title' profile attribute to the CSV 'Title' column
    compare_attributes('title', row['Title'])
    # This compares the Okta 'organization' profile attribute to the CSV 'Organization' column
    compare_attributes('organization', row['Organization'])
    # This compares the Okta 'manager' profile attribute to the CSV 'Manager' column
    compare_attributes('manager', row['Manager'])
    ```
    The *compare_attributes* function expects two inputs:
    - The Okta profile attribute name
    - The CSV attribute column name

## Run

To only compare the attributes specified, run:
```
python3 diff_user_attributes.py
```
This will show any attributes that don't match in Okta so that you can audit before making any changes. It will also provide a list of users that exist in the CSV but do not exist in Okta. Example output:
```
% python3 diff_user_attributes.py
Total records in file: 2
Processing test.user@examplecompany.com...
Processing test.user2@examplecompany.com...

Diff Attributes (2/2):
{'test.user@examplecompany.com': {'old': {'title': '', 'organization': 'Small Company', 'manager': ''}, 'new': {'title': 'Senior Analyst', 'organization': 'Big Company', 'manager': 'James Test'}}}
{'test.user2@examplecompany.com': {'old': {'title': 'Sr Manager', 'manager': 'John Smith'}, 'new': {'title': 'Director', 'manager': 'Ben Test'}}}
```

To compare and push attribute changes to Okta, run:
```
python3 diff_user_attributes.py update_okta
```
Example output when pushing changes:
```
% python3 diff_user_attributes.py update_okta
Attribute updates will be pushed to Okta, do you want to continue? (Y/N) y
Total records in file: 2
Processing test.user@examplecompany.com...
Pushing new attributes to Okta for test.user@examplecompany.com
Processing test.user2@examplecompany.com...
Pushing new attributes to Okta for test.user2@examplecompany.com

Diff Attributes (2/2):
{'test.user@examplecompany.com': {'old': {'title': '', 'organization': 'Small Company', 'manager': ''}, 'new': {'title': 'Senior Analyst', 'organization': 'Big Company', 'manager': 'James Test'}}}
{'test.user2@examplecompany.com': {'old': {'title': 'Sr Manager', 'manager': 'John Smith'}, 'new': {'title': 'Director', 'manager': 'Ben Test'}}}
```

## Optional

### Users to Ignore
You can add usernames to the *users_to_ignore* list, and the script will not compare or push changes for them. Example:

```
users_to_ignore = [
    'test.user@mycompany.com',
    'test.user2@mycompany.com'
]
```
### Attribute Validation
Sometimes it is useful to validate attributes before pushing any changes. For example, if HR creates a new department, the Okta admin may need to create new groups/group rules for the new department. By keeping a static list of valid departments in this script, the new department value will not be pushed until added to the valid department list. Example:

1. First, create the list of valid/expected attributes:
    ```
    valid_departments = [
        'Finance',
        'Information Systems',
        'Marketing'
    ]
    ```
2. Second, add the *is_valid_attribute* if statement as a condition before the *compare_attributes* function:
    ```
    if is_valid_attribute(valid_departments, row['Department']):
        compare_attributes('department', row['Department'])
    ```