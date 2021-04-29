# SMART on FHIR python client demo
> Demo the python SMART on FHIR client.


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pete88b/smart-on-fhir-client-py-demo/blob/main/index.ipynb)

Using [client-py](https://github.com/smart-on-fhir/client-py), this project aims to provide some simple demos to help people get started with the python client.

This is also a learning excercise - so if you see anything that could be done better, please let us know.

## Getting started

Note: This project `pip install`s [the latest client-py code](https://github.com/smart-on-fhir/). We could install [this commit](https://github.com/smart-on-fhir/client-py/commit/6047277daa31f10931e44ed19e92128298cdb64b) if breaking changes are introduced.

We're using the latest client-py code becuase [PyPI history](https://pypi.org/project/fhirclient/#history) shows the last available release was `3.2.0` 2018-02-06 ... and we want to use some of the new FHIR R4 features.

### If you want to run everything on your own machine

#### Clone this project and set-up a conda environment

```
git clone https://github.com/pete88b/smart-on-fhir-client-py-demo.git
cd smart-on-fhir-client-py-demo
conda create -n smart-on-fhir-client-py-demo python==3.8 -y
conda activate smart-on-fhir-client-py-demo
pip install -r requirements.txt
nbdev_install_git_hooks
```

#### Start jupyter 

If you have already created and activated your conda environment, you can start a notebook server with;

```
jupyter notebook
```

### If you want to run demo notebooks using google colab

- Open [this notebook](https://colab.research.google.com/github/pete88b/smart-on-fhir-client-py-demo/blob/main/index.ipynb) in colab
- We'll add more demo notebooks when they are ready (o:

The cell below will install the fhirclient if you're running in colab.

## Define `print_resource` - a generic way to print a resource

We use `print_resource(procedure)` etc, rather than looking at specific resource details with code like `procedure.code.coding[0].as_json()`, so that the demos won't fail if resouces are missing specific content.

```python
def print_resource(resource, indent=None, length=100):
    s=json.dumps(resource.as_json(), indent=indent)
    print(s[:length-4]+' ...' if len(s)>length else s)
```

## Client use

Lets start by trying to make something like the code examples in [client-py README.md](https://github.com/smart-on-fhir/client-py) work.

These docs refer to the FHIR server https://fhir-open-api-dstu2.smarthealthit.org which is probably not running any more.

The following demos will use http://wildfhir4.aegis.net/fhir4-0-0 - which is one of the "open" servers listed on the [public test servers wiki](https://confluence.hl7.org/display/FHIR/Public+Test+Servers). If you'd like to try other servers, feel free to change `api_base` &darr;

```python
settings = {
    'app_id': 'my_web_app',
    'api_base': 'http://wildfhir4.aegis.net/fhir4-0-0'
}
```

### Read Data from Server

Note: We use `Resource ID` `'f001'` rather than `'hca-pat-1'` - which could be found with a [Aegis FHIR4-0-0 GUI](http://wildfhir4.aegis.net/fhir4-0-0-gui/index.jsf) search. 

If the `p.Patient.read` call raises `FHIRNotFoundException: <Response [404]>`, it probably means that the `Resource ID` does not exist on the server.

```python
from fhirclient import client
smart = client.FHIRClient(settings=settings)

import fhirclient.models.patient as p
patient = p.Patient.read('f001', smart.server)
print('Birth Date', patient.birthDate.isostring)
print('Patient Name', smart.human_name(patient.name[0]))
```

    Birth Date 1994-11-17
    Patient Name Pieter van de Heuvel, MSc
    

Note: We could show the full patient resource as JSON with `patient.as_json()` - which should give us the same data as `GET` http://wildfhir4.aegis.net/fhir4-0-0/Patient/f001

## If this is a protected server ...

I'm going to ignore authorization for now as `smart.authorize_url` and `smart.prepare()` raise exceptions with most of the FHIR servers I've tried.

## You can work with the `FHIRServer` class directly, without using `FHIRClient`, but this is not recommended

```python
from fhirclient import server
smart = server.FHIRServer(None, settings['api_base'])
import fhirclient.models.patient as p
patient = p.Patient.read('f001', smart)
patient.name[0].given
```




    ['Pieter']



## Search Records on Server

Note: I think `GET` http://wildfhir4.aegis.net/fhir4-0-0/Patient/f001/Procedure should work

```python
smart = client.FHIRClient(settings=settings)
import fhirclient.models.procedure as p
search = p.Procedure.where(struct={'subject': 'f001', 'status': 'completed'})
procedures = search.perform_resources(smart.server)
for procedure in procedures:
    print_resource(procedure)
#     print(procedure.id, procedure.code.coding[0].as_json())
```

    {"id": "f001", "meta": {"lastUpdated": "2020-11-15T19:51:31.947-05:00", "security": [{"code": "H ...
    {"id": "f002", "meta": {"lastUpdated": "2020-11-15T19:51:32.153-05:00", "security": [{"code": "H ...
    {"id": "f003", "meta": {"lastUpdated": "2020-11-15T19:51:32.574-05:00", "security": [{"code": "H ...
    {"id": "f004", "meta": {"lastUpdated": "2020-11-15T19:51:32.868-05:00", "security": [{"code": "H ...
    

### To include the resources referred to by the procedure via `subject` in the results

Before calling `search.include('subject')`, `search.construct()` gave us 
- `Procedure?subject=f001&status=completed`

After calling `search.include('subject')`, `search.construct()` gave us 
- `Procedure?subject=f001&status=completed&_include=Procedure:subject`

so ... `search.perform_resources` will now give us a list of procedures _and patients_ that the procedures refer to.

```python
search = search.include('subject')
```

```python
procedures = search.perform_resources(smart.server)
for resource in procedures:
    print(resource.__class__.__name__)
    print_resource(resource)
```

    Procedure
    {"id": "f001", "meta": {"lastUpdated": "2020-11-15T19:51:31.947-05:00", "security": [{"code": "H ...
    Patient
    {"id": "f001", "meta": {"lastUpdated": "2021-02-01T14:47:43.050-05:00", "versionId": "5"}, "text ...
    Procedure
    {"id": "f002", "meta": {"lastUpdated": "2020-11-15T19:51:32.153-05:00", "security": [{"code": "H ...
    Procedure
    {"id": "f003", "meta": {"lastUpdated": "2020-11-15T19:51:32.574-05:00", "security": [{"code": "H ...
    Procedure
    {"id": "f004", "meta": {"lastUpdated": "2020-11-15T19:51:32.868-05:00", "security": [{"code": "H ...
    

we could check the type of resource and run specific code for each type with something like

```
for resource in procedures:
    if isinstance(resource, p.Procedure):
        # process Procedure here
        print(resource.id, resource.code.coding[0].as_json())
    else:
        # process Patient here
        print('Patient', resource.id)
```

### To include the MedicationAdministration resources which refer to the procedure via `partOf`

We probably won't find any `MedicationAdministration`s ...

```python
import fhirclient.models.medicationadministration as m
search = search.include('partOf', m.MedicationAdministration, reverse=True)
procedures = search.perform_resources(smart.server)
for resource in procedures:
    print(resource.__class__.__name__)
    print_resource(resource)
```

    Procedure
    {"id": "f001", "meta": {"lastUpdated": "2020-11-15T19:51:31.947-05:00", "security": [{"code": "H ...
    Patient
    {"id": "f001", "meta": {"lastUpdated": "2021-02-01T14:47:43.050-05:00", "versionId": "5"}, "text ...
    Procedure
    {"id": "f002", "meta": {"lastUpdated": "2020-11-15T19:51:32.153-05:00", "security": [{"code": "H ...
    Procedure
    {"id": "f003", "meta": {"lastUpdated": "2020-11-15T19:51:32.574-05:00", "security": [{"code": "H ...
    Procedure
    {"id": "f004", "meta": {"lastUpdated": "2020-11-15T19:51:32.868-05:00", "security": [{"code": "H ...
    

to get the raw Bundle instead of resources only, you can use:

```python
bundle = search.perform(smart.server)
# we'll just show the 1st 200 characters of the bundle (after converting to JSON)
print_resource(bundle, indent=2, length=200)
```

    {
      "id": "5d16c5f5-8fa0-4d4a-8510-b592d17d833e",
      "meta": {
        "lastUpdated": "2021-04-29T09:40:02.182-04:00",
        "versionId": "1"
      },
      "entry": [
        {
          "fullUrl": "http://wildfhir4.ae ...
    

## Data Model Use

```python
import fhirclient.models.patient as p
import fhirclient.models.humanname as hn
patient = p.Patient({'id': 'patient-1'})
print(patient.as_json()) # prints `patient-1`

name = hn.HumanName()
name.given = ['Peter']
name.family = 'Parker'
patient.name = [name]
print(patient.as_json()) # prints patient's JSON representation, now with id and name

name.given = 'Peter'
try:
    patient.as_json()
except Exception as ex:
    print('patient.as_json() raised', type(ex),'with message')
    print(ex)
```

    {'id': 'patient-1', 'resourceType': 'Patient'}
    {'id': 'patient-1', 'name': [{'family': 'Parker', 'given': ['Peter']}], 'resourceType': 'Patient'}
    patient.as_json() raised <class 'fhirclient.models.fhirabstractbase.FHIRValidationError'> with message
    {root}:
      name.0:
        given:
          Expecting property "given" on <class 'fhirclient.models.humanname.HumanName'> to be list, but is <class 'str'>
    

## Initialize from JSON file

Create a folder to save json data to

```python
data_path=Path('data')
data_path.mkdir(exist_ok=True)
```

Create a file by reading a patient from the server and writing as json

```python
import fhirclient.models.patient as p

smart = client.FHIRClient(settings=settings)
patient = p.Patient.read('f001', smart.server)

with open(data_path/'patient.json', 'w') as f:
    f.write(json.dumps(patient.as_json(), indent=2))
```

Now we can read the json file and initialize a `Patient`

```python
with open(data_path/'patient.json', 'r') as h:
    pjs = json.load(h)
patient = p.Patient(pjs)
patient.name[0].given
```




    ['Pieter']



## Run the flask app

51_flask_client_py_readme.ipynb creates a Flask app like [the client-py demo flask app](https://github.com/smart-on-fhir/client-py/blob/master/flask_app.py).

You can run `python smart_on_fhir_client_py_demo/flask_client_py_readme.py` from the command line and hit 
- http://localhost:8000/

This is a little different to the client-py demo;
- It's set-up to run against http://wildfhir4.aegis.net/fhir4-0-0 which is a no-auth server
- It'll allow you to select a patient if you're running against a no-auth server
    - http://localhost:8000/logout
- It'll allow you to pass a patient ID as a URL paramter
    - http://localhost:8000/?patient_id=patient456
- Note: It hasn't been tested with an auth server yet.
