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
    "ICAgICAgICAgICAgICAgPHAgY2xhc3M9InRleHQtc20gZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1m"
    "b3JlZ3JvdW5kIG1iLTIgdGV4dC1jZW50ZXIiPlNlbGVjY2lvbmEgdGlwbyBkZSBwcm9tcHQ8L3A+"
    "CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJncmlkIGdyaWQtY29scy00IGdhcC0yIj4KICAg"
    "ICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0ic3lzdGVtIiBjbGFzcz0icHJvbXB0"
    "LXR5cGUtY2FyZCBmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWNlbnRlciBnYXAtMiByb3VuZGVk"
    "LWxnIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgcHgtMyBweS0yIHRyYW5zaXRpb24tYWxs"
    "IGhvdmVyOmJvcmRlci1yaW5nIGhvdmVyOnNoYWRvdy1zbSBjdXJzb3ItcG9pbnRlciI+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJtb25pdG9yIiBjbGFzcz0iaC01IHct"
    "NSI+PC9pPgogICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14cyBmb250"
    "LWJvbGQgdGV4dC1jYXJkLWZvcmVncm91bmQiPlNZU1RFTTwvc3Bhbj4KICAgICAgICAgICAgICAg"
    "ICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0ic3Rh"
    "cnQiIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2Vu"
    "dGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctY2FyZCBweC0zIHB5"
    "LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92ZXI6c2hhZG93LXNtIGN1cnNv"
    "ci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InJvY2tl"
    "dCIgY2xhc3M9ImgtNCB3LTQiPjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xh"
    "c3M9InRleHQteHMgZm9udC1ib2xkIHRleHQtY2FyZC1mb3JlZ3JvdW5kIj5TVEFSVDwvc3Bhbj4K"
    "ICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8YnV0dG9u"
    "IGRhdGEtdHlwZT0iZm9sbG93dXAiIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRlbXMt"
    "Y2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1ib3Jk"
    "ZXIgYmctY2FyZCBweC0zIHB5LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92"
    "ZXI6c2hhZG93LXNtIGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGkg"
    "ZGF0YS1sdWNpZGU9InJlcGVhdCIgY2xhc3M9ImgtNSB3LTUiPjwvaT4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9udC1ib2xkIHRleHQtY2FyZC1mb3JlZ3Jv"
    "dW5kIj5GT0xMT1ctVVA8L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAg"
    "ICAgICAgICAgICAgICAgPGJ1dHRvbiBkYXRhLXR5cGU9ImRlYnVnIiBjbGFzcz0icHJvbXB0LXR5"
    "cGUtY2FyZCBmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWNlbnRlciBnYXAtMiByb3VuZGVkLWxn"
    "IGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgcHgtMyBweS0yIHRyYW5zaXRpb24tYWxsIGhv"
    "dmVyOmJvcmRlci1yaW5nIGhvdmVyOnNoYWRvdy1zbSBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAg"
    "ICAgICAgICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJidWciIGNsYXNzPSJoLTQgdy00Ij48L2k+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzPSJ0ZXh0LXhzIGZvbnQtYm9sZCB0"
    "ZXh0LWNhcmQtZm9yZWdyb3VuZCI+REVCVUc8L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgPC9i"
    "dXR0b24+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+CgogICAgICAg"
    "ICAgICA8ZGl2PgogICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0idXNlci1pbnB1dCIgY2xhc3M9"
    "Im1iLTIgYmxvY2sgdGV4dC1zbSB0ZXh0LW11dGVkLWZvcmVncm91bmQgdGV4dC1jZW50ZXIiPkRl"
    "c2NyaWJlIHR1IHByb3llY3RvIHkgb2J0aWVuZSBwcm9tcHRzIG9wdGltaXphZG9zIHBhcmEgZGVz"
    "YXJyb2xsbyBkZSBzb2Z0d2FyZS48L2xhYmVsPgogICAgICAgICAgICAgICAgPHRleHRhcmVhCiAg"
    "ICAgICAgICAgICAgICAgICAgaWQ9InVzZXItaW5wdXQiCiAgICAgICAgICAgICAgICAgICAgcm93"
    "cz0iNCIKICAgICAgICAgICAgICAgICAgICBjbGFzcz0iZmxleCB3LWZ1bGwgcm91bmRlZC1sZyBi"
    "b3JkZXIgYm9yZGVyLWlucHV0IGJnLWJhY2tncm91bmQgcHgtMyBweS0yLjUgdGV4dC1zbSBzaGFk"
    "b3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgcGxhY2Vob2xkZXI6dGV4dC1tdXRlZC1mb3JlZ3JvdW5k"
    "IGZvY3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3VzLXZpc2libGU6cmluZy0yIGZvY3VzLXZp"
    "c2libGU6cmluZy1yaW5nIHJlc2l6ZS1ub25lIgogICAgICAgICAgICAgICAgICAgIHBsYWNlaG9s"
    "ZGVyPSJFamVtcGxvOiBDcmVhciB1bmEgQVBJIFJFU1QgY29uIFB5dGhvbiB5IEZhc3RBUEkgcGFy"
    "YSBnZXN0aW9uIGRlIHRhcmVhcywgY29uIGF1dGVudGljYWNpb24gSldUIHkgYmFzZSBkZSBkYXRv"
    "cyBQb3N0Z3JlU1FMLi4uIgogICAgICAgICAgICAgICAgPjwvdGV4dGFyZWE+CiAgICAgICAgICAg"
    "IDwvZGl2PgoKICAgICAgICAgICAgPGRpdiBjbGFzcz0iZ3JpZCBncmlkLWNvbHMtMSBnYXAtNCBz"
    "bTpncmlkLWNvbHMtMyI+CiAgICAgICAgICAgICAgICA8ZGl2PgogICAgICAgICAgICAgICAgICAg"
    "IDxsYWJlbCBmb3I9Imxhbmd1YWdlLXNlbGVjdCIgY2xhc3M9Im1iLTIgYmxvY2sgdGV4dC1zbSBm"
    "b250LW1lZGl1bSB0ZXh0LW11dGVkLWZvcmVncm91bmQiPkxlbmd1YWplIChvcGNpb25hbCk8L2xh"
    "YmVsPgogICAgICAgICAgICAgICAgICAgIDxzZWxlY3QgaWQ9Imxhbmd1YWdlLXNlbGVjdCIgY2xh"
    "c3M9ImZsZXggaC05IHctZnVsbCByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFj"
    "a2dyb3VuZCBweC0zIHRleHQtc20gc2hhZG93LXhzIHRyYW5zaXRpb24tY29sb3JzIGZvY3VzLXZp"
    "c2libGU6b3V0bGluZS1ub25lIGZvY3VzLXZpc2libGU6cmluZy0yIGZvY3VzLXZpc2libGU6cmlu"
    "Zy1yaW5nIj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iIj5BdXRvLWRl"
    "dGVjdGFyPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlB5"
    "dGhvbiI+UHl0aG9uPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFs"
    "dWU9IlR5cGVTY3JpcHQiPlR5cGVTY3JpcHQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPG9wdGlvbiB2YWx1ZT0iRGFydCI+RGFydDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJKYXZhU2NyaXB0Ij5KYXZhU2NyaXB0PC9vcHRpb24+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJ1c3QiPlJ1c3Q8L29wdGlvbj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iR28iPkdvPC9vcHRpb24+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkphdmEiPkphdmE8L29wdGlvbj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iQyMiPkMjPC9vcHRpb24+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlBIUCI+UEhQPC9vcHRpb24+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJ1YnkiPlJ1Ynk8L29wdGlvbj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iU3dpZnQiPlN3aWZ0PC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IktvdGxpbiI+S290bGluPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgPC9zZWxlY3Q+CiAgICAgICAgICAgICAgICA8L2Rp"
    "dj4KICAgICAgICAgICAgICAgIDxkaXY+CiAgICAgICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0i"
    "ZnJhbWV3b3JrLXNlbGVjdCIgY2xhc3M9Im1iLTIgYmxvY2sgdGV4dC1zbSBmb250LW1lZGl1bSB0"
    "ZXh0LW11dGVkLWZvcmVncm91bmQiPkZyYW1ld29yayAob3BjaW9uYWwpPC9sYWJlbD4KICAgICAg"
    "ICAgICAgICAgICAgICA8c2VsZWN0IGlkPSJmcmFtZXdvcmstc2VsZWN0IiBjbGFzcz0iZmxleCBo"
    "LTkgdy1mdWxsIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1pbnB1dCBiZy1iYWNrZ3JvdW5kIHB4"
    "LTMgdGV4dC1zbSBzaGFkb3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgZm9jdXMtdmlzaWJsZTpvdXRs"
    "aW5lLW5vbmUgZm9jdXMtdmlzaWJsZTpyaW5nLTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJpbmciPgog"
    "ICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSIiPk5pbmd1bm8gLyBBdXRvPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZhc3RBUEkiPkZh"
    "c3RBUEk8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iRGph"
    "bmdvIj5EamFuZ288L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1"
    "ZT0iRmx1dHRlciI+Rmx1dHRlcjwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0"
    "aW9uIHZhbHVlPSJGbGFzayI+Rmxhc2s8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAg"
    "PG9wdGlvbiB2YWx1ZT0iTmV4dC5qcyI+TmV4dC5qczwvb3B0aW9uPgogICAgICAgICAgICAgICAg"
    "ICAgICAgICA8b3B0aW9uIHZhbHVlPSJSZWFjdCI+UmVhY3Q8L29wdGlvbj4KICAgICAgICAgICAg"
    "ICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iVnVlLmpzIj5WdWUuanM8L29wdGlvbj4KICAgICAg"
    "ICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iRXhwcmVzcyI+RXhwcmVzczwvb3B0aW9u"
    "PgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJOZXN0SlMiPk5lc3RKUzwv"
    "b3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJTcHJpbmcgQm9v"
    "dCI+U3ByaW5nIEJvb3Q8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2"
    "YWx1ZT0iQWN0aXgiPkFjdGl4PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRp"
    "b24gdmFsdWU9IkF4dW0iPkF4dW08L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9w"
    "dGlvbiB2YWx1ZT0iTGFyYXZlbCI+TGFyYXZlbDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJSYWlscyI+UmFpbHM8L29wdGlvbj4KICAgICAgICAgICAgICAg"
    "ICAgICA8L3NlbGVjdD4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgPGRp"
    "dj4KICAgICAgICAgICAgICAgICAgICA8bGFiZWwgZm9yPSJkYXRhYmFzZS1zZWxlY3QiIGNsYXNz"
    "PSJtYi0yIGJsb2NrIHRleHQtc20gZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIj5C"
    "YXNlIGRlIGRhdG9zIChvcGNpb25hbCk8L2xhYmVsPgogICAgICAgICAgICAgICAgICAgIDxzZWxl"
    "Y3QgaWQ9ImRhdGFiYXNlLXNlbGVjdCIgY2xhc3M9ImZsZXggaC05IHctZnVsbCByb3VuZGVkLWxn"
    "IGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFja2dyb3VuZCBweC0zIHRleHQtc20gc2hhZG93LXhz"
    "IHRyYW5zaXRpb24tY29sb3JzIGZvY3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3VzLXZpc2li"
    "bGU6cmluZy0yIGZvY3VzLXZpc2libGU6cmluZy1yaW5nIj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPG9wdGlvbiB2YWx1ZT0iIj5OaW5ndW5hIC8gQXV0bzwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJTdXBhYmFzZSI+U3VwYWJhc2UgKHdlYi9BUEkpPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZpcmViYXNlIj5G"
    "aXJlYmFzZSAoYXBwcyBtb3ZpbGVzKTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8"
    "b3B0aW9uIHZhbHVlPSJQb3N0Z3JlU1FMIj5Qb3N0Z3JlU1FMPC9vcHRpb24+CiAgICAgICAgICAg"
    "ICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9Ik15U1FMIj5NeVNRTDwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJNb25nb0RCIj5Nb25nb0RCPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlNRTGl0ZSI+U1FMaXRlPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJlZGlzIj5SZWRp"
    "czwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJNYXJpYURC"
    "Ij5NYXJpYURCPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9"
    "IlBsYW5ldFNjYWxlIj5QbGFuZXRTY2FsZTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAg"
    "ICA8b3B0aW9uIHZhbHVlPSJDb2Nrcm9hY2hEQiI+Q29ja3JvYWNoREI8L29wdGlvbj4KICAgICAg"
    "ICAgICAgICAgICAgICA8L3NlbGVjdD4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAg"
    "ICA8L2Rpdj4KCiAgICAgICAgICAgIDxidXR0b24KICAgICAgICAgICAgICAgIGlkPSJnZW5lcmF0"
    "ZS1idG4iCiAgICAgICAgICAgICAgICBjbGFzcz0iaW5saW5lLWZsZXggdy1mdWxsIGl0ZW1zLWNl"
    "bnRlciBqdXN0aWZ5LWNlbnRlciBnYXAtMiByb3VuZGVkLWxnIGJnLXByaW1hcnkgcHgtNCBweS0y"
    "LjUgdGV4dC1zbSBmb250LW1lZGl1bSB0ZXh0LXByaW1hcnktZm9yZWdyb3VuZCBzaGFkb3cteHMg"
    "dHJhbnNpdGlvbi1jb2xvcnMgaG92ZXI6YmctcHJpbWFyeS85MCBkaXNhYmxlZDpwb2ludGVyLWV2"
    "ZW50cy1ub25lIGRpc2FibGVkOm9wYWNpdHktNTAgY3Vyc29yLXBvaW50ZXIiCiAgICAgICAgICAg"
    "ICAgICBkaXNhYmxlZAogICAgICAgICAgICA+CiAgICAgICAgICAgICAgICA8c3BhbiBpZD0iYnRu"
    "LXRleHQiPkdFTkVSQVIgUFJPTVBUPC9zcGFuPgogICAgICAgICAgICAgICAgPHNwYW4gaWQ9ImJ0"
    "bi1zcGlubmVyIiBjbGFzcz0iaGlkZGVuIj4KICAgICAgICAgICAgICAgICAgICA8c3ZnIGNsYXNz"
    "PSJoLTQgdy00IGFuaW1hdGUtc3BpbiIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIj48"
    "Y2lyY2xlIGNsYXNzPSJvcGFjaXR5LTI1IiBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiIHN0cm9rZT0i"
    "Y3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjQiPjwvY2lyY2xlPjxwYXRoIGNsYXNzPSJvcGFj"
    "aXR5LTc1IiBmaWxsPSJjdXJyZW50Q29sb3IiIGQ9Ik00IDEyYTggOCAwIDAxOC04VjBDNS4zNzMg"
    "MCAwIDUuMzczIDAgMTJoNHoiPjwvcGF0aD48L3N2Zz4KICAgICAgICAgICAgICAgIDwvc3Bhbj4K"
    "ICAgICAgICAgICAgPC9idXR0b24+CgogICAgICAgIDwvc2VjdGlvbj4KCiAgICAgICAgPHNlY3Rp"
    "b24gaWQ9ImVycm9yLXNlY3Rpb24iIGNsYXNzPSJtdC02IGhpZGRlbiI+CiAgICAgICAgICAgIDxk"
    "aXYgY2xhc3M9InJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1kZXN0cnVjdGl2ZS81MCBiZy1kZXN0"
    "cnVjdGl2ZS8xMCBwLTQgdGV4dC1zbSB0ZXh0LWRlc3RydWN0aXZlIj4KICAgICAgICAgICAgICAg"
    "IDxwIGlkPSJlcnJvci1tZXNzYWdlIj48L3A+CiAgICAgICAgICAgIDwvZGl2PgogICAgICAgIDwv"
    "c2VjdGlvbj4KCiAgICAgICAgPHNlY3Rpb24gaWQ9InJlc3VsdC1zZWN0aW9uIiBjbGFzcz0ibXQt"
    "OCBoaWRkZW4iPgogICAgICAgICAgICA8ZGl2IGNsYXNzPSJyb3VuZGVkLWxnIGJvcmRlciBib3Jk"
    "ZXItYm9yZGVyIGJnLWNhcmQgc2hhZG93LXNtIj4KICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9"
    "ImZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktYmV0d2VlbiBib3JkZXItYiBib3JkZXItYm9yZGVy"
    "IHB4LTQgcHktMyI+CiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0iZmxleCBpdGVtcy1j"
    "ZW50ZXIgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBpZD0icmVzdWx0LWlj"
    "b24iPjwvc3Bhbj4KICAgICAgICAgICAgICAgICAgICAgICAgPGgyIGlkPSJyZXN1bHQtdGl0bGUi"
    "IGNsYXNzPSJ0ZXh0LXNtIGZvbnQtc2VtaWJvbGQgdGV4dC1jYXJkLWZvcmVncm91bmQiPjwvaDI+"
    "CiAgICAgICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFz"
    "cz0iZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAgICAgICA8YnV0"
    "dG9uIGlkPSJjb3B5LWJ0biIgY2xhc3M9ImlubGluZS1mbGV4IGl0ZW1zLWNlbnRlciBnYXAtMS41"
    "IHJvdW5kZWQtbWQgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZCBweC0yLjUgcHkt"
    "MS41IHRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIHRyYW5zaXRpb24t"
    "Y29sb3JzIGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0LWFjY2VudC1mb3JlZ3JvdW5kIGN1cnNv"
    "ci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJj"
    "b3B5IiBjbGFzcz0iaC0zLjUgdy0zLjUiPjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "IENvcGlhcgogICAgICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPGJ1dHRvbiBpZD0icmVnZW5lcmF0ZS1idG4iIGNsYXNzPSJpbmxpbmUtZmxleCBp"
    "dGVtcy1jZW50ZXIgZ2FwLTEuNSByb3VuZGVkLW1kIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWJh"
    "Y2tncm91bmQgcHgtMi41IHB5LTEuNSB0ZXh0LXhzIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9y"
    "ZWdyb3VuZCB0cmFuc2l0aW9uLWNvbG9ycyBob3ZlcjpiZy1hY2NlbnQgaG92ZXI6dGV4dC1hY2Nl"
    "bnQtZm9yZWdyb3VuZCBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAgICAgICAgICAgICAgICAgICAg"
    "ICA8aSBkYXRhLWx1Y2lkZT0icmVmcmVzaC1jdyIgY2xhc3M9ImgtMy41IHctMy41Ij48L2k+CiAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICBSZWdlbmVyYXIKICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPC9idXR0b24+CiAgICAgICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICA8"
    "L2Rpdj4KICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9InAtNCI+CiAgICAgICAgICAgICAgICAg"
    "ICAgPHByZSBpZD0icmVzdWx0LWNvbnRlbnQiIGNsYXNzPSJ3aGl0ZXNwYWNlLXByZS13cmFwIGJy"
    "ZWFrLXdvcmRzIGZvbnQtbW9ubyB0ZXh0LXNtIGxlYWRpbmctcmVsYXhlZCB0ZXh0LWNhcmQtZm9y"
    "ZWdyb3VuZCI+PC9wcmU+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICAgIDxk"
    "aXYgY2xhc3M9ImJvcmRlci10IGJvcmRlci1ib3JkZXIgcHgtNCBweS0yIj4KICAgICAgICAgICAg"
    "ICAgICAgICA8cCBpZD0icmVzdWx0LXRpbWVzdGFtcCIgY2xhc3M9InRleHQteHMgdGV4dC1tdXRl"
    "ZC1mb3JlZ3JvdW5kIj48L3A+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgPC9k"
    "aXY+CiAgICAgICAgPC9zZWN0aW9uPgoKICAgIDwvbWFpbj4KCiAgICA8Zm9vdGVyIGNsYXNzPSJi"
    "b3JkZXItdCBib3JkZXItYm9yZGVyIHB5LTYgdGV4dC1jZW50ZXIgdGV4dC14cyB0ZXh0LW11dGVk"
    "LWZvcmVncm91bmQiPgogICAgICAgIDxkaXYgaWQ9InBlYWstaW5mbyI+PC9kaXY+CiAgICA8L2Zv"
    "b3Rlcj4KCiAgICA8c2NyaXB0IHNyYz0iL2pzL2FwcC5qcyI+PC9zY3JpcHQ+CjwvYm9keT4KPC9o"
    "dG1sPgo="
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
