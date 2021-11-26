# Django-DocuSign
Django wrapper app for DocuSign functionalities

`pip install django-docusign`

## Running Tests
We have a unit test defined for testing the los application.
This can be executed using the below command.

```
python manage.py test
```

## Usage
In order to use the system you must add los_docusign.apps.LosDocusignConfig to your installed apps in your settings.py file.
```python
INSTALLED_APPS = [
    'los_docusign'
]
```

Test file has the sample implementation of the test_app

## Functions in client.py
1.  generate_docusign_preview_url(dict)
    
    Params required in dict:
    -   "envelope_id"
    -   "authentication_method"
    -   "email"
    -   "user_name"
    -   "client_user_id"
    -   "return_url"

2. create_envelope(payload)

    Params required:
    -   DocuSign payload in JSON format

3. download_docusign_document(dict)

    Params required in dict:
    -   "envelope_id"
    -   "doc_download_option"
        -   Valid Values:
            1. archive - If the document to be downloaded in zip format.
            2. combined - If the document to be downloaded as a combined document.
