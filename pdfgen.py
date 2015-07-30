import zlib
from cStringIO import StringIO
import re
import sys
import random

import settings

PDF_FILE=settings.CANARY_PDF_TEMPLATE
STREAM_OFFSET=settings.CANARY_PDF_TEMPLATE_OFFSET

def _substitute_stream(header=None, stream=None, search='abcdefghijklmnopqrstuvwxyz.zyxwvutsrqponmlkjihgfedcba.aceegikmoqsuwy.bdfhjlnprtvxz', replace=None):
    #Ohhhh, this is nasty. Instead of trying to get the xref positions right,
    #we're going to brute-force a URL that's the right size after compression.
    #Give up after 1000 attempts.
    old_len = len(stream)
    candidate_stream = zlib.compress(zlib.decompress(stream).replace(search, replace))
    count = 1
    while len(candidate_stream) < old_len and count < 1000:
        padding = ''.join([ chr(random.randrange(65,90)) for x in range(0,count)])
        candidate_stream = zlib.compress(zlib.decompress(stream).replace(search, replace+'/'+padding))
        count += 1

    #header should be the same size, no need to recalc
    #header = re.sub(r'Length [0-9]+', 'Length {len}'.format(len=len(new_stream)), header)
    if old_len != len(candidate_stream):
        raise Exception('Dammit, new PDF is too big ({new_len} > {old_len})'
                            .format(new_len=len(candidate_stream), old_len=old_len))

    return (header, candidate_stream)

def make_canary_pdf(hostname=None):
    f = open(PDF_FILE, 'r')
    contents = f.read()
    f.close()

    stream_size = int(re.match(r'.*\/Length ([0-9]+)\/.*', contents[STREAM_OFFSET:]).group(1))
    stream_start = STREAM_OFFSET+contents[STREAM_OFFSET:].index('stream\r\n')+8
    stream_header = contents[STREAM_OFFSET:stream_start]
    stream = contents[stream_start:stream_start+stream_size]

    (stream_header, stream) = _substitute_stream(header=stream_header,
                                                 stream=stream,
                                                 replace=hostname)

    output = StringIO()
    output.write(contents[0:STREAM_OFFSET])
    output.write(stream_header)
    output.write(stream)
    output.write(contents[stream_start+stream_size:])
    new_contents = output.getvalue()
    output.close()

    return new_contents


