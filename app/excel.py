import io
import pandas as pd
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files import file


import base64
import io
import urllib.request
from openpyxl import load_workbook

def create_onedrive_directdownload(onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/', '_').replace('+', '-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

def df_from_link(url):
    onedrive_direct_link = create_onedrive_directdownload(url)
    file = urllib.request.urlopen(onedrive_direct_link).read()
    wb = load_workbook(filename=io.BytesIO(file))
    ws = wb['Sheet1']

    print(f"Value in Cell A1: '{ws['A1'].value}'")
    df = pd.read_excel(io.BytesIO(file))
    # df = pd.read_excel(wb)
    print("Dataframe\n", df)
    return df

def df_from_link_credentials(url):
# site_url = "https://1drv.ms/x/s!Apw4mhMkELavg-0qvRdYeLFDQnGLpQ?e=iaymIR&nav=MTVfezA5QzBFQkNFLTRBNUYtNDQwMy05MTNFLTkxNEJGM0JBQjY0Rn0"

# Replace with your username and password
# username = "yourusername"
# password = "yourpassword"

# Initialize the client context
# ctx = ClientContext(site_url).with_credentials(UserCredential(username, password=password))

    ctx = ClientContext(url)
    ctx.load(ctx.web)
    ctx.execute_query()

    # Specify the relative URL of the Excel file
    relative_url = "/sites/documentsite/Documents/filename.xlsx"

    # Open the binary content of the file
    response = file.File.open_binary(ctx, relative_url)

    # Save data to a BytesIO stream
    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)

    # Read the file into a pandas dataframe
    df = pd.read_excel(bytes_file_obj)
    print(df)
