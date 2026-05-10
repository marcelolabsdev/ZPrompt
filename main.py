import os
import base64
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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
    "ZXMuY3NzIj4KICAgIDxzY3JpcHQgc3JjPSJodHRwczovL3VucGtnLmNvbS9sdWNpZGVAbGF0ZXN0"
    "Ij48L3NjcmlwdD4KPC9oZWFkPgo8Ym9keSBjbGFzcz0ibWluLWgtc2NyZWVuIGJnLWJhY2tncm91"
    "bmQgdGV4dC1mb3JlZ3JvdW5kIGZvbnQtc2FucyBhbnRpYWxpYXNlZCI+CgogICAgPGhlYWRlciBj"
    "bGFzcz0ic3RpY2t5IHRvcC0wIHotNTAgdy1mdWxsIGJvcmRlci1iIGJvcmRlci1ib3JkZXIgYmct"
    "YmFja2dyb3VuZC84MCBiYWNrZHJvcC1ibHVyLXNtIj4KICAgICAgICA8ZGl2IGNsYXNzPSJteC1h"
    "dXRvIGZsZXggaC0xNCBtYXgtdy00eGwgaXRlbXMtY2VudGVyIHB4LTQgc206cHgtNiI+CiAgICAg"
    "ICAgICAgIDxkaXYgY2xhc3M9ImZsZXgtMSI+PC9kaXY+CiAgICAgICAgICAgIDxhIGhyZWY9Ii8i"
    "IGNsYXNzPSJmbGV4IGl0ZW1zLWNlbnRlciBnYXAtMiB0ZXh0LWxnIGZvbnQtc2VtaWJvbGQgdHJh"
    "Y2tpbmctdGlnaHQiPgogICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InphcCIgY2xhc3M9"
    "ImgtNSB3LTUgdGV4dC1wcmltYXJ5Ij48L2k+CiAgICAgICAgICAgICAgICA8c3Bhbj5aUHJvbXB0"
    "PC9zcGFuPgogICAgICAgICAgICA8L2E+CiAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZsZXgtMSBm"
    "bGV4IGl0ZW1zLWNlbnRlciBqdXN0aWZ5LWVuZCBnYXAtMyI+CiAgICAgICAgICAgICAgICA8YnV0"
    "dG9uIGlkPSJ0aGVtZS10b2dnbGUiIGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIganVz"
    "dGlmeS1jZW50ZXIgcm91bmRlZC1tZCBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1iYWNrZ3JvdW5k"
    "IHAtMiB0ZXh0LW11dGVkLWZvcmVncm91bmQgdHJhbnNpdGlvbi1jb2xvcnMgaG92ZXI6YmctYWNj"
    "ZW50IGhvdmVyOnRleHQtYWNjZW50LWZvcmVncm91bmQgY3Vyc29yLXBvaW50ZXIiPgogICAgICAg"
    "ICAgICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJzdW4iIGlkPSJ0aGVtZS1pY29uLXN1biIgY2xh"
    "c3M9ImgtNCB3LTQiPjwvaT4KICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0ibW9v"
    "biIgaWQ9InRoZW1lLWljb24tbW9vbiIgY2xhc3M9ImgtNCB3LTQgaGlkZGVuIj48L2k+CiAgICAg"
    "ICAgICAgICAgICA8L2J1dHRvbj4KICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgPC9kaXY+CiAg"
    "ICA8L2hlYWRlcj4KCiAgICA8bWFpbiBjbGFzcz0ibXgtYXV0byBtYXgtdy00eGwgcHgtNCBweS04"
    "IHNtOnB4LTYgc206cHktMTIiPgoKICAgICAgICA8c2VjdGlvbiBjbGFzcz0ibWItMTAgdGV4dC1j"
    "ZW50ZXIiPgogICAgICAgICAgICA8aDEgY2xhc3M9InRleHQtM3hsIGZvbnQtYm9sZCB0cmFja2lu"
    "Zy10aWdodCBzbTp0ZXh0LTR4bCI+CiAgICAgICAgICAgICAgICBHZW5lcmEgcHJvbXB0cyBlc3Ry"
    "dWN0dXJhZG9zCiAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC1wcmltYXJ5Ij5wYXJh"
    "IEdMTTwvc3Bhbj4KICAgICAgICAgICAgPC9oMT4KICAgICAgICAgICAgPHAgY2xhc3M9Im10LTMg"
    "dGV4dC1tdXRlZC1mb3JlZ3JvdW5kIj4KICAgICAgICAgICAgICAgIERlc2NyaWJlIHR1IHByb3ll"
    "Y3RvIHkgb2J0aWVuZSBwcm9tcHRzIG9wdGltaXphZG9zIHBhcmEgZGVzYXJyb2xsbyBkZSBzb2Z0"
    "d2FyZS4KICAgICAgICAgICAgPC9wPgogICAgICAgIDwvc2VjdGlvbj4KCiAgICAgICAgPHNlY3Rp"
    "b24gY2xhc3M9InNwYWNlLXktNiI+CgogICAgICAgICAgICA8ZGl2PgogICAgICAgICAgICAgICAg"
    "PGRpdiBjbGFzcz0iZ3JpZCBncmlkLWNvbHMtNCBnYXAtMiI+CiAgICAgICAgICAgICAgICAgICAg"
    "PGJ1dHRvbiBkYXRhLXR5cGU9InN5c3RlbSIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxleCBp"
    "dGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgZ2FwLTIgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVy"
    "LWJvcmRlciBiZy1jYXJkIHB4LTMgcHktMiB0cmFuc2l0aW9uLWFsbCBob3Zlcjpib3JkZXItcmlu"
    "ZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAgICAg"
    "ICA8aSBkYXRhLWx1Y2lkZT0ibW9uaXRvciIgY2xhc3M9ImgtNCB3LTQiPjwvaT4KICAgICAgICAg"
    "ICAgICAgICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1jYXJk"
    "LWZvcmVncm91bmQiPlN5c3RlbTwvc3Bhbj4KICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj4K"
    "ICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0ic3RhcnQiIGNsYXNzPSJwcm9t"
    "cHQtdHlwZS1jYXJkIGZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5k"
    "ZWQtbGcgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctY2FyZCBweC0zIHB5LTIgdHJhbnNpdGlvbi1h"
    "bGwgaG92ZXI6Ym9yZGVyLXJpbmcgaG92ZXI6c2hhZG93LXNtIGN1cnNvci1wb2ludGVyIj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPGkgZGF0YS1sdWNpZGU9InJvY2tldCIgY2xhc3M9ImgtNCB3"
    "LTQiPjwvaT4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9u"
    "dC1tZWRpdW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPlN0YXJ0PC9zcGFuPgogICAgICAgICAgICAg"
    "ICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDxidXR0b24gZGF0YS10eXBlPSJm"
    "b2xsb3d1cCIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxleCBpdGVtcy1jZW50ZXIganVzdGlm"
    "eS1jZW50ZXIgZ2FwLTIgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHB4"
    "LTMgcHktMiB0cmFuc2l0aW9uLWFsbCBob3Zlcjpib3JkZXItcmluZyBob3ZlcjpzaGFkb3ctc20g"
    "Y3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0i"
    "cmVwZWF0IiBjbGFzcz0iaC00IHctNCI+PC9pPgogICAgICAgICAgICAgICAgICAgICAgICA8c3Bh"
    "biBjbGFzcz0idGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+Rm9sbG93"
    "LVVwPC9zcGFuPgogICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAg"
    "ICAgIDxidXR0b24gZGF0YS10eXBlPSJkZWJ1ZyIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxl"
    "eCBpdGVtcy1jZW50ZXIganVzdGlmeS1jZW50ZXIgZ2FwLTIgcm91bmRlZC1sZyBib3JkZXIgYm9y"
    "ZGVyLWJvcmRlciBiZy1jYXJkIHB4LTMgcHktMiB0cmFuc2l0aW9uLWFsbCBob3Zlcjpib3JkZXIt"
    "cmluZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8aSBkYXRhLWx1Y2lkZT0iYnVnIiBjbGFzcz0iaC00IHctNCI+PC9pPgogICAgICAgICAg"
    "ICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LWNhcmQt"
    "Zm9yZWdyb3VuZCI+RGVidWc8L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAg"
    "ICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+CgogICAgICAgICAgICA8ZGl2"
    "PgogICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0idXNlci1pbnB1dCIgY2xhc3M9Im1iLTIgYmxv"
    "Y2sgdGV4dC1zbSBmb250LW1lZGl1bSI+RGVzY3JpYmUgdHUgcHJveWVjdG8gbyB0YXJlYTwvbGFi"
    "ZWw+CiAgICAgICAgICAgICAgICA8dGV4dGFyZWEKICAgICAgICAgICAgICAgICAgICBpZD0idXNl"
    "ci1pbnB1dCIKICAgICAgICAgICAgICAgICAgICByb3dzPSI0IgogICAgICAgICAgICAgICAgICAg"
    "IGNsYXNzPSJmbGV4IHctZnVsbCByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFj"
    "a2dyb3VuZCBweC0zIHB5LTIuNSB0ZXh0LXNtIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9ycyBw"
    "bGFjZWhvbGRlcjp0ZXh0LW11dGVkLWZvcmVncm91bmQgZm9jdXMtdmlzaWJsZTpvdXRsaW5lLW5v"
    "bmUgZm9jdXMtdmlzaWJsZTpyaW5nLTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJpbmcgcmVzaXplLW5v"
    "bmUiCiAgICAgICAgICAgICAgICAgICAgcGxhY2Vob2xkZXI9IkVqZW1wbG86IENyZWFyIHVuYSBB"
    "UEkgUkVTVCBjb24gUHl0aG9uIHkgRmFzdEFQSSBwYXJhIGdlc3Rpb24gZGUgdGFyZWFzLCBjb24g"
    "YXV0ZW50aWNhY2lvbiBKV1QgeSBiYXNlIGRlIGRhdG9zIFBvc3RncmVTUUwuLi4iCiAgICAgICAg"
    "ICAgICAgICA+PC90ZXh0YXJlYT4KICAgICAgICAgICAgPC9kaXY+CgogICAgICAgICAgICA8ZGl2"
    "IGNsYXNzPSJncmlkIGdyaWQtY29scy0xIGdhcC00IHNtOmdyaWQtY29scy0yIj4KICAgICAgICAg"
    "ICAgICAgIDxkaXY+CiAgICAgICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0ibGFuZ3VhZ2Utc2Vs"
    "ZWN0IiBjbGFzcz0ibWItMiBibG9jayB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9y"
    "ZWdyb3VuZCI+TGVuZ3VhamUgKG9wY2lvbmFsKTwvbGFiZWw+CiAgICAgICAgICAgICAgICAgICAg"
    "PHNlbGVjdCBpZD0ibGFuZ3VhZ2Utc2VsZWN0IiBjbGFzcz0iZmxleCBoLTkgdy1mdWxsIHJvdW5k"
    "ZWQtbGcgYm9yZGVyIGJvcmRlci1pbnB1dCBiZy1iYWNrZ3JvdW5kIHB4LTMgdGV4dC1zbSBzaGFk"
    "b3cteHMgdHJhbnNpdGlvbi1jb2xvcnMgZm9jdXMtdmlzaWJsZTpvdXRsaW5lLW5vbmUgZm9jdXMt"
    "dmlzaWJsZTpyaW5nLTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJpbmciPgogICAgICAgICAgICAgICAg"
    "ICAgICAgICA8b3B0aW9uIHZhbHVlPSIiPkF1dG8tZGV0ZWN0YXI8L29wdGlvbj4KICAgICAgICAg"
    "ICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iUHl0aG9uIj5QeXRob248L29wdGlvbj4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iVHlwZVNjcmlwdCI+VHlwZVNjcmlw"
    "dDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJEYXJ0Ij5E"
    "YXJ0PC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkphdmFT"
    "Y3JpcHQiPkphdmFTY3JpcHQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iUnVzdCI+UnVzdDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0"
    "aW9uIHZhbHVlPSJHbyI+R288L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iSmF2YSI+SmF2YTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0"
    "aW9uIHZhbHVlPSJDIyI+QyM8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iUEhQIj5QSFA8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iUnVieSI+UnVieTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0"
    "aW9uIHZhbHVlPSJTd2lmdCI+U3dpZnQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAg"
    "PG9wdGlvbiB2YWx1ZT0iS290bGluIj5Lb3RsaW48L29wdGlvbj4KICAgICAgICAgICAgICAgICAg"
    "ICA8L3NlbGVjdD4KICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgPGRpdj4K"
    "ICAgICAgICAgICAgICAgICAgICA8bGFiZWwgZm9yPSJmcmFtZXdvcmstc2VsZWN0IiBjbGFzcz0i"
    "bWItMiBibG9jayB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+RnJh"
    "bWV3b3JrIChvcGNpb25hbCk8L2xhYmVsPgogICAgICAgICAgICAgICAgICAgIDxzZWxlY3QgaWQ9"
    "ImZyYW1ld29yay1zZWxlY3QiIGNsYXNzPSJmbGV4IGgtOSB3LWZ1bGwgcm91bmRlZC1sZyBib3Jk"
    "ZXIgYm9yZGVyLWlucHV0IGJnLWJhY2tncm91bmQgcHgtMyB0ZXh0LXNtIHNoYWRvdy14cyB0cmFu"
    "c2l0aW9uLWNvbG9ycyBmb2N1cy12aXNpYmxlOm91dGxpbmUtbm9uZSBmb2N1cy12aXNpYmxlOnJp"
    "bmctMiBmb2N1cy12aXNpYmxlOnJpbmctcmluZyI+CiAgICAgICAgICAgICAgICAgICAgICAgIDxv"
    "cHRpb24gdmFsdWU9IiI+TmluZ3VubyAvIEF1dG88L29wdGlvbj4KICAgICAgICAgICAgICAgICAg"
    "ICAgICAgPG9wdGlvbiB2YWx1ZT0iRmFzdEFQSSI+RmFzdEFQSTwvb3B0aW9uPgogICAgICAgICAg"
    "ICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJEamFuZ28iPkRqYW5nbzwvb3B0aW9uPgogICAg"
    "ICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJGbHV0dGVyIj5GbHV0dGVyPC9vcHRp"
    "b24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZsYXNrIj5GbGFzazwv"
    "b3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJOZXh0LmpzIj5O"
    "ZXh0LmpzPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJl"
    "YWN0Ij5SZWFjdDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVl"
    "PSJWdWUuanMiPlZ1ZS5qczwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9u"
    "IHZhbHVlPSJFeHByZXNzIj5FeHByZXNzPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAg"
    "IDxvcHRpb24gdmFsdWU9Ik5lc3RKUyI+TmVzdEpTPC9vcHRpb24+CiAgICAgICAgICAgICAgICAg"
    "ICAgICAgIDxvcHRpb24gdmFsdWU9IlNwcmluZyBCb290Ij5TcHJpbmcgQm9vdDwvb3B0aW9uPgog"
    "ICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJBY3RpeCI+QWN0aXg8L29wdGlv"
    "bj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iQXh1bSI+QXh1bTwvb3B0"
    "aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJMYXJhdmVsIj5MYXJh"
    "dmVsPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJhaWxz"
    "Ij5SYWlsczwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgIDwvc2VsZWN0PgogICAgICAgICAg"
    "ICAgICAgPC9kaXY+CiAgICAgICAgICAgIDwvZGl2PgoKICAgICAgICAgICAgPGJ1dHRvbgogICAg"
    "ICAgICAgICAgICAgaWQ9ImdlbmVyYXRlLWJ0biIKICAgICAgICAgICAgICAgIGNsYXNzPSJpbmxp"
    "bmUtZmxleCB3LWZ1bGwgaXRlbXMtY2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5kZWQt"
    "bGcgYmctcHJpbWFyeSBweC00IHB5LTIuNSB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtcHJpbWFy"
    "eS1mb3JlZ3JvdW5kIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9ycyBob3ZlcjpiZy1wcmltYXJ5"
    "LzkwIGRpc2FibGVkOnBvaW50ZXItZXZlbnRzLW5vbmUgZGlzYWJsZWQ6b3BhY2l0eS01MCBjdXJz"
    "b3ItcG9pbnRlciIKICAgICAgICAgICAgICAgIGRpc2FibGVkCiAgICAgICAgICAgID4KICAgICAg"
    "ICAgICAgICAgIDxpIGRhdGEtbHVjaWRlPSJ6YXAiIGNsYXNzPSJoLTQgdy00Ij48L2k+CiAgICAg"
    "ICAgICAgICAgICA8c3BhbiBpZD0iYnRuLXRleHQiPkdlbmVyYXIgUHJvbXB0PC9zcGFuPgogICAg"
    "ICAgICAgICAgICAgPHNwYW4gaWQ9ImJ0bi1zcGlubmVyIiBjbGFzcz0iaGlkZGVuIj4KICAgICAg"
    "ICAgICAgICAgICAgICA8c3ZnIGNsYXNzPSJoLTQgdy00IGFuaW1hdGUtc3BpbiIgdmlld0JveD0i"
    "MCAwIDI0IDI0IiBmaWxsPSJub25lIj48Y2lyY2xlIGNsYXNzPSJvcGFjaXR5LTI1IiBjeD0iMTIi"
    "IGN5PSIxMiIgcj0iMTAiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjQiPjwv"
    "Y2lyY2xlPjxwYXRoIGNsYXNzPSJvcGFjaXR5LTc1IiBmaWxsPSJjdXJyZW50Q29sb3IiIGQ9Ik00"
    "IDEyYTggOCAwIDAxOC04VjBDNS4zNzMgMCAwIDUuMzczIDAgMTJoNHoiPjwvcGF0aD48L3N2Zz4K"
    "ICAgICAgICAgICAgICAgIDwvc3Bhbj4KICAgICAgICAgICAgPC9idXR0b24+CgogICAgICAgIDwv"
    "c2VjdGlvbj4KCiAgICAgICAgPHNlY3Rpb24gaWQ9ImVycm9yLXNlY3Rpb24iIGNsYXNzPSJtdC02"
    "IGhpZGRlbiI+CiAgICAgICAgICAgIDxkaXYgY2xhc3M9InJvdW5kZWQtbGcgYm9yZGVyIGJvcmRl"
    "ci1kZXN0cnVjdGl2ZS81MCBiZy1kZXN0cnVjdGl2ZS8xMCBwLTQgdGV4dC1zbSB0ZXh0LWRlc3Ry"
    "dWN0aXZlIj4KICAgICAgICAgICAgICAgIDxwIGlkPSJlcnJvci1tZXNzYWdlIj48L3A+CiAgICAg"
    "ICAgICAgIDwvZGl2PgogICAgICAgIDwvc2VjdGlvbj4KCiAgICAgICAgPHNlY3Rpb24gaWQ9InJl"
    "c3VsdC1zZWN0aW9uIiBjbGFzcz0ibXQtOCBoaWRkZW4iPgogICAgICAgICAgICA8ZGl2IGNsYXNz"
    "PSJyb3VuZGVkLWxnIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgc2hhZG93LXNtIj4KICAg"
    "ICAgICAgICAgICAgIDxkaXYgY2xhc3M9ImZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktYmV0d2Vl"
    "biBib3JkZXItYiBib3JkZXItYm9yZGVyIHB4LTQgcHktMyI+CiAgICAgICAgICAgICAgICAgICAg"
    "PGRpdiBjbGFzcz0iZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAg"
    "ICAgICA8c3BhbiBpZD0icmVzdWx0LWljb24iPjwvc3Bhbj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPGgyIGlkPSJyZXN1bHQtdGl0bGUiIGNsYXNzPSJ0ZXh0LXNtIGZvbnQtc2VtaWJvbGQgdGV4"
    "dC1jYXJkLWZvcmVncm91bmQiPjwvaDI+CiAgICAgICAgICAgICAgICAgICAgPC9kaXY+CiAgICAg"
    "ICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0iZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTIiPgogICAg"
    "ICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGlkPSJjb3B5LWJ0biIgY2xhc3M9ImlubGluZS1m"
    "bGV4IGl0ZW1zLWNlbnRlciBnYXAtMS41IHJvdW5kZWQtbWQgYm9yZGVyIGJvcmRlci1ib3JkZXIg"
    "YmctYmFja2dyb3VuZCBweC0yLjUgcHktMS41IHRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1tdXRl"
    "ZC1mb3JlZ3JvdW5kIHRyYW5zaXRpb24tY29sb3JzIGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0"
    "LWFjY2VudC1mb3JlZ3JvdW5kIGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgICAgIDxpIGRhdGEtbHVjaWRlPSJjb3B5IiBjbGFzcz0iaC0zLjUgdy0zLjUiPjwvaT4KICAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgIENvcGlhcgogICAgICAgICAgICAgICAgICAgICAgICA8"
    "L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPGJ1dHRvbiBpZD0icmVnZW5lcmF0ZS1i"
    "dG4iIGNsYXNzPSJpbmxpbmUtZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTEuNSByb3VuZGVkLW1kIGJv"
    "cmRlciBib3JkZXItYm9yZGVyIGJnLWJhY2tncm91bmQgcHgtMi41IHB5LTEuNSB0ZXh0LXhzIGZv"
    "bnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCB0cmFuc2l0aW9uLWNvbG9ycyBob3Zlcjpi"
    "Zy1hY2NlbnQgaG92ZXI6dGV4dC1hY2NlbnQtZm9yZWdyb3VuZCBjdXJzb3ItcG9pbnRlciI+CiAg"
    "ICAgICAgICAgICAgICAgICAgICAgICAgICA8aSBkYXRhLWx1Y2lkZT0icmVmcmVzaC1jdyIgY2xh"
    "c3M9ImgtMy41IHctMy41Ij48L2k+CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBSZWdlbmVy"
    "YXIKICAgICAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAgICAgICAgICAgICAgICAg"
    "PC9kaXY+CiAgICAgICAgICAgICAgICA8L2Rpdj4KICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9"
    "InAtNCI+CiAgICAgICAgICAgICAgICAgICAgPHByZSBpZD0icmVzdWx0LWNvbnRlbnQiIGNsYXNz"
    "PSJ3aGl0ZXNwYWNlLXByZS13cmFwIGJyZWFrLXdvcmRzIGZvbnQtbW9ubyB0ZXh0LXNtIGxlYWRp"
    "bmctcmVsYXhlZCB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+PC9wcmU+CiAgICAgICAgICAgICAgICA8"
    "L2Rpdj4KICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9ImJvcmRlci10IGJvcmRlci1ib3JkZXIg"
    "cHgtNCBweS0yIj4KICAgICAgICAgICAgICAgICAgICA8cCBpZD0icmVzdWx0LXRpbWVzdGFtcCIg"
    "Y2xhc3M9InRleHQteHMgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIj48L3A+CiAgICAgICAgICAgICAg"
    "ICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgPC9zZWN0aW9uPgoKICAgIDwvbWFp"
    "bj4KCiAgICA8Zm9vdGVyIGNsYXNzPSJib3JkZXItdCBib3JkZXItYm9yZGVyIHB5LTYgdGV4dC1j"
    "ZW50ZXIgdGV4dC14cyB0ZXh0LW11dGVkLWZvcmVncm91bmQiPgogICAgICAgIDxwPlpQcm9tcHQg"
    "Jm1kYXNoOyBHZW5lcmFkb3IgZGUgcHJvbXB0cyBlc3RydWN0dXJhZG9zIHBhcmEgR0xNPC9wPgog"
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


class PromptResponse(BaseModel):
    prompt: str
    prompt_type: str
    label: str
    timestamp: str


@app.get("/")
def serve_index():
    return HTMLResponse(content=INDEX_HTML)


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
