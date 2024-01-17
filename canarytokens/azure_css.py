from azure.identity import ClientSecretCredential
from canarytokens.settings import FrontendSettings
from requests import Response, get, put, delete
import logging

frontend_settings = FrontendSettings()

BearerToken = str

def _auth_to_tenant(tenant_id: str) -> BearerToken:
    """
    Tenant that the client app has permissions to, returns a Graph API Bearer token
    """
    cred = ClientSecretCredential(tenant_id, frontend_settings.AZUREAPP_ID, frontend_settings.AZUREAPP_SECRET)
    return cred.get_token('.default').token

def _check_if_custom_branding(token: BearerToken, tenant_id: str) -> bool:
    """
    Checks to see if a tenant has custom branding (and if it's not safe to install our custom CSS)
    Returns: True if there is branding present, false otherwise
    """
    headers = {
        'Accept-Language': '0',
        'Authorization': 'Bearer ' + token
    }
    res: Response = get(f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding", headers=headers)
    # This API returns 404 if there is no corporate branding configured
    return res.status_code != 404

def _check_if_can_install_custom_css(token: BearerToken, tenant_id: str) -> bool:
    """
    Checks to see if a tenant has custom branding (and if it's not safe to install our custom CSS)
    Returns: True if there is branding present, but no existing CSS, False otherwise
    """
    headers = {
        'Accept-Language': '0',
        'Authorization': 'Bearer ' + token
    }
    res: Response = get(f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding", headers=headers)
    logging.error(f"Got {res.status_code} - {res.text}")
    if res.status_code != 200:
        return False
    if res.json().get('customCSSRelativeUrl') is None:
        return True
    return False

def _install_custom_css(token: BearerToken, tenant_id: str, css: str) -> bool:
    """
    Attempts to configure the tenant with the custom css
    Returns: True if successful, False otherwise
    """
    headers = {
        'Content-Type': 'text/css', 
        'Authorization': 'Bearer ' + token,
        'Accept-Language': '0'
    }
    res: Response = put(f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding/localizations/0/customCSS", data=css.encode(), headers=headers)
    return res.status_code == 204

def _delete_self(token: BearerToken) -> bool:
    """
    Tries to delete itself from the tenant to reduce risk
    Returns: True is successful, False otherwise
    """
    res: Response = delete(f"https://graph.microsoft.com/v1.0/servicePrincipals(appId='{frontend_settings.AZUREAPP_ID}')", headers={'Authorization': 'Bearer ' + token})
    return res.status_code == 204

def install_azure_css(tenant_id: str, css: str) -> tuple[bool, str]:
    """
    Main business logic function to install the Azure CSS token into the tenant
    NB: Must be called after the Azure permission consent workflow has occurred
    Returns: True on success, False otherwise
    """
    token = _auth_to_tenant(tenant_id)
    if not _check_if_can_install_custom_css(token, tenant_id):
        return (False, f"Installation failed: your tenant already has custom CSS, or no default branding created, please manually add the CSS to your portal branding.")
    if not _install_custom_css(token, tenant_id, css):
        # Might as well remove ourselves anyways
        _delete_self(token)
        return (False, f"Installation failed: Unable to automatically install the CSS, please manually add the CSS to your portal branding.")
    _delete_self(token)
    return (True, "Successfully installed the CSS into your Azure tenant. Please wait for a few minutes for the changes to propogate; no further action is needed.")

