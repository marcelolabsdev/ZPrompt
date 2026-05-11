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
    "b3JlZ3JvdW5kIG1iLTIiPkdMTSBDb2RpbmcgUGxhbjwvcD4KICAgICAgICAgICAgICAgIDxkaXYg"
    "Y2xhc3M9ImdyaWQgZ3JpZC1jb2xzLTQgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAgIDxidXR0"
    "b24gZGF0YS10eXBlPSJzeXN0ZW0iIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRlbXMt"
    "Y2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1ib3Jk"
    "ZXIgYmctY2FyZCBweC0zIHB5LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92"
    "ZXI6c2hhZG93LXNtIGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGkg"
    "ZGF0YS1sdWNpZGU9Im1vbml0b3IiIGNsYXNzPSJoLTUgdy01Ij48L2k+CiAgICAgICAgICAgICAg"
    "ICAgICAgICAgIDxzcGFuIGNsYXNzPSJ0ZXh0LXhzIGZvbnQtbWVkaXVtIHRleHQtY2FyZC1mb3Jl"
    "Z3JvdW5kIj5TWVNURU08L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAg"
    "ICAgICAgICAgICAgICAgPGJ1dHRvbiBkYXRhLXR5cGU9InN0YXJ0IiBjbGFzcz0icHJvbXB0LXR5"
    "cGUtY2FyZCBmbGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWNlbnRlciBnYXAtMiByb3VuZGVkLWxn"
    "IGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgcHgtMyBweS0yIHRyYW5zaXRpb24tYWxsIGhv"
    "dmVyOmJvcmRlci1yaW5nIGhvdmVyOnNoYWRvdy1zbSBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAg"
    "ICAgICAgICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJyb2NrZXQiIGNsYXNzPSJoLTQgdy00Ij48"
    "L2k+CiAgICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzPSJ0ZXh0LXhzIGZvbnQtbWVk"
    "aXVtIHRleHQtY2FyZC1mb3JlZ3JvdW5kIj5TVEFSVDwvc3Bhbj4KICAgICAgICAgICAgICAgICAg"
    "ICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0iZm9sbG93"
    "dXAiIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2Vu"
    "dGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctY2FyZCBweC0zIHB5"
    "LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92ZXI6c2hhZG93LXNtIGN1cnNv"
    "ci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InJlcGVh"
    "dCIgY2xhc3M9ImgtNSB3LTUiPjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xh"
    "c3M9InRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPkZPTExPVy1VUDwv"
    "c3Bhbj4KICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8"
    "YnV0dG9uIGRhdGEtdHlwZT0iZGVidWciIGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggaXRl"
    "bXMtY2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1i"
    "b3JkZXIgYmctY2FyZCBweC0zIHB5LTIgdHJhbnNpdGlvbi1hbGwgaG92ZXI6Ym9yZGVyLXJpbmcg"
    "aG92ZXI6c2hhZG93LXNtIGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAg"
    "PGkgZGF0YS1sdWNpZGU9ImJ1ZyIgY2xhc3M9ImgtNCB3LTQiPjwvaT4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1jYXJkLWZvcmVn"
    "cm91bmQiPkRFQlVHPC9zcGFuPgogICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAg"
    "ICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgIDwvZGl2PgoKICAgICAgICAgICAgPGRpdj4KICAg"
    "ICAgICAgICAgICAgIDxsYWJlbCBmb3I9InVzZXItaW5wdXQiIGNsYXNzPSJtYi0yIGJsb2NrIHRl"
    "eHQtc20gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIHRleHQtY2VudGVyIj5EZXNjcmliZSB0dSBwcm95"
    "ZWN0byB5IG9idGllbmUgcHJvbXB0cyBvcHRpbWl6YWRvcyBwYXJhIGRlc2Fycm9sbG8gZGUgc29m"
    "dHdhcmUuPC9sYWJlbD4KICAgICAgICAgICAgICAgIDx0ZXh0YXJlYQogICAgICAgICAgICAgICAg"
    "ICAgIGlkPSJ1c2VyLWlucHV0IgogICAgICAgICAgICAgICAgICAgIHJvd3M9IjQiCiAgICAgICAg"
    "ICAgICAgICAgICAgY2xhc3M9ImZsZXggdy1mdWxsIHJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1p"
    "bnB1dCBiZy1iYWNrZ3JvdW5kIHB4LTMgcHktMi41IHRleHQtc20gc2hhZG93LXhzIHRyYW5zaXRp"
    "b24tY29sb3JzIHBsYWNlaG9sZGVyOnRleHQtbXV0ZWQtZm9yZWdyb3VuZCBmb2N1cy12aXNpYmxl"
    "Om91dGxpbmUtbm9uZSBmb2N1cy12aXNpYmxlOnJpbmctMiBmb2N1cy12aXNpYmxlOnJpbmctcmlu"
    "ZyByZXNpemUtbm9uZSIKICAgICAgICAgICAgICAgICAgICBwbGFjZWhvbGRlcj0iRWplbXBsbzog"
    "Q3JlYXIgdW5hIEFQSSBSRVNUIGNvbiBQeXRob24geSBGYXN0QVBJIHBhcmEgZ2VzdGlvbiBkZSB0"
    "YXJlYXMsIGNvbiBhdXRlbnRpY2FjaW9uIEpXVCB5IGJhc2UgZGUgZGF0b3MgUG9zdGdyZVNRTC4u"
    "LiIKICAgICAgICAgICAgICAgID48L3RleHRhcmVhPgogICAgICAgICAgICA8L2Rpdj4KCiAgICAg"
    "ICAgICAgIDxkaXYgY2xhc3M9ImdyaWQgZ3JpZC1jb2xzLTEgZ2FwLTQgc206Z3JpZC1jb2xzLTMi"
    "PgogICAgICAgICAgICAgICAgPGRpdj4KICAgICAgICAgICAgICAgICAgICA8bGFiZWwgZm9yPSJs"
    "YW5ndWFnZS1zZWxlY3QiIGNsYXNzPSJtYi0yIGJsb2NrIHRleHQtc20gZm9udC1tZWRpdW0gdGV4"
    "dC1tdXRlZC1mb3JlZ3JvdW5kIj5MZW5ndWFqZSAob3BjaW9uYWwpPC9sYWJlbD4KICAgICAgICAg"
    "ICAgICAgICAgICA8c2VsZWN0IGlkPSJsYW5ndWFnZS1zZWxlY3QiIGNsYXNzPSJmbGV4IGgtOSB3"
    "LWZ1bGwgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWlucHV0IGJnLWJhY2tncm91bmQgcHgtMyB0"
    "ZXh0LXNtIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9ycyBmb2N1cy12aXNpYmxlOm91dGxpbmUt"
    "bm9uZSBmb2N1cy12aXNpYmxlOnJpbmctMiBmb2N1cy12aXNpYmxlOnJpbmctcmluZyI+CiAgICAg"
    "ICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IiI+QXV0by1kZXRlY3Rhcjwvb3B0aW9u"
    "PgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJQeXRob24iPlB5dGhvbjwv"
    "b3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJUeXBlU2NyaXB0"
    "Ij5UeXBlU2NyaXB0PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFs"
    "dWU9IkRhcnQiPkRhcnQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2"
    "YWx1ZT0iSmF2YVNjcmlwdCI+SmF2YVNjcmlwdDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJSdXN0Ij5SdXN0PC9vcHRpb24+CiAgICAgICAgICAgICAgICAg"
    "ICAgICAgIDxvcHRpb24gdmFsdWU9IkdvIj5Hbzwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJKYXZhIj5KYXZhPC9vcHRpb24+CiAgICAgICAgICAgICAgICAg"
    "ICAgICAgIDxvcHRpb24gdmFsdWU9IkMjIj5DIzwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJQSFAiPlBIUDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8b3B0aW9uIHZhbHVlPSJSdWJ5Ij5SdWJ5PC9vcHRpb24+CiAgICAgICAgICAgICAgICAg"
    "ICAgICAgIDxvcHRpb24gdmFsdWU9IlN3aWZ0Ij5Td2lmdDwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJLb3RsaW4iPktvdGxpbjwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgIDwvc2VsZWN0PgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAg"
    "ICAgICA8ZGl2PgogICAgICAgICAgICAgICAgICAgIDxsYWJlbCBmb3I9ImZyYW1ld29yay1zZWxl"
    "Y3QiIGNsYXNzPSJtYi0yIGJsb2NrIHRleHQtc20gZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3Jl"
    "Z3JvdW5kIj5GcmFtZXdvcmsgKG9wY2lvbmFsKTwvbGFiZWw+CiAgICAgICAgICAgICAgICAgICAg"
    "PHNlbGVjdCBpZD0iZnJhbWV3b3JrLXNlbGVjdCIgY2xhc3M9ImZsZXggaC05IHctZnVsbCByb3Vu"
    "ZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFja2dyb3VuZCBweC0zIHRleHQtc20gc2hh"
    "ZG93LXhzIHRyYW5zaXRpb24tY29sb3JzIGZvY3VzLXZpc2libGU6b3V0bGluZS1ub25lIGZvY3Vz"
    "LXZpc2libGU6cmluZy0yIGZvY3VzLXZpc2libGU6cmluZy1yaW5nIj4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iIj5OaW5ndW5vIC8gQXV0bzwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJGYXN0QVBJIj5GYXN0QVBJPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkRqYW5nbyI+RGphbmdvPC9v"
    "cHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZsdXR0ZXIiPkZs"
    "dXR0ZXI8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iRmxh"
    "c2siPkZsYXNrPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9"
    "Ik5leHQuanMiPk5leHQuanM8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iUmVhY3QiPlJlYWN0PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxv"
    "cHRpb24gdmFsdWU9IlZ1ZS5qcyI+VnVlLmpzPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAg"
    "ICAgIDxvcHRpb24gdmFsdWU9IkV4cHJlc3MiPkV4cHJlc3M8L29wdGlvbj4KICAgICAgICAgICAg"
    "ICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iTmVzdEpTIj5OZXN0SlM8L29wdGlvbj4KICAgICAg"
    "ICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iU3ByaW5nIEJvb3QiPlNwcmluZyBCb290"
    "PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkFjdGl4Ij5B"
    "Y3RpeDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJBeHVt"
    "Ij5BeHVtPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9Ikxh"
    "cmF2ZWwiPkxhcmF2ZWw8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2"
    "YWx1ZT0iUmFpbHMiPlJhaWxzPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgPC9zZWxlY3Q+"
    "CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICAgIDxkaXY+CiAgICAgICAgICAg"
    "ICAgICAgICAgPGxhYmVsIGZvcj0iZGF0YWJhc2Utc2VsZWN0IiBjbGFzcz0ibWItMiBibG9jayB0"
    "ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+QmFzZSBkZSBkYXRvcyAo"
    "b3BjaW9uYWwpPC9sYWJlbD4KICAgICAgICAgICAgICAgICAgICA8c2VsZWN0IGlkPSJkYXRhYmFz"
    "ZS1zZWxlY3QiIGNsYXNzPSJmbGV4IGgtOSB3LWZ1bGwgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVy"
    "LWlucHV0IGJnLWJhY2tncm91bmQgcHgtMyB0ZXh0LXNtIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNv"
    "bG9ycyBmb2N1cy12aXNpYmxlOm91dGxpbmUtbm9uZSBmb2N1cy12aXNpYmxlOnJpbmctMiBmb2N1"
    "cy12aXNpYmxlOnJpbmctcmluZyI+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFs"
    "dWU9IiI+TmluZ3VuYSAvIEF1dG88L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9w"
    "dGlvbiB2YWx1ZT0iU3VwYWJhc2UiPlN1cGFiYXNlICh3ZWIvQVBJKTwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJGaXJlYmFzZSI+RmlyZWJhc2UgKGFwcHMg"
    "bW92aWxlcyk8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0i"
    "UG9zdGdyZVNRTCI+UG9zdGdyZVNRTDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8"
    "b3B0aW9uIHZhbHVlPSJNeVNRTCI+TXlTUUw8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPG9wdGlvbiB2YWx1ZT0iTW9uZ29EQiI+TW9uZ29EQjwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJTUUxpdGUiPlNRTGl0ZTwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJSZWRpcyI+UmVkaXM8L29wdGlvbj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iTWFyaWFEQiI+TWFyaWFEQjwvb3B0"
    "aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJQbGFuZXRTY2FsZSI+"
    "UGxhbmV0U2NhbGU8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1"
    "ZT0iQ29ja3JvYWNoREIiPkNvY2tyb2FjaERCPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAg"
    "PC9zZWxlY3Q+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+CgogICAg"
    "ICAgICAgICA8YnV0dG9uCiAgICAgICAgICAgICAgICBpZD0iZ2VuZXJhdGUtYnRuIgogICAgICAg"
    "ICAgICAgICAgY2xhc3M9ImlubGluZS1mbGV4IHctZnVsbCBpdGVtcy1jZW50ZXIganVzdGlmeS1j"
    "ZW50ZXIgZ2FwLTIgcm91bmRlZC1sZyBiZy1wcmltYXJ5IHB4LTQgcHktMi41IHRleHQtc20gZm9u"
    "dC1tZWRpdW0gdGV4dC1wcmltYXJ5LWZvcmVncm91bmQgc2hhZG93LXhzIHRyYW5zaXRpb24tY29s"
    "b3JzIGhvdmVyOmJnLXByaW1hcnkvOTAgZGlzYWJsZWQ6cG9pbnRlci1ldmVudHMtbm9uZSBkaXNh"
    "YmxlZDpvcGFjaXR5LTUwIGN1cnNvci1wb2ludGVyIgogICAgICAgICAgICAgICAgZGlzYWJsZWQK"
    "ICAgICAgICAgICAgPgogICAgICAgICAgICAgICAgPHNwYW4gaWQ9ImJ0bi10ZXh0Ij5HRU5FUkFS"
    "IFBST01QVDwvc3Bhbj4KICAgICAgICAgICAgICAgIDxzcGFuIGlkPSJidG4tc3Bpbm5lciIgY2xh"
    "c3M9ImhpZGRlbiI+CiAgICAgICAgICAgICAgICAgICAgPHN2ZyBjbGFzcz0iaC00IHctNCBhbmlt"
    "YXRlLXNwaW4iIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSI+PGNpcmNsZSBjbGFzcz0i"
    "b3BhY2l0eS0yNSIgY3g9IjEyIiBjeT0iMTIiIHI9IjEwIiBzdHJva2U9ImN1cnJlbnRDb2xvciIg"
    "c3Ryb2tlLXdpZHRoPSI0Ij48L2NpcmNsZT48cGF0aCBjbGFzcz0ib3BhY2l0eS03NSIgZmlsbD0i"
    "Y3VycmVudENvbG9yIiBkPSJNNCAxMmE4IDggMCAwMTgtOFYwQzUuMzczIDAgMCA1LjM3MyAwIDEy"
    "aDR6Ij48L3BhdGg+PC9zdmc+CiAgICAgICAgICAgICAgICA8L3NwYW4+CiAgICAgICAgICAgIDwv"
    "YnV0dG9uPgoKICAgICAgICA8L3NlY3Rpb24+CgogICAgICAgIDxzZWN0aW9uIGlkPSJlcnJvci1z"
    "ZWN0aW9uIiBjbGFzcz0ibXQtNiBoaWRkZW4iPgogICAgICAgICAgICA8ZGl2IGNsYXNzPSJyb3Vu"
    "ZGVkLWxnIGJvcmRlciBib3JkZXItZGVzdHJ1Y3RpdmUvNTAgYmctZGVzdHJ1Y3RpdmUvMTAgcC00"
    "IHRleHQtc20gdGV4dC1kZXN0cnVjdGl2ZSI+CiAgICAgICAgICAgICAgICA8cCBpZD0iZXJyb3It"
    "bWVzc2FnZSI+PC9wPgogICAgICAgICAgICA8L2Rpdj4KICAgICAgICA8L3NlY3Rpb24+CgogICAg"
    "ICAgIDxzZWN0aW9uIGlkPSJyZXN1bHQtc2VjdGlvbiIgY2xhc3M9Im10LTggaGlkZGVuIj4KICAg"
    "ICAgICAgICAgPGRpdiBjbGFzcz0icm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1j"
    "YXJkIHNoYWRvdy1zbSI+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJmbGV4IGl0ZW1zLWNl"
    "bnRlciBqdXN0aWZ5LWJldHdlZW4gYm9yZGVyLWIgYm9yZGVyLWJvcmRlciBweC00IHB5LTMiPgog"
    "ICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZsZXggaXRlbXMtY2VudGVyIGdhcC0yIj4K"
    "ICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gaWQ9InJlc3VsdC1pY29uIj48L3NwYW4+CiAg"
    "ICAgICAgICAgICAgICAgICAgICAgIDxoMiBpZD0icmVzdWx0LXRpdGxlIiBjbGFzcz0idGV4dC1z"
    "bSBmb250LXNlbWlib2xkIHRleHQtY2FyZC1mb3JlZ3JvdW5kIj48L2gyPgogICAgICAgICAgICAg"
    "ICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZsZXggaXRlbXMt"
    "Y2VudGVyIGdhcC0yIj4KICAgICAgICAgICAgICAgICAgICAgICAgPGJ1dHRvbiBpZD0iY29weS1i"
    "dG4iIGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTEuNSByb3VuZGVkLW1kIGJv"
    "cmRlciBib3JkZXItYm9yZGVyIGJnLWJhY2tncm91bmQgcHgtMi41IHB5LTEuNSB0ZXh0LXhzIGZv"
    "bnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCB0cmFuc2l0aW9uLWNvbG9ycyBob3Zlcjpi"
    "Zy1hY2NlbnQgaG92ZXI6dGV4dC1hY2NlbnQtZm9yZWdyb3VuZCBjdXJzb3ItcG9pbnRlciI+CiAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0iY29weSIgY2xhc3M9Imgt"
    "My41IHctMy41Ij48L2k+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBDb3BpYXIKICAgICAg"
    "ICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0"
    "b24gaWQ9InJlZ2VuZXJhdGUtYnRuIiBjbGFzcz0iaW5saW5lLWZsZXggaXRlbXMtY2VudGVyIGdh"
    "cC0xLjUgcm91bmRlZC1tZCBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1iYWNrZ3JvdW5kIHB4LTIu"
    "NSBweS0xLjUgdGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LW11dGVkLWZvcmVncm91bmQgdHJhbnNp"
    "dGlvbi1jb2xvcnMgaG92ZXI6YmctYWNjZW50IGhvdmVyOnRleHQtYWNjZW50LWZvcmVncm91bmQg"
    "Y3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNp"
    "ZGU9InJlZnJlc2gtY3ciIGNsYXNzPSJoLTMuNSB3LTMuNSI+PC9pPgogICAgICAgICAgICAgICAg"
    "ICAgICAgICAgICAgUmVnZW5lcmFyCiAgICAgICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgog"
    "ICAgICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAg"
    "ICAgICAgICA8ZGl2IGNsYXNzPSJwLTQiPgogICAgICAgICAgICAgICAgICAgIDxwcmUgaWQ9InJl"
    "c3VsdC1jb250ZW50IiBjbGFzcz0id2hpdGVzcGFjZS1wcmUtd3JhcCBicmVhay13b3JkcyBmb250"
    "LW1vbm8gdGV4dC1zbSBsZWFkaW5nLXJlbGF4ZWQgdGV4dC1jYXJkLWZvcmVncm91bmQiPjwvcHJl"
    "PgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJib3Jk"
    "ZXItdCBib3JkZXItYm9yZGVyIHB4LTQgcHktMiI+CiAgICAgICAgICAgICAgICAgICAgPHAgaWQ9"
    "InJlc3VsdC10aW1lc3RhbXAiIGNsYXNzPSJ0ZXh0LXhzIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+"
    "PC9wPgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgIDwvZGl2PgogICAgICAgIDwv"
    "c2VjdGlvbj4KCiAgICA8L21haW4+CgogICAgPGZvb3RlciBjbGFzcz0iYm9yZGVyLXQgYm9yZGVy"
    "LWJvcmRlciBweS02IHRleHQtY2VudGVyIHRleHQteHMgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIj4K"
    "ICAgICAgICA8ZGl2IGlkPSJwZWFrLWluZm8iPjwvZGl2PgogICAgPC9mb290ZXI+CgogICAgPHNj"
    "cmlwdCBzcmM9Ii9qcy9hcHAuanMiPjwvc2NyaXB0Pgo8L2JvZHk+CjwvaHRtbD4K"
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
