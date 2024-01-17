// Cloudfront Function to check the referrer compared to the expected one base64 encoded into the URI
// Expected uri looks like: /TOKEN_ID/escape(btoa(expected_referrer))/imagename.gif
// Either returns a 1x1 pixel GIF, or forwards it to the token server with the referrer as a GET parameter for reporting

var token_server = 'https://canarytokens.com';

function handler(event) {
    var uri = event.request.uri.split('/');
    var expected_referrer = String.bytesFrom(uri[2], 'base64url');
    if ('referer' in event.request.headers)
        var referer = event.request.headers.referer.value;
    else
        var referer = '';
    
    if (referer == '' || referer.indexOf(expected_referrer) >= 0) { // Happy case where the referer matches
        var response = {
            statusCode: 200,
            statusDescription: 'OK',
            headers: {
                'content-type': { value: 'image/gif' }
            },
            body: "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            + "\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00"
            + "\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
        };
        return response;
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