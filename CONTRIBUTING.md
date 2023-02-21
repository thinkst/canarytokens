

# Adding a new token
When adding a new token here are a set of steps / checkboxes that are useful to follow.
1. Add a file `canarytokens/{new_token}.py`. Use this file to define all `new_token` specific logic.
2. Create tests in `tests/units/test_new_token.py`. Check that a significant amount of this token specific code is covered by test.
Use: `coverage run --source=./canarytokens/{new_token}.py -m pytest tests/units/test_new_token.py` and view coverage: `coverage report -m`
3. Adding `new_token` models. Add `{new_token_type}TokenRequest`, `{new_token_type}TokenResponse` and `{new_token_type}` to `canarytokens/models.py::Class TokenTypes`.
Add `{new_token_type}TokenHit` and `{new_token_type}TokenHistory`.
Finally add these as entries to `AnyTokenHit, AnyTokenHistory, AnyTokenRequest, AnyTokenResponse`. This allows `parse_obj_as(AnyTokenXXX, data)` to return hydrated object.
4. Token creation happens in `./frontend/app.py`. Add a `create_response` handler. This handler should hold all Token specific creation logic.
example:
```
@create_response.register
def _(
    token_request_details: {new_token_type}TokenRequest,canarydrop:Canarydrop,
)->{new_token_type}TokenResponse:
    ...
    # Save canarydrop with token specific details
```
5. Download happens in `./frontend/app.py`. Add a `create_download_response` handler. This handler should hold all the token download specifics. Create a `Download{new_token_type}Request` and `Download{new_token_type}Response`
Example:
```
@create_download_response.register
def _(download_request_details:DownloadCMDRequest, canarydrop: Canarydrop)->DownloadCMDResponse:
    """Creates a download response for CMD token.
    This holds a plain text `{token_value}.reg` file.
    """
    return DownloadCMDResponse(...)
```

That should be all that is needed to create a new token.
