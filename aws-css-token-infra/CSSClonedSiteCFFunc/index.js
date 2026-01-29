// Cloudfront Function to check the referrer compared to the expected one base64 encoded into the URI
// Expected uri looks like: /TOKEN_ID/escape(btoa(expected_referrer))/imagename.gif
// Either returns a 1x1 pixel GIF, or forwards it to the token server with the referrer as a GET parameter for reporting

const querystring = require('querystring');

import cf from 'cloudfront';
const kvsId = "KVS_ID";
const kvsHandle = cf.kvs(kvsId);

const token_server = 'https://canarytokens.com';

const matching_ref_response = {
    statusCode: 200,
    statusDescription: 'OK',
    headers: {
        'content-type': { value: 'image/gif' },
        'cache-control': { value: 'no-store' },
        'cross-origin-resource-policy': { value: 'cross-origin' }
    },
    body: "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
    + "\xff\xff\xff\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00"
    + "\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b"
};

async function handler(event) {
    const decoder = new TextDecoder();
    const uri = event.request.uri.split('/');
    var expected_referrer = '';
    if (uri.length != 4) { // We have a malformed request, return a 404
        return {
            statusCode: 404,
            statusDescription: 'Not Found'
        };
    }
    const ja4 = event.request.headers['cloudfront-viewer-ja4-fingerprint'] ? event.request.headers['cloudfront-viewer-ja4-fingerprint'].value : 'none';
    const user_agent = event.request.headers['user-agent'] ? event.request.headers['user-agent'].value : 'none';
    const token_id = uri[1];
    const exclusions_exist = await kvsHandle.exists(token_id);
    expected_referrer = decoder.decode(Buffer.from(uri[2], 'base64url'));
    var referer = '';
    var referer_origin = '';
    if ('referer' in event.request.headers) {
        referer = event.request.headers.referer.value;
        if (referer.indexOf('//') >= 0) {
            if (referer.startsWith('fbapp://')) {
                // Global ignore any FB app schemes
                return matching_ref_response;
            }
            const pathArray = referer.split( '/' );
            referer_origin = pathArray[2];
        } else {
            referer_origin = referer;
        }
        if (referer_origin.indexOf(':') >= 0) {
            // There is a port in the Referer (e.g., blah.com:443)
            // Remove the port to get the raw origin domain
            var domain_port = referer_origin.split(':');
            referer_origin = domain_port[0];
        }
        if (referer_origin.endsWith(".")) {
            // According to the DNS spec in RFC 1034 domains always end with a trailing "." (dot)
            // Most tools simply strip this out.
            referer_origin = referer_origin.slice(0, -1);
        }
    }

    const redirect_response = {
        statusCode: 302,
        statusDescription: 'Found',
        headers: {
            'location': { value: token_server + '/' + token_id + '/' + uri[3] + '?' + querystring.stringify({"r": referer, "ja4": ja4}) }
        }
    };

    if (expected_referrer == '')
        console.log("Empty expected_referrer!");
    if (referer == '')
        console.log("Empty/missing Referer header for: " + expected_referrer);

    if (expected_referrer == '' || referer == '' || referer_origin.endsWith(expected_referrer) || referer_origin.endsWith(event.context.distributionDomainName)) {
        // Happy case where the referer matches
        if (expected_referrer.endsWith('microsoftonline.com') && user_agent.startsWith('Mozilla/') && ja4 == 'SUSPICIOUS_JA4_VALUE') {
            console.log("M365 SOFT ALERT ON SUSPICIOUS JA4: " + ja4 + " with UA: " + user_agent);
            // return redirect_response; // Soft alerting only for now
        }
        return matching_ref_response;
    }

    if (expected_referrer.endsWith('microsoftonline.com') && referer_origin.endsWith('login.microsoft.com')) {
        // Special case of an MS login token came from login.microsoft.com instead of microsoftonline.com
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }
    if (expected_referrer.endsWith('microsoftonline.com') && referer_origin.endsWith('login.microsoftonline.us')) {
        // Special case of an MS login token came from the US Gov Azure login
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }
    if (expected_referrer.endsWith('microsoftonline.com') && referer_origin.endsWith('autologon.microsoftazuread-sso.com')) {
        // Special case of an MS login token came from the Azure seamless SSO login instead of microsoftonline.com
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }
    if (expected_referrer.endsWith('microsoftonline.com') && (referer_origin.endsWith('aadcdn.msauthimages.net') || referer_origin.endsWith('aadcdn.msftauthimages.net') || referer_origin.endsWith('login.windows.net'))) {
        // Special case of an MS login token came from the Azure CDN or a MS Windows domain
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }
    if (expected_referrer.endsWith('microsoftonline.com') && referer_origin.endsWith('.office.com')) {
        // Special case of an MS login token coming from an office.com URL
        // We still want to treat this as a good login since the referer is a valid MS domain
        return matching_ref_response;
    }

    if (exclusions_exist) {
        const exclusions = (await kvsHandle.get(token_id)).split(',');
        for (var i = 0; i < exclusions.length; i++) {
            if (referer_origin.endsWith(exclusions[i]))
                return matching_ref_response;
        }
    }

    // Default case of redirecting to the tokens server
    return redirect_response;
}
