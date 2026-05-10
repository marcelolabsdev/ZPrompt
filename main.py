import os
import base64
import json
import urllib.request
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from services.openai_service import generate_prompt
from services.templates import TEMPLATE_DESCRIPTIONS, TEMPLATE_LABELS

_INDEX_B64 = (
    "PCFET0NUWVBFIGh0bWw+CjxodG1sIGxhbmc9ImVzIiBjbGFzcz0iZGFyayI+CjxoZWFkPgogICAg"
    "PG1ldGEgY2hhcnNldD0iVVRGLTgiPgogICAgPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9"
    "IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiPgogICAgPHRpdGxlPlpQcm9t"
    "cHQgLSBHZW5lcmFkb3IgZGUgUHJvbXB0cyBwYXJhIERlc2Fycm9sbG8gZGUgU29mdHdhcmU8L3Rp"
    "dGxlPgogICAgPG1ldGEgbmFtZT0iZGVzY3JpcHRpb24iIGNvbnRlbnQ9IkdlbmVyYSBwcm9tcHRz"
    "IGVzdHJ1Y3R1cmFkb3MgcGFyYSBHTE0gb3B0aW1pemFkb3MgcGFyYSBkZXNhcnJvbGxvIGRlIHNv"
    "ZnR3YXJlLiI+CiAgICA8bGluayByZWw9Imljb24iIHR5cGU9ImltYWdlL3gtaWNvbiIgaHJlZj0i"
    "L2Zhdmljb24uaWNvIj4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iL2Nzcy9zdHls"
    "ZXMuY3NzIj4KICAgIDxsaW5rIHJlbD0ic3R5bGVzaGVldCIgaHJlZj0iaHR0cHM6Ly9jZG4uanNk"
    "ZWxpdnIubmV0L25wbS9nZWlzdEAxL2Rpc3QvZm9udHMvZ2Vpc3Qtc2Fucy9zdHlsZS5jc3MiPgog"
    "ICAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQv"
    "bnBtL21hbnJvcGVAMS9kaXN0L2ZvbnRzL21hbnJvcGUvc3R5bGUuY3NzIj4KICAgIDxzY3JpcHQg"
    "c3JjPSJodHRwczovL3VucGtnLmNvbS9sdWNpZGVAbGF0ZXN0Ij48L3NjcmlwdD4KPC9oZWFkPgo8"
    "Ym9keSBjbGFzcz0ibWluLWgtc2NyZWVuIGJnLWJhY2tncm91bmQgdGV4dC1mb3JlZ3JvdW5kIGZv"
    "bnQtc2FucyBhbnRpYWxpYXNlZCI+CgogICAgPGhlYWRlciBjbGFzcz0ic3RpY2t5IHRvcC0wIHot"
    "NTAgdy1mdWxsIGJvcmRlci1iIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZC84MCBiYWNrZHJv"
    "cC1ibHVyLXNtIj4KICAgICAgICA8ZGl2IGNsYXNzPSJteC1hdXRvIGZsZXggaC0xNCBtYXgtdy00"
    "eGwgaXRlbXMtY2VudGVyIHB4LTQgc206cHgtNiI+CiAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZs"
    "ZXgtMSI+PC9kaXY+CiAgICAgICAgICAgIDxhIGhyZWY9Ii8iIGNsYXNzPSJmbGV4IGl0ZW1zLWNl"
    "bnRlciB0ZXh0LXhsIGZvbnQtc2VtaWJvbGQgdHJhY2tpbmctd2lkZXIiIHN0eWxlPSJmbGV4LWRp"
    "cmVjdGlvbjpjb2x1bW4iPgogICAgICAgICAgICAgICAgPHNwYW4+WlBST01QVDwvc3Bhbj4KICAg"
    "ICAgICAgICAgICAgIDxzcGFuIGNsYXNzPSJibG9jayB0ZXh0LXhzIGZvbnQtbm9ybWFsIHRleHQt"
    "bXV0ZWQtZm9yZWdyb3VuZCB0cmFja2luZy1ub3JtYWwiIHN0eWxlPSJtYXJnaW4tdG9wOjJweCI+"
    "R2VuZXJhIHByb21wdHMgZXN0cnVjdHVyYWRvcyBwYXJhIEdMTTwvc3Bhbj4KICAgICAgICAgICAg"
    "PC9hPgogICAgICAgICAgICA8ZGl2IGNsYXNzPSJmbGV4LTEgZmxleCBpdGVtcy1jZW50ZXIganVz"
    "dGlmeS1lbmQgZ2FwLTMiPgogICAgICAgICAgICAgICAgPGJ1dHRvbiBpZD0idGhlbWUtdG9nZ2xl"
    "IiBjbGFzcz0iaW5saW5lLWZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2VudGVyIHJvdW5kZWQt"
    "bWQgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZCBwLTIgdGV4dC1tdXRlZC1mb3Jl"
    "Z3JvdW5kIHRyYW5zaXRpb24tY29sb3JzIGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0LWFjY2Vu"
    "dC1mb3JlZ3JvdW5kIGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICA8aSBkYXRh"
    "LWx1Y2lkZT0ic3VuIiBpZD0idGhlbWUtaWNvbi1zdW4iIGNsYXNzPSJoLTQgdy00Ij48L2k+CiAg"
    "ICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9Im1vb24iIGlkPSJ0aGVtZS1pY29uLW1v"
    "b24iIGNsYXNzPSJoLTQgdy00IGhpZGRlbiI+PC9pPgogICAgICAgICAgICAgICAgPC9idXR0b24+"
    "CiAgICAgICAgICAgIDwvZGl2PgogICAgICAgIDwvZGl2PgogICAgPC9oZWFkZXI+CgogICAgPG1h"
    "aW4gY2xhc3M9Im14LWF1dG8gbWF4LXctNHhsIHB4LTQgcHktOCBzbTpweC02IHNtOnB5LTEyIj4K"
    "CiAgICAgICAgPHNlY3Rpb24gY2xhc3M9InNwYWNlLXktNiI+CgogICAgICAgICAgICA8ZGl2Pgog"
    "ICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0iZ3JpZCBncmlkLWNvbHMtNCBnYXAtMiI+CiAgICAg"
    "ICAgICAgICAgICAgICAgPGJ1dHRvbiBkYXRhLXR5cGU9InN5c3RlbSIgY2xhc3M9InByb21wdC10"
    "eXBlLWNhcmQgZmxleCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgZ2FwLTIgcm91bmRlZC1s"
    "ZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHB4LTMgcHktMiB0cmFuc2l0aW9uLWFsbCBo"
    "b3Zlcjpib3JkZXItcmluZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0ibW9uaXRvciIgY2xhc3M9ImgtNSB3LTUi"
    "PjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9udC1t"
    "ZWRpdW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPlNZU1RFTTwvc3Bhbj4KICAgICAgICAgICAgICAg"
    "ICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0ic3Rh"
    "cnQiIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2Vu"
    "dGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctY2FyZCBweC0zIHB5"
    "LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92ZXI6c2hhZG93LXNtIGN1cnNv"
    "ci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InJvY2tl"
    "dCIgY2xhc3M9ImgtNCB3LTQiPjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xh"
    "c3M9InRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPlNUQVJUPC9zcGFu"
    "PgogICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDxidXR0"
    "b24gZGF0YS10eXBlPSJmb2xsb3d1cCIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxleCBpdGVt"
    "cy1jZW50ZXIganVzdGlmeS1jZW50ZXIgZ2FwLTIgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWJv"
    "cmRlciBiZy1jYXJkIHB4LTMgcHktMiB0cmFuc2l0aW9uLWFsbCBob3Zlcjpib3JkZXItcmluZyBo"
    "b3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAgICAgICA8"
    "aSBkYXRhLWx1Y2lkZT0icmVwZWF0IiBjbGFzcz0iaC01IHctNSI+PC9pPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LWNhcmQtZm9y"
    "ZWdyb3VuZCI+Rk9MTE9XLVVQPC9zcGFuPgogICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgog"
    "ICAgICAgICAgICAgICAgICAgIDxidXR0b24gZGF0YS10eXBlPSJkZWJ1ZyIgY2xhc3M9InByb21w"
    "dC10eXBlLWNhcmQgZmxleCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgZ2FwLTIgcm91bmRl"
    "ZC1sZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHB4LTMgcHktMiB0cmFuc2l0aW9uLWFs"
    "bCBob3Zlcjpib3JkZXItcmluZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgogICAg"
    "ICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0iYnVnIiBjbGFzcz0iaC00IHctNCI+"
    "PC9pPgogICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14cyBmb250LW1l"
    "ZGl1bSB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+REVCVUc8L3NwYW4+CiAgICAgICAgICAgICAgICAg"
    "ICAgPC9idXR0b24+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+Cgog"
    "ICAgICAgICAgICA8ZGl2PgogICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0idXNlci1pbnB1dCIg"
    "Y2xhc3M9Im1iLTIgYmxvY2sgdGV4dC1zbSB0ZXh0LW11dGVkLWZvcmVncm91bmQgdGV4dC1jZW50"
    "ZXIiPkRlc2NyaWJlIHR1IHByb3llY3RvIHkgb2J0aWVuZSBwcm9tcHRzIG9wdGltaXphZG9zIHBh"
    "cmEgZGVzYXJyb2xsbyBkZSBzb2Z0d2FyZS48L2xhYmVsPgogICAgICAgICAgICAgICAgPHRleHRh"
    "cmVhCiAgICAgICAgICAgICAgICAgICAgaWQ9InVzZXItaW5wdXQiCiAgICAgICAgICAgICAgICAg"
    "ICAgcm93cz0iNCIKICAgICAgICAgICAgICAgICAgICBjbGFzcz0iZmxleCB3LWZ1bGwgcm91bmRl"
    "ZC1sZyBib3JkZXIgYm9yZGVyLWlucHV0IGJnLWJhY2tncm91bmQgcHgtMyBweS0yLjUgdGV4dC1z"
    "bSBzaGFkb3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgcGxhY2Vob2xkZXI6dGV4dC1tdXRlZC1mb3Jl"
    "Z3JvdW5kIGZvY3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3VzLXZpc2libGU6cmluZy0yIGZv"
    "Y3VzLXZpc2libGU6cmluZy1yaW5nIHJlc2l6ZS1ub25lIgogICAgICAgICAgICAgICAgICAgIHBs"
    "YWNlaG9sZGVyPSJFamVtcGxvOiBDcmVhciB1bmEgQVBJIFJFU1QgY29uIFB5dGhvbiB5IEZhc3RB"
    "UEkgcGFyYSBnZXN0aW9uIGRlIHRhcmVhcywgY29uIGF1dGVudGljYWNpb24gSldUIHkgYmFzZSBk"
    "ZSBkYXRvcyBQb3N0Z3JlU1FMLi4uIgogICAgICAgICAgICAgICAgPjwvdGV4dGFyZWE+CiAgICAg"
    "ICAgICAgIDwvZGl2PgoKICAgICAgICAgICAgPGRpdiBjbGFzcz0iZ3JpZCBncmlkLWNvbHMtMSBn"
    "YXAtNCBzbTpncmlkLWNvbHMtMyI+CiAgICAgICAgICAgICAgICA8ZGl2PgogICAgICAgICAgICAg"
    "ICAgICAgIDxsYWJlbCBmb3I9Imxhbmd1YWdlLXNlbGVjdCIgY2xhc3M9Im1iLTIgYmxvY2sgdGV4"
    "dC1zbSBmb250LW1lZGl1bSB0ZXh0LW11dGVkLWZvcmVncm91bmQiPkxlbmd1YWplIChvcGNpb25h"
    "bCk8L2xhYmVsPgogICAgICAgICAgICAgICAgICAgIDxzZWxlY3QgaWQ9Imxhbmd1YWdlLXNlbGVj"
    "dCIgY2xhc3M9ImZsZXggaC05IHctZnVsbCByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQg"
    "YmctYmFja2dyb3VuZCBweC0zIHRleHQtc20gc2hhZG93LXhzIHRyYW5zaXRpb24tY29sb3JzIGZv"
    "Y3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3VzLXZpc2libGU6cmluZy0yIGZvY3VzLXZpc2li"
    "bGU6cmluZy1yaW5nIj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iIj5B"
    "dXRvLWRldGVjdGFyPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFs"
    "dWU9IlB5dGhvbiI+UHl0aG9uPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRp"
    "b24gdmFsdWU9IlR5cGVTY3JpcHQiPlR5cGVTY3JpcHQ8L29wdGlvbj4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iRGFydCI+RGFydDwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJKYXZhU2NyaXB0Ij5KYXZhU2NyaXB0PC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJ1c3QiPlJ1c3Q8L29wdGlv"
    "bj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iR28iPkdvPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkphdmEiPkphdmE8L29wdGlv"
    "bj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iQyMiPkMjPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlBIUCI+UEhQPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJ1YnkiPlJ1Ynk8L29wdGlv"
    "bj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iU3dpZnQiPlN3aWZ0PC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IktvdGxpbiI+S290"
    "bGluPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgPC9zZWxlY3Q+CiAgICAgICAgICAgICAg"
    "ICA8L2Rpdj4KICAgICAgICAgICAgICAgIDxkaXY+CiAgICAgICAgICAgICAgICAgICAgPGxhYmVs"
    "IGZvcj0iZnJhbWV3b3JrLXNlbGVjdCIgY2xhc3M9Im1iLTIgYmxvY2sgdGV4dC1zbSBmb250LW1l"
    "ZGl1bSB0ZXh0LW11dGVkLWZvcmVncm91bmQiPkZyYW1ld29yayAob3BjaW9uYWwpPC9sYWJlbD4K"
    "ICAgICAgICAgICAgICAgICAgICA8c2VsZWN0IGlkPSJmcmFtZXdvcmstc2VsZWN0IiBjbGFzcz0i"
    "ZmxleCBoLTkgdy1mdWxsIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1pbnB1dCBiZy1iYWNrZ3Jv"
    "dW5kIHB4LTMgdGV4dC1zbSBzaGFkb3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgZm9jdXMtdmlzaWJs"
    "ZTpvdXRsaW5lLW5vbmUgZm9jdXMtdmlzaWJsZTpyaW5nLTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJp"
    "bmciPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIiPk5pbmd1bm8gLyBB"
    "dXRvPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZhc3RB"
    "UEkiPkZhc3RBUEk8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1"
    "ZT0iRGphbmdvIj5EamFuZ288L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iRmx1dHRlciI+Rmx1dHRlcjwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAg"
    "ICA8b3B0aW9uIHZhbHVlPSJGbGFzayI+Rmxhc2s8L29wdGlvbj4KICAgICAgICAgICAgICAgICAg"
    "ICAgICAgPG9wdGlvbiB2YWx1ZT0iTmV4dC5qcyI+TmV4dC5qczwvb3B0aW9uPgogICAgICAgICAg"
    "ICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJSZWFjdCI+UmVhY3Q8L29wdGlvbj4KICAgICAg"
    "ICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iVnVlLmpzIj5WdWUuanM8L29wdGlvbj4K"
    "ICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iRXhwcmVzcyI+RXhwcmVzczwv"
    "b3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJOZXN0SlMiPk5l"
    "c3RKUzwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJTcHJp"
    "bmcgQm9vdCI+U3ByaW5nIEJvb3Q8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9w"
    "dGlvbiB2YWx1ZT0iQWN0aXgiPkFjdGl4PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAg"
    "IDxvcHRpb24gdmFsdWU9IkF4dW0iPkF4dW08L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPG9wdGlvbiB2YWx1ZT0iTGFyYXZlbCI+TGFyYXZlbDwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJSYWlscyI+UmFpbHM8L29wdGlvbj4KICAgICAgICAg"
    "ICAgICAgICAgICA8L3NlbGVjdD4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAg"
    "ICAgPGRpdj4KICAgICAgICAgICAgICAgICAgICA8bGFiZWwgZm9yPSJkYXRhYmFzZS1zZWxlY3Qi"
    "IGNsYXNzPSJtYi0yIGJsb2NrIHRleHQtc20gZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3Jv"
    "dW5kIj5CYXNlIGRlIGRhdG9zIChvcGNpb25hbCk8L2xhYmVsPgogICAgICAgICAgICAgICAgICAg"
    "IDxzZWxlY3QgaWQ9ImRhdGFiYXNlLXNlbGVjdCIgY2xhc3M9ImZsZXggaC05IHctZnVsbCByb3Vu"
    "ZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFja2dyb3VuZCBweC0zIHRleHQtc20gc2hh"
    "ZG93LXhzIHRyYW5zaXRpb24tY29sb3JzIGZvY3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3Vz"
    "LXZpc2libGU6cmluZy0yIGZvY3VzLXZpc2libGU6cmluZy1yaW5nIj4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iIj5OaW5ndW5hIC8gQXV0bzwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJTdXBhYmFzZSI+U3VwYWJhc2UgKHdlYi9B"
    "UEkpPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZpcmVi"
    "YXNlIj5GaXJlYmFzZSAoYXBwcyBtb3ZpbGVzKTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJQb3N0Z3JlU1FMIj5Qb3N0Z3JlU1FMPC9vcHRpb24+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9Ik15U1FMIj5NeVNRTDwvb3B0aW9uPgog"
    "ICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJNb25nb0RCIj5Nb25nb0RCPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlNRTGl0ZSI+U1FM"
    "aXRlPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJlZGlz"
    "Ij5SZWRpczwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJN"
    "YXJpYURCIj5NYXJpYURCPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24g"
    "dmFsdWU9IlBsYW5ldFNjYWxlIj5QbGFuZXRTY2FsZTwvb3B0aW9uPgogICAgICAgICAgICAgICAg"
    "ICAgICAgICA8b3B0aW9uIHZhbHVlPSJDb2Nrcm9hY2hEQiI+Q29ja3JvYWNoREI8L29wdGlvbj4K"
    "ICAgICAgICAgICAgICAgICAgICA8L3NlbGVjdD4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAg"
    "ICAgICAgICA8L2Rpdj4KCiAgICAgICAgICAgIDxidXR0b24KICAgICAgICAgICAgICAgIGlkPSJn"
    "ZW5lcmF0ZS1idG4iCiAgICAgICAgICAgICAgICBjbGFzcz0iaW5saW5lLWZsZXggdy1mdWxsIGl0"
    "ZW1zLWNlbnRlciBqdXN0aWZ5LWNlbnRlciBnYXAtMiByb3VuZGVkLWxnIGJnLXByaW1hcnkgcHgt"
    "NCBweS0yLjUgdGV4dC1zbSBmb250LW1lZGl1bSB0ZXh0LXByaW1hcnktZm9yZWdyb3VuZCBzaGFk"
    "b3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgaG92ZXI6YmctcHJpbWFyeS85MCBkaXNhYmxlZDpwb2lu"
    "dGVyLWV2ZW50cy1ub25lIGRpc2FibGVkOm9wYWNpdHktNTAgY3Vyc29yLXBvaW50ZXIiCiAgICAg"
    "ICAgICAgICAgICBkaXNhYmxlZAogICAgICAgICAgICA+CiAgICAgICAgICAgICAgICA8aSBkYXRh"
    "LWx1Y2lkZT0iemFwIiBjbGFzcz0iaC00IHctNCI+PC9pPgogICAgICAgICAgICAgICAgPHNwYW4g"
    "aWQ9ImJ0bi10ZXh0Ij5HZW5lcmFyIFByb21wdDwvc3Bhbj4KICAgICAgICAgICAgICAgIDxzcGFu"
    "IGlkPSJidG4tc3Bpbm5lciIgY2xhc3M9ImhpZGRlbiI+CiAgICAgICAgICAgICAgICAgICAgPHN2"
    "ZyBjbGFzcz0iaC00IHctNCBhbmltYXRlLXNwaW4iIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0i"
    "bm9uZSI+PGNpcmNsZSBjbGFzcz0ib3BhY2l0eS0yNSIgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIiBz"
    "dHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSI0Ij48L2NpcmNsZT48cGF0aCBjbGFz"
    "cz0ib3BhY2l0eS03NSIgZmlsbD0iY3VycmVudENvbG9yIiBkPSJNNCAxMmE4IDggMCAwMTgtOFYw"
    "QzUuMzczIDAgMCA1LjM3MyAwIDEyaDR6Ij48L3BhdGg+PC9zdmc+CiAgICAgICAgICAgICAgICA8"
    "L3NwYW4+CiAgICAgICAgICAgIDwvYnV0dG9uPgoKICAgICAgICA8L3NlY3Rpb24+CgogICAgICAg"
    "IDxzZWN0aW9uIGlkPSJlcnJvci1zZWN0aW9uIiBjbGFzcz0ibXQtNiBoaWRkZW4iPgogICAgICAg"
    "ICAgICA8ZGl2IGNsYXNzPSJyb3VuZGVkLWxnIGJvcmRlciBib3JkZXItZGVzdHJ1Y3RpdmUvNTAg"
    "YmctZGVzdHJ1Y3RpdmUvMTAgcC00IHRleHQtc20gdGV4dC1kZXN0cnVjdGl2ZSI+CiAgICAgICAg"
    "ICAgICAgICA8cCBpZD0iZXJyb3ItbWVzc2FnZSI+PC9wPgogICAgICAgICAgICA8L2Rpdj4KICAg"
    "ICAgICA8L3NlY3Rpb24+CgogICAgICAgIDxzZWN0aW9uIGlkPSJyZXN1bHQtc2VjdGlvbiIgY2xh"
    "c3M9Im10LTggaGlkZGVuIj4KICAgICAgICAgICAgPGRpdiBjbGFzcz0icm91bmRlZC1sZyBib3Jk"
    "ZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHNoYWRvdy1zbSI+CiAgICAgICAgICAgICAgICA8ZGl2"
    "IGNsYXNzPSJmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWJldHdlZW4gYm9yZGVyLWIgYm9yZGVy"
    "LWJvcmRlciBweC00IHB5LTMiPgogICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZsZXgg"
    "aXRlbXMtY2VudGVyIGdhcC0yIj4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gaWQ9InJl"
    "c3VsdC1pY29uIj48L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgICAgIDxoMiBpZD0icmVzdWx0"
    "LXRpdGxlIiBjbGFzcz0idGV4dC1zbSBmb250LXNlbWlib2xkIHRleHQtY2FyZC1mb3JlZ3JvdW5k"
    "Ij48L2gyPgogICAgICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgICAgIDxk"
    "aXYgY2xhc3M9ImZsZXggaXRlbXMtY2VudGVyIGdhcC0yIj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPGJ1dHRvbiBpZD0iY29weS1idG4iIGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIg"
    "Z2FwLTEuNSByb3VuZGVkLW1kIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWJhY2tncm91bmQgcHgt"
    "Mi41IHB5LTEuNSB0ZXh0LXhzIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCB0cmFu"
    "c2l0aW9uLWNvbG9ycyBob3ZlcjpiZy1hY2NlbnQgaG92ZXI6dGV4dC1hY2NlbnQtZm9yZWdyb3Vu"
    "ZCBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1"
    "Y2lkZT0iY29weSIgY2xhc3M9ImgtMy41IHctMy41Ij48L2k+CiAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICBDb3BpYXIKICAgICAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAgICAg"
    "ICAgICAgICAgICAgICAgIDxidXR0b24gaWQ9InJlZ2VuZXJhdGUtYnRuIiBjbGFzcz0iaW5saW5l"
    "LWZsZXggaXRlbXMtY2VudGVyIGdhcC0xLjUgcm91bmRlZC1tZCBib3JkZXIgYm9yZGVyLWJvcmRl"
    "ciBiZy1iYWNrZ3JvdW5kIHB4LTIuNSBweS0xLjUgdGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LW11"
    "dGVkLWZvcmVncm91bmQgdHJhbnNpdGlvbi1jb2xvcnMgaG92ZXI6YmctYWNjZW50IGhvdmVyOnRl"
    "eHQtYWNjZW50LWZvcmVncm91bmQgY3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InJlZnJlc2gtY3ciIGNsYXNzPSJoLTMuNSB3LTMuNSI+"
    "PC9pPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgUmVnZW5lcmFyCiAgICAgICAgICAgICAg"
    "ICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAg"
    "ICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJwLTQiPgogICAgICAgICAg"
    "ICAgICAgICAgIDxwcmUgaWQ9InJlc3VsdC1jb250ZW50IiBjbGFzcz0id2hpdGVzcGFjZS1wcmUt"
    "d3JhcCBicmVhay13b3JkcyBmb250LW1vbm8gdGV4dC1zbSBsZWFkaW5nLXJlbGF4ZWQgdGV4dC1j"
    "YXJkLWZvcmVncm91bmQiPjwvcHJlPgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAg"
    "ICAgICA8ZGl2IGNsYXNzPSJib3JkZXItdCBib3JkZXItYm9yZGVyIHB4LTQgcHktMiI+CiAgICAg"
    "ICAgICAgICAgICAgICAgPHAgaWQ9InJlc3VsdC10aW1lc3RhbXAiIGNsYXNzPSJ0ZXh0LXhzIHRl"
    "eHQtbXV0ZWQtZm9yZWdyb3VuZCI+PC9wPgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAg"
    "ICAgIDwvZGl2PgogICAgICAgIDwvc2VjdGlvbj4KCiAgICA8L21haW4+CgogICAgPGZvb3RlciBj"
    "bGFzcz0iYm9yZGVyLXQgYm9yZGVyLWJvcmRlciBweS02IHRleHQtY2VudGVyIHRleHQteHMgdGV4"
    "dC1tdXRlZC1mb3JlZ3JvdW5kIj4KICAgICAgICA8ZGl2IGlkPSJwZWFrLWluZm8iPjwvZGl2Pgog"
    "ICAgPC9mb290ZXI+CgogICAgPHNjcmlwdCBzcmM9Ii9qcy9hcHAuanMiPjwvc2NyaXB0Pgo8L2Jv"
    "ZHk+CjwvaHRtbD4K"
)




