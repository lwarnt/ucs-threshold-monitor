#!/usr/bin/env python3
"""
Monitors Cisco UCS threshold-crossed events.

Retention Policy:
    Admin > All > Faults, Events and Audit Log > Settings > Global Fault Policy
"""
import smtplib
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from time import sleep

from ucsmsdk.ucshandle import UcsHandle

from env import (
    MAIL_FROM_ADDR,
    MAIL_SMTP_HOST,
    MAIL_TO_ADDR,
    UCS_HOST,
    UCS_PASSWORD,
    UCS_SESSION_OPTS,
    UCS_USERNAME,
)


def send_mail(subject: str, message: str) -> None:
    """Sends SMTP MIMEmultipart message."""
    msg = EmailMessage()
    html_content = (
        f"<h3>{subject}</h3>"
        f"<a href='https://{UCS_HOST}/app/ucsm/index.html'>Check here to go to UCSM!</a>"
        f"<pre>{message}</pre></br>"
    )
    msg.add_alternative(html_content, subtype="html")
    msg["To"] = MAIL_TO_ADDR
    msg["CC"] = MAIL_TO_ADDR
    msg["Subject"] = subject

    with smtplib.SMTP(host=MAIL_SMTP_HOST, port=25, timeout=15) as smtp:
        smtp.sendmail(MAIL_FROM_ADDR, MAIL_TO_ADDR, msg.as_string())

    print(f"mailed: '{msg['Subject']}' to {MAIL_TO_ADDR}")


@dataclass(frozen=True)
class Fault:
    id: int
    raised: bool
    msg: str

    def __hash__(self):
        return hash(self.id)


def monitor_faults():
    """Query UCS for faults."""
    session: UcsHandle = None
    raised_faults: set[int] = set()
    cleared_faults: set[int] = set()

    try:
        while True:
            if session is None:
                session = UcsHandle(
                    UCS_HOST, UCS_USERNAME, UCS_PASSWORD, **UCS_SESSION_OPTS
                )
                session.login()
                print(f"new session for {UCS_HOST}")

            print("check faults")
            faults = session.query_classid(
                class_id="faultInst",
                filter_str="(cause, 'threshold-crossed', type='eq')",
            )

            if len(faults) > 0:
                for mo in faults:
                    # ManagedObject https://ciscoucs.github.io/ucsmsdk_docs/ucsmsdk.html#ucsmsdk.ucsmo.ManagedObject
                    xml = mo.to_xml()

                    raised = True if xml.attrib["severity"] != "cleared" else False
                    fid = xml.attrib["id"]
                    dn = xml.attrib["dn"]

                    f = Fault(fid, raised, str(mo))

                    subject = f"UCS - threshold-crossed - {'Raised' if raised else 'Recovered'}: {f.id} - {dn}"
                    if raised:
                        if f.id not in raised_faults:
                            print(f"raised: {f.id}")
                            send_mail(subject, f.msg)
                            raised_faults.add(f.id)
                    else:
                        if f.id not in cleared_faults:
                            print(f"cleared: {f.id}")
                            send_mail(subject, f.msg)
                            cleared_faults.add(f.id)

            else:
                raised_faults.clear()
                cleared_faults.clear()

            sleep(30)

    except Exception as err:
        print(err)

    finally:
        session.logout()


if __name__ == "__main__":
    sys.exit(monitor_faults())
