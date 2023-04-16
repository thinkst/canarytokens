import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path


def authenticode_sign_binary(
    nxdomain_token_url: str, inputfile: Path, outputfile: Path
):  # pragma: no cover
    try:
        tmpdir = tempfile.mkdtemp()

        cmd = "cp root-ca.conf {tmpdir}/root-ca.conf".format(tmpdir=tmpdir)
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        with open("{tmpdir}/root-ca.conf".format(tmpdir=tmpdir), "r") as fp:
            filedata = fp.read()
            newdata = filedata.replace("_TOKEN_", nxdomain_token_url)
            newdata = newdata.replace("TMPDIR", tmpdir)

        with open("{tmpdir}/root-ca.conf".format(tmpdir=tmpdir), "w") as fp:
            fp.write(newdata)

        cmd = 'echo "00" > {tmpdir}/ser'.format(tmpdir=tmpdir)
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        cmd = "touch {tmpdir}/db  {tmpdir}/db.attr".format(tmpdir=tmpdir)
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        cmd = "openssl req -x509 -new -keyout {tmpdir}/rootCA.key -out {tmpdir}/rootCA.crt -config {tmpdir}/root-ca.conf -days 365 -nodes".format(
            tmpdir=tmpdir
        )
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        cmd = 'openssl req -new -keyout {tmpdir}/cert.key -out {tmpdir}/cert.csr -nodes -subj "/C=US/ST=Washington/L=Redmond/O=Microsoft Corporation/CN=Microsoft Windows"'.format(
            tmpdir=tmpdir
        )
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        cmd = "openssl ca -batch -config {tmpdir}/root-ca.conf -cert {tmpdir}/rootCA.crt -keyfile {tmpdir}/rootCA.key -in {tmpdir}/cert.csr -out {tmpdir}/cert.crt".format(
            tmpdir=tmpdir,
        )
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()

        cmd = "osslsigncode sign -certs {tmpdir}/cert.crt -key {tmpdir}/cert.key -in {inputfile} -out {outputfile}".format(
            tmpdir=tmpdir, inputfile=inputfile, outputfile=outputfile
        )
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.communicate()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
