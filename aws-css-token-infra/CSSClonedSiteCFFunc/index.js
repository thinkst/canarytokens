// Cloudfront Function to check the referrer compared to the expected one base64 encoded into the URI
// Expected uri looks like: /TOKEN_ID/escape(btoa(expected_referrer))/imagename.gif
// Either returns a 1x1 pixel GIF, or forwards it to the token server with the referrer as a GET parameter for reporting

var token_server = 'https://canarytokens.com';

var matching_ref_response = {
    statusCode: 200,
    statusDescription: 'OK',
    headers: {
        'content-type': { value: 'image/gif' }
    },
    body: "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    + "\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00"
    + "\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
};

function handler(event) {
    var uri = event.request.uri.split('/');
    var expected_referrer = '';
    if (uri.length != 4) { // We have a malformed request, return a 404
        return {
            statusCode: 404,
            statusDescription: 'Not Found'
        };
    }
    expected_referrer = String.bytesFrom(uri[2], 'base64url');
    var referer = '';
    var referer_origin = '';
    if ('referer' in event.request.headers) {
        referer = event.request.headers.referer.value;
        if (referer.indexOf('//') >= 0) {
            const pathArray = referer.split( '/' );
            referer_origin = pathArray[2];
        } else {
            referer_origin = referer;
        }
    }

    if (expected_referrer == '')
        console.log("Empty expected_referrer!");
    if (referer == '')
        console.log("Empty/missing Referer header for: " + expected_referrer);

    if (expected_referrer == '' || referer == '' || referer_origin.endsWith(expected_referrer)) { // Happy case where the referer matches   
        return matching_ref_response;
    }
    if (expected_referrer == 'microsoftonline.com' && referer_origin.endsWith('login.microsoft.com')) {
        // Special case of an MS login token came from login.microsoft.com instead of microsoftonline.com
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }
    // Default case of redirecting to the tokens server
    var response = {
        statusCode: 302,
        statusDescription: 'Found',
        headers: {
            'location': { value: token_server + '/' + uri[1] + '/' + uri[3] + '?r=' + referer }
        }
    };
    return response;
}