INDEX_HTML = base64.b64decode(_INDEX_B64).decode("utf-8")

load_dotenv()

app = FastAPI(
    title="ZPrompt",
    description="Generador de prompts estructurados para desarrollo de software",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    prompt_type: str = Field(..., pattern="^(system|start|followup|debug)$")
    language: str | None = None
    framework: str | None = None
    database: str | None = None


class PromptResponse(BaseModel):
    prompt: str
    prompt_type: str
    label: str
    timestamp: str


@app.get("/")
def serve_index():
    return HTMLResponse(content=INDEX_HTML)


@app.get("/api/timezone")
def get_timezone(request: Request):
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not client_ip or client_ip == "127.0.0.1" or client_ip == "::1":
        client_ip = request.client.host if request.client else ""
    try:
        url = f"https://ipapi.co/{client_ip}/json/" if client_ip else "https://ipapi.co/json/"
        req = urllib.request.Request(url, headers={"User-Agent": "ZPrompt/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        tz_name = data.get("timezone", "UTC")
        utc_offset_str = data.get("utc_offset", "+0000")
        sign = 1 if utc_offset_str.startswith("+") else -1
        h = int(utc_offset_str[1:3])
        m = int(utc_offset_str[3:5])
        offset_minutes = sign * (h * 60 + m)
        return {"timezone": tz_name, "offset": offset_minutes}
    except Exception:
        return {"timezone": "UTC", "offset": 0}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/templates")
def get_templates():
    result = []
    for key, label in TEMPLATE_LABELS.items():
        result.append(
            {
                "id": key,
                "label": label,
                "description": TEMPLATE_DESCRIPTIONS.get(key, ""),
            }
        )
    return {"templates": result}


@app.post("/api/generate", response_model=PromptResponse)
async def create_prompt(request: PromptRequest):
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY no configurada. Agregala como variable de entorno.",
        )

    try:
        prompt_text = await generate_prompt(
            text=request.text,
            prompt_type=request.prompt_type,
            language=request.language,
            framework=request.framework,
            database=request.database,
        )
        return PromptResponse(
            prompt=prompt_text,
            prompt_type=request.prompt_type,
            label=TEMPLATE_LABELS.get(request.prompt_type, ""),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generando prompt: {str(e)}"
        )


@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300},
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z",
    }
