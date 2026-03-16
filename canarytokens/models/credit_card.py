from abc import ABCMeta, abstractmethod
import csv
from io import StringIO
from typing import Dict, Optional

from pydantic import BaseModel


class CreditCard(BaseModel):
    id: str
    number: Optional[str]
    cvc: Optional[str]
    expiration: Optional[str]
    kind: Optional[str]
    name: str
    billing_zip: str
    address: str

    def render_html(self) -> str:
        """Returns an HTML div to render the card info on a website"""
        # return """<div id="cccontainer" style="position: relative; margin: auto; background-image: url('/resources/cc-background-{kind}.png'); height: 290px; width: 460px;"><span id="ccname" style="left: 45px; top: 135px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white;">{name}</span><span id="ccnumber" style="left: 45px; top: 160px; font-family: 'Open Sans'; position: absolute; font-size: 20pt; color: white; word-spacing: .45em;">{number}</span><span id="ccexpires" style="left: 45px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{expiration}</span><span id="cccvc" style="left: 240px; top: 230px; position: absolute; font-family: 'Open Sans'; font-size: 18pt; color: white;">{cvc}</span></div>""".format(
        #     kind=self.kind,
        #     cvc=self.cvc,
        #     number=self.number,
        #     name=self.name,
        #     expiration=self.expiration,
        # )
        return f"""<div id="cccontainer"><span id="ccname">{self.name}</span><span id="ccnumber">{self.__format_token()}</span><span id="ccexpires">{self.expiration}</span><span id="cccvc">{self.cvc}</span></div>"""

    def to_csv(self) -> str:
        f = StringIO()
        fn = ["name", "type", "number", "cvc", "exp", "billing_zip"]
        sd = self.to_dict()
        del sd["address"]
        del sd["id"]
        writer = csv.DictWriter(f, fieldnames=fn)
        writer.writeheader()
        writer.writerow(sd)
        return f.getvalue()

    def to_dict(self) -> Dict[str, str]:
        """Returns the CC information as a python dict"""
        out = {
            "id": str(self.id),
            "name": self.name,
            "number": str(self.number),
            "cvc": str(self.cvc),
            "billing_zip": str(self.billing_zip),
            "type": str(self.kind),
            "address": str(self.address),
            "exp": str(self.expiration),
        }
        return out

    def __format_token(self):
        digits = 4
        if self.kind != "AMEX":
            split = [
                self.number[i : i + digits]  # noqa: E203
                for i in range(0, len(self.number), digits)
            ]
            return " ".join(split)
        else:
            split = [self.number[0:4], self.number[4:10], self.number[10:15]]
            return " ".join(split)


class ApiProvider(metaclass=ABCMeta):
    """Abstract base class for a credit card API provider"""

    def __init__(self):
        pass

    @abstractmethod
    def create_credit_card(
        self,
        token_url: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        billing_zip: Optional[str] = None,
    ) -> CreditCard:
        """Abstract method to create a virtual credit card number"""
        pass

    @abstractmethod
    def get_credit_card(self, id: str) -> CreditCard:
        """Abstract method to get a virtual credit card"""
        pass

    @abstractmethod
    def get_latest_transaction(self, cc: CreditCard) -> Optional[Dict[str, str]]:
        """Abstract method to get the latest transaction for a credit card"""
        pass
