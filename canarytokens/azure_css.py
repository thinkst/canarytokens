from azure.identity import ClientSecretCredential
from canarytokens.settings import FrontendSettings
from requests import Response, get, put, delete, post
from time import sleep
from cssutils.css import CSSStyleRule

import logging
import cssutils
import enum

frontend_settings = FrontendSettings()

BearerToken = str

EntraTokenErrorAccessDenied = "access_denied"

ENTRA_BASE_REDIRECT_URL = "/nest/entra/{status}"


class EntraTokenStatus(enum.Enum):
    ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY = "has_custom_css_already"
    ENTRA_STATUS_ERROR = "error"
    ENTRA_STATUS_SUCCESS = "success"
    ENTRA_STATUS_NO_ADMIN_CONSENT = "no_admin_consent"


LEGACY_ENTRA_STATUS_MAP = {
    EntraTokenStatus.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY.value: "Installation failed: your tenant already has a conflicting custom CSS, please manually add the CSS to your portal branding. We have uninstalled our application from your tenant, revoking all of our permissions.",
    EntraTokenStatus.ENTRA_STATUS_ERROR.value: "Installation failed: Unable to automatically install the CSS, please manually add the CSS to your portal branding. We have uninstalled our application from you tenant, revoking all of our permissions.",
    EntraTokenStatus.ENTRA_STATUS_SUCCESS.value: "Successfully installed the CSS into your Azure tenant. Please wait for a few minutes for the changes to propagate; no further action is needed. We have uninstalled our application from your tenant, revoking all of our permissions.",
    EntraTokenStatus.ENTRA_STATUS_NO_ADMIN_CONSENT.value: "Installation failed due to lack of sufficient granted permissions. We have uninstalled our application from your tenant, revoking all of our permissions.",
}


def _auth_to_tenant(tenant_id: str) -> BearerToken:
    """
    Tenant that the client app has permissions to, returns a Graph API Bearer token
    """
    cred = ClientSecretCredential(
        tenant_id, frontend_settings.AZUREAPP_ID, frontend_settings.AZUREAPP_SECRET
    )
    return cred.get_token(".default").token


def _check_if_custom_branding(token: BearerToken, tenant_id: str) -> bool:
    """
    Checks to see if a tenant has custom branding (and if it's not safe to install our custom CSS)
    Reference: https://learn.microsoft.com/en-us/graph/api/organizationalbranding-get
    Returns: True if there is branding present, false otherwise
    """
    headers = {"Accept-Language": "0", "Authorization": "Bearer " + token}
    res: Response = get(
        f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding",
        headers=headers,
    )
    # This API returns 404 if there is no corporate branding configured
    return res.status_code != 404


def _check_existing_body_background(css: str) -> bool:
    """
    Parses an existing CSS file to see if there is a conflicting rule
    Returns True if there is a conflicting rule, False otherwise
    """
    css_rules: list[CSSStyleRule] = cssutils.parseString(css)
    for rule in css_rules:
        if rule.selectorText == "body" and "background" in rule.style.cssText:
            return True
    return False


def _check_if_can_install_custom_css(
    token: BearerToken, tenant_id: str
) -> tuple[bool, str]:
    """
    Checks to see if a tenant has custom branding (and if it's not safe to install our custom CSS)
    References:
        - https://learn.microsoft.com/en-us/graph/api/organizationalbranding-get
        - https://learn.microsoft.com/en-us/graph/api/resources/organizationalbrandingproperties
    Returns: A tuple of (True, css) if we can safely install a custom CSS, False otherwise
    """
    headers = {"Accept-Language": "0", "Authorization": "Bearer " + token}
    res: Response = get(
        f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding",
        headers=headers,
    )
    if res.status_code == 404:  # There is no branding at all
        return (True, "")
    if res.status_code != 200:  # Other error
        return (False, "")
    if (
        res.json().get("customCSSRelativeUrl") is None
    ):  # Is there another CSS? If not then we can install!
        return (True, "")
    # There is an existing CSS, let's check for compatibility
    res: Response = get(
        f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding/localizations/0/customCSS",
        headers=headers,
    )
    if res.status_code == 200:
        return (not _check_existing_body_background(res.text), res.text)
    return (False, "")


def _install_custom_css(token: BearerToken, tenant_id: str, css: str) -> bool:
    """
    Attempts to configure the tenant with the custom css
    References:
        - https://learn.microsoft.com/en-us/graph/api/organizationalbranding-update
        - https://learn.microsoft.com/en-us/graph/api/organizationalbranding-post-localizations
    Returns: True if successful, False otherwise
    """
    headers = {"Authorization": "Bearer " + token, "Accept-Language": "0"}
    if not _check_if_custom_branding(token, tenant_id):
        # If we need to create a default OrganizationalBranding object, we set a blank string to a single space to create it
        logging.error("Creating a new default organizationalBranding object...")
        res: Response = post(
            f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding/localizations/",
            json={"usernameHintText": " "},
            headers=headers,
        )
        if res.status_code != 201:
            logging.error(
                f"Unable to create OrganizationalBranding object: {res.status_code} - {res.text}"
            )
            return False
        sleep(5)  # Give the Graph API a second to recognize it's built

    headers["Content-Type"] = "text/css"
    res: Response = put(
        f"https://graph.microsoft.com/v1.0/organization/{tenant_id}/branding/localizations/0/customCSS",
        data=css.encode(),
        headers=headers,
    )
    if res.status_code != 204:
        logging.error(f"Unable to add customCSS: {res.status_code} - {res.text}")
    return res.status_code == 204


def _delete_self(token: BearerToken) -> bool:
    """
    Tries to delete itself from the tenant to reduce risk
    Returns: True is successful, False otherwise
    """
    res: Response = delete(
        f"https://graph.microsoft.com/v1.0/servicePrincipals(appId='{frontend_settings.AZUREAPP_ID}')",
        headers={"Authorization": "Bearer " + token},
    )
    return res.status_code == 204


def install_azure_css(tenant_id: str, css: str) -> EntraTokenStatus:
    """
    Main business logic function to install the Azure CSS token into the tenant
    NB: Must be called after the Azure permission consent workflow has occurred
    Returns: True on success, False otherwise
    """
    token = _auth_to_tenant(tenant_id)
    (check, existing_css) = _check_if_can_install_custom_css(token, tenant_id)
    if not check:
        return EntraTokenStatus.ENTRA_STATUS_HAS_CUSTOM_CSS_ALREADY

    if not _install_custom_css(token, tenant_id, existing_css + css):
        # Might as well remove ourselves anyways
        _delete_self(token)
        return EntraTokenStatus.ENTRA_STATUS_ERROR

    _delete_self(token)

    return EntraTokenStatus.ENTRA_STATUS_SUCCESS


def build_entra_redirect_url(status):
    return ENTRA_BASE_REDIRECT_URL.format(status=status)


# Other reference that's of note but not linked to from the other Graph API docs: https://learn.microsoft.com/en-us/graph/api/organizationalbrandinglocalization-delete
