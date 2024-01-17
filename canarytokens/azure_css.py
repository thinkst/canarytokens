from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient
from canarytokens.settings import FrontendSettings
from requests import Response

frontend_settings = FrontendSettings()

def _auth_to_tenant(tenant_id: str) -> GraphClient:
    """
    Tenant that the client app has permissions to, returns a Graph API client for that tenant
    """
    cred = ClientSecretCredential(tenant_id, frontend_settings.AZUREAPP_ID, frontend_settings.AZUREAPP_SECRET)
    return GraphClient(credential=cred)

def _check_if_custom_branding(client: GraphClient, tenant_id: str) -> bool:
    """
    Checks to see if a tenant has custom branding (and if it's not safe to install our custom CSS)
    Returns: True if there is branding present, false otherwise
    """
    res: Response = client.get(f"/organization/{tenant_id}/branding")
    # This API returns 404 if there is no corporate branding configured
    return res.status_code != 404

def _install_custom_css(client: GraphClient, tenant_id: str, css: str) -> bool:
    """
    Attempts to configure the tenant with the custom css
    Returns: True if successful, False otherwise
    """
    res: Response = client.put(f"/organization/{tenant_id}/branding/localizations/0/customCSS", data=css.encode(), headers={'Content-Type': 'text/css'})
    return res.status_code == 204

def _delete_self(client: GraphClient) -> bool:
    """
    Tries to delete itself from the tenant to reduce risk
    Returns: True is successful, False otherwise
    """
    res: Response = client.delete(f"/servicePrincipals(appId='{frontend_settings.AZUREAPP_ID}')")
    return res.status_code == 204

def install_azure_css(tenant_id: str, css: str) -> tuple[bool, str]:
    """
    Main business logic function to install the Azure CSS token into the tenant
    NB: Must be called after the Azure permission consent workflow has occurred
    Returns: True on success, False otherwise
    """
    client = _auth_to_tenant(tenant_id)
    if _check_if_custom_branding(client, tenant_id):
        return (False, f"Installation failed: your tenant already has custom CSS, please manually add the CSS to your portal branding.")
    if not _install_custom_css(client, tenant_id, css):
        # Might as well remove ourselves anyways
        _delete_self(client)
        return (False, f"Installation failed: Unable to automatically install the CSS, please manually add the CSS to your portal branding.")
    _delete_self(client)
    return (True, "Successfully installed the CSS into your Azure tenant. Please wait for a few minutes for the changes to propogate; no further action is needed.")

