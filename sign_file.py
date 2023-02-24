import sys
import getopt
import os
import tempfile
import shutil

def authenticode_sign_binary(token, inputfile, outputfile):
    try:
        tmpdir = tempfile.mkdtemp()

        os.system('cp root-ca.conf {tmpdir}/root-ca.conf'.format(tmpdir=tmpdir))

        f = open('{tmpdir}/root-ca.conf'.format(tmpdir=tmpdir),'r')
        filedata = f.read()
        f.close()

        newdata = filedata.replace('_TOKEN_', token)
        newdata = newdata.replace('TMPDIR', tmpdir)

        f = open('{tmpdir}/root-ca.conf'.format(tmpdir=tmpdir),'w')
        f.write(newdata)
        f.close()

        os.system('echo "00"> {tmpdir}/set'.format(tmpdir=tmpdir))
        os.system('touch {tmpdir}/db  {tmpdir}/db.attr'.format(tmpdir=tmpdir))
        os.system('openssl req -x509 -new -keyout {tmpdir}/rootCA.key -out {tmpdir}/rootCA.crt -config {tmpdir}/root-ca.conf -days 365 -nodes'.format(tmpdir=tmpdir))
        os.system('openssl req -new -keyout {tmpdir}/cert.key -out {tmpdir}/cert.csr -nodes -subj "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Windows"'.format(tmpdir=tmpdir))
        os.system('openssl ca -batch -config {tmpdir}/root-ca.conf -cert {tmpdir}/rootCA.crt -keyfile {tmpdir}/rootCA.key -in {tmpdir}/cert.csr -out {tmpdir}/cert.crt'.format(tmpdir=tmpdir,))
        os.system('osslsigncode sign -certs {tmpdir}/cert.crt -key {tmpdir}/cert.key -in {inputfile} -out {outputfile}'.format(tmpdir=tmpdir,inputfile=inputfile,outputfile=outputfile))
    except Exception as e:
        print e
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def main(argv):
    token = None
    inputfile = None
    outputfile = None
    try:
        opts, args = getopt.getopt(argv,"ht:f:o:",["token=","inputfile=","outputfile="])
    except getopt.GetoptError:
        print 'usage: sign_file.py -t <token> -f <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'usage: sign_file.py -t <token> -f <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in ("-f", "--inputfile"):
            inputfile = arg
        elif opt in ("-o", "--outputfile"):
            outputfile = arg

    if not inputfile or not token or not outputfile:
        print 'usage: sign_file.py -t <token> -f <inputfile> -o <outputfile>'
        sys.exit()

    if not os.path.isfile(inputfile):
        print 'File does not exist'
        sys.exit()

    if not any(x == os.path.splitext(inputfile)[1] for x in ['.dll','.exe']):
        print 'File can only be dll or exe'
        sys.exit()

    authenticode_sign_binary(token, inputfile, outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])
