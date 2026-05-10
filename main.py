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
    "ZXMuY3NzIj4KPC9oZWFkPgo8Ym9keSBjbGFzcz0ibWluLWgtc2NyZWVuIGJnLWJhY2tncm91bmQg"
    "dGV4dC1mb3JlZ3JvdW5kIGZvbnQtc2FucyBhbnRpYWxpYXNlZCI+CgogICAgPGhlYWRlciBjbGFz"
    "cz0ic3RpY2t5IHRvcC0wIHotNTAgdy1mdWxsIGJvcmRlci1iIGJvcmRlci1ib3JkZXIgYmctYmFj"
    "a2dyb3VuZC84MCBiYWNrZHJvcC1ibHVyLXNtIj4KICAgICAgICA8ZGl2IGNsYXNzPSJteC1hdXRv"
    "IGZsZXggaC0xNCBtYXgtdy00eGwgaXRlbXMtY2VudGVyIGp1c3RpZnktYmV0d2VlbiBweC00IHNt"
    "OnB4LTYiPgogICAgICAgICAgICA8YSBocmVmPSIvIiBjbGFzcz0iZmxleCBpdGVtcy1jZW50ZXIg"
    "Z2FwLTIgdGV4dC1sZyBmb250LXNlbWlib2xkIHRyYWNraW5nLXRpZ2h0Ij4KICAgICAgICAgICAg"
    "ICAgIDxzcGFuIGNsYXNzPSJ0ZXh0LXByaW1hcnkiPuKaoTwvc3Bhbj4KICAgICAgICAgICAgICAg"
    "IDxzcGFuPlpQcm9tcHQ8L3NwYW4+CiAgICAgICAgICAgIDwvYT4KICAgICAgICAgICAgPGRpdiBj"
    "bGFzcz0iZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTMiPgogICAgICAgICAgICAgICAgPGJ1dHRvbiBp"
    "ZD0idGhlbWUtdG9nZ2xlIiBjbGFzcz0iaW5saW5lLWZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnkt"
    "Y2VudGVyIHJvdW5kZWQtbWQgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZCBweC0y"
    "LjUgcHktMS41IHRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIHRyYW5z"
    "aXRpb24tY29sb3JzIGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0LWFjY2VudC1mb3JlZ3JvdW5k"
    "IGN1cnNvci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICA8c3BhbiBpZD0idGhlbWUtaWNv"
    "biI+4piA77iPPC9zcGFuPgogICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAgICAgICAgIDwv"
    "ZGl2PgogICAgICAgIDwvZGl2PgogICAgPC9oZWFkZXI+CgogICAgPG1haW4gY2xhc3M9Im14LWF1"
    "dG8gbWF4LXctNHhsIHB4LTQgcHktOCBzbTpweC02IHNtOnB5LTEyIj4KCiAgICAgICAgPHNlY3Rp"
    "b24gY2xhc3M9Im1iLTEwIHRleHQtY2VudGVyIj4KICAgICAgICAgICAgPGgxIGNsYXNzPSJ0ZXh0"
    "LTN4bCBmb250LWJvbGQgdHJhY2tpbmctdGlnaHQgc206dGV4dC00eGwiPgogICAgICAgICAgICAg"
    "ICAgR2VuZXJhIHByb21wdHMgZXN0cnVjdHVyYWRvcwogICAgICAgICAgICAgICAgPHNwYW4gY2xh"
    "c3M9InRleHQtcHJpbWFyeSI+cGFyYSBHTE08L3NwYW4+CiAgICAgICAgICAgIDwvaDE+CiAgICAg"
    "ICAgICAgIDxwIGNsYXNzPSJtdC0zIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+CiAgICAgICAgICAg"
    "ICAgICBEZXNjcmliZSB0dSBwcm95ZWN0byB5IG9idGllbmUgcHJvbXB0cyBvcHRpbWl6YWRvcyBw"
    "YXJhIGRlc2Fycm9sbG8gZGUgc29mdHdhcmUuCiAgICAgICAgICAgIDwvcD4KICAgICAgICA8L3Nl"
    "Y3Rpb24+CgogICAgICAgIDxzZWN0aW9uIGNsYXNzPSJzcGFjZS15LTYiPgoKICAgICAgICAgICAg"
    "PGRpdj4KICAgICAgICAgICAgICAgIDxsYWJlbCBjbGFzcz0ibWItMyBibG9jayB0ZXh0LXNtIGZv"
    "bnQtbWVkaXVtIj5TZWxlY2Npb25hIHRpcG8gZGUgcHJvbXB0PC9sYWJlbD4KICAgICAgICAgICAg"
    "ICAgIDxkaXYgY2xhc3M9ImdyaWQgZ3JpZC1jb2xzLTIgZ2FwLTMgc206Z3JpZC1jb2xzLTQiPgog"
    "ICAgICAgICAgICAgICAgICAgIDxidXR0b24gZGF0YS10eXBlPSJzeXN0ZW0iIGNsYXNzPSJwcm9t"
    "cHQtdHlwZS1jYXJkIGZsZXggZmxleC1jb2wgaXRlbXMtY2VudGVyIGdhcC0xLjUgcm91bmRlZC1s"
    "ZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHAtMyB0ZXh0LWNlbnRlciB0cmFuc2l0aW9u"
    "LWFsbCBob3Zlcjpib3JkZXItcmluZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29yLXBvaW50ZXIiPgog"
    "ICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14bCI+8J+Wpe+4jzwvc3Bh"
    "bj4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMgZm9udC1tZWRp"
    "dW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPlN5c3RlbTwvc3Bhbj4KICAgICAgICAgICAgICAgICAg"
    "ICA8L2J1dHRvbj4KICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGRhdGEtdHlwZT0ic3RhcnQi"
    "IGNsYXNzPSJwcm9tcHQtdHlwZS1jYXJkIGZsZXggZmxleC1jb2wgaXRlbXMtY2VudGVyIGdhcC0x"
    "LjUgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWJvcmRlciBiZy1jYXJkIHAtMyB0ZXh0LWNlbnRl"
    "ciB0cmFuc2l0aW9uLWFsbCBob3Zlcjpib3JkZXItcmluZyBob3ZlcjpzaGFkb3ctc20gY3Vyc29y"
    "LXBvaW50ZXIiPgogICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz0idGV4dC14bCI+"
    "8J+agDwvc3Bhbj4KICAgICAgICAgICAgICAgICAgICAgICAgPHNwYW4gY2xhc3M9InRleHQteHMg"
    "Zm9udC1tZWRpdW0gdGV4dC1jYXJkLWZvcmVncm91bmQiPlN0YXJ0PC9zcGFuPgogICAgICAgICAg"
    "ICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDxidXR0b24gZGF0YS10eXBl"
    "PSJmb2xsb3d1cCIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxleCBmbGV4LWNvbCBpdGVtcy1j"
    "ZW50ZXIgZ2FwLTEuNSByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgcC0z"
    "IHRleHQtY2VudGVyIHRyYW5zaXRpb24tYWxsIGhvdmVyOmJvcmRlci1yaW5nIGhvdmVyOnNoYWRv"
    "dy1zbSBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNz"
    "PSJ0ZXh0LXhsIj7wn5SEPC9zcGFuPgogICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFz"
    "cz0idGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+Rm9sbG93LVVwPC9z"
    "cGFuPgogICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDxi"
    "dXR0b24gZGF0YS10eXBlPSJkZWJ1ZyIgY2xhc3M9InByb21wdC10eXBlLWNhcmQgZmxleCBmbGV4"
    "LWNvbCBpdGVtcy1jZW50ZXIgZ2FwLTEuNSByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItYm9yZGVy"
    "IGJnLWNhcmQgcC0zIHRleHQtY2VudGVyIHRyYW5zaXRpb24tYWxsIGhvdmVyOmJvcmRlci1yaW5n"
    "IGhvdmVyOnNoYWRvdy1zbSBjdXJzb3ItcG9pbnRlciI+CiAgICAgICAgICAgICAgICAgICAgICAg"
    "IDxzcGFuIGNsYXNzPSJ0ZXh0LXhsIj7wn5CbPC9zcGFuPgogICAgICAgICAgICAgICAgICAgICAg"
    "ICA8c3BhbiBjbGFzcz0idGV4dC14cyBmb250LW1lZGl1bSB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+"
    "RGVidWc8L3NwYW4+CiAgICAgICAgICAgICAgICAgICAgPC9idXR0b24+CiAgICAgICAgICAgICAg"
    "ICA8L2Rpdj4KICAgICAgICAgICAgPC9kaXY+CgogICAgICAgICAgICA8ZGl2PgogICAgICAgICAg"
    "ICAgICAgPGxhYmVsIGZvcj0idXNlci1pbnB1dCIgY2xhc3M9Im1iLTIgYmxvY2sgdGV4dC1zbSBm"
    "b250LW1lZGl1bSI+RGVzY3JpYmUgdHUgcHJveWVjdG8gbyB0YXJlYTwvbGFiZWw+CiAgICAgICAg"
    "ICAgICAgICA8dGV4dGFyZWEKICAgICAgICAgICAgICAgICAgICBpZD0idXNlci1pbnB1dCIKICAg"
    "ICAgICAgICAgICAgICAgICByb3dzPSI0IgogICAgICAgICAgICAgICAgICAgIGNsYXNzPSJmbGV4"
    "IHctZnVsbCByb3VuZGVkLWxnIGJvcmRlciBib3JkZXItaW5wdXQgYmctYmFja2dyb3VuZCBweC0z"
    "IHB5LTIuNSB0ZXh0LXNtIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9ycyBwbGFjZWhvbGRlcjp0"
    "ZXh0LW11dGVkLWZvcmVncm91bmQgZm9jdXMtdmlzaWJsZTpvdXRsaW5lLW5vbmUgZm9jdXMtdmlz"
    "aWJsZTpyaW5nLTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJpbmcgcmVzaXplLW5vbmUiCiAgICAgICAg"
    "ICAgICAgICAgICAgcGxhY2Vob2xkZXI9IkVqZW1wbG86IENyZWFyIHVuYSBBUEkgUkVTVCBjb24g"
    "UHl0aG9uIHkgRmFzdEFQSSBwYXJhIGdlc3Rpb24gZGUgdGFyZWFzLCBjb24gYXV0ZW50aWNhY2lv"
    "biBKV1QgeSBiYXNlIGRlIGRhdG9zIFBvc3RncmVTUUwuLi4iCiAgICAgICAgICAgICAgICA+PC90"
    "ZXh0YXJlYT4KICAgICAgICAgICAgPC9kaXY+CgogICAgICAgICAgICA8ZGl2IGNsYXNzPSJncmlk"
    "IGdyaWQtY29scy0xIGdhcC00IHNtOmdyaWQtY29scy0yIj4KICAgICAgICAgICAgICAgIDxkaXY+"
    "CiAgICAgICAgICAgICAgICAgICAgPGxhYmVsIGZvcj0ibGFuZ3VhZ2Utc2VsZWN0IiBjbGFzcz0i"
    "bWItMiBibG9jayB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+TGVu"
    "Z3VhamUgKG9wY2lvbmFsKTwvbGFiZWw+CiAgICAgICAgICAgICAgICAgICAgPHNlbGVjdCBpZD0i"
    "bGFuZ3VhZ2Utc2VsZWN0IiBjbGFzcz0iZmxleCBoLTkgdy1mdWxsIHJvdW5kZWQtbGcgYm9yZGVy"
    "IGJvcmRlci1pbnB1dCBiZy1iYWNrZ3JvdW5kIHB4LTMgdGV4dC1zbSBzaGFkb3cteHMgdHJhbnNp"
    "dGlvbi1jb2xvcnMgZm9jdXMtdmlzaWJsZTpvdXRsaW5lLW5vbmUgZm9jdXMtdmlzaWJsZTpyaW5n"
    "LTIgZm9jdXMtdmlzaWJsZTpyaW5nLXJpbmciPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0"
    "aW9uIHZhbHVlPSIiPkF1dG8tZGV0ZWN0YXI8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAg"
    "ICAgPG9wdGlvbiB2YWx1ZT0iUHl0aG9uIj5QeXRob248L29wdGlvbj4KICAgICAgICAgICAgICAg"
    "ICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iVHlwZVNjcmlwdCI+VHlwZVNjcmlwdDwvb3B0aW9uPgog"
    "ICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJEYXJ0Ij5EYXJ0PC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkphdmFTY3JpcHQiPkphdmFT"
    "Y3JpcHQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iUnVz"
    "dCI+UnVzdDwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJH"
    "byI+R288L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iSmF2"
    "YSI+SmF2YTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJD"
    "IyI+QyM8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iUEhQ"
    "Ij5QSFA8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iUnVi"
    "eSI+UnVieTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJT"
    "d2lmdCI+U3dpZnQ8L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1"
    "ZT0iS290bGluIj5Lb3RsaW48L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICA8L3NlbGVjdD4K"
    "ICAgICAgICAgICAgICAgIDwvZGl2PgogICAgICAgICAgICAgICAgPGRpdj4KICAgICAgICAgICAg"
    "ICAgICAgICA8bGFiZWwgZm9yPSJmcmFtZXdvcmstc2VsZWN0IiBjbGFzcz0ibWItMiBibG9jayB0"
    "ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+RnJhbWV3b3JrIChvcGNp"
    "b25hbCk8L2xhYmVsPgogICAgICAgICAgICAgICAgICAgIDxzZWxlY3QgaWQ9ImZyYW1ld29yay1z"
    "ZWxlY3QiIGNsYXNzPSJmbGV4IGgtOSB3LWZ1bGwgcm91bmRlZC1sZyBib3JkZXIgYm9yZGVyLWlu"
    "cHV0IGJnLWJhY2tncm91bmQgcHgtMyB0ZXh0LXNtIHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9y"
    "cyBmb2N1cy12aXNpYmxlOm91dGxpbmUtbm9uZSBmb2N1cy12aXNpYmxlOnJpbmctMiBmb2N1cy12"
    "aXNpYmxlOnJpbmctcmluZyI+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9"
    "IiI+TmluZ3VubyAvIEF1dG88L29wdGlvbj4KICAgICAgICAgICAgICAgICAgICAgICAgPG9wdGlv"
    "biB2YWx1ZT0iRmFzdEFQSSI+RmFzdEFQSTwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAg"
    "ICA8b3B0aW9uIHZhbHVlPSJEamFuZ28iPkRqYW5nbzwvb3B0aW9uPgogICAgICAgICAgICAgICAg"
    "ICAgICAgICA8b3B0aW9uIHZhbHVlPSJGbHV0dGVyIj5GbHV0dGVyPC9vcHRpb24+CiAgICAgICAg"
    "ICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IkZsYXNrIj5GbGFzazwvb3B0aW9uPgogICAg"
    "ICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJOZXh0LmpzIj5OZXh0LmpzPC9vcHRp"
    "b24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJlYWN0Ij5SZWFjdDwv"
    "b3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJWdWUuanMiPlZ1"
    "ZS5qczwvb3B0aW9uPgogICAgICAgICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJFeHBy"
    "ZXNzIj5FeHByZXNzPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFs"
    "dWU9Ik5lc3RKUyI+TmVzdEpTPC9vcHRpb24+CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRp"
    "b24gdmFsdWU9IlNwcmluZyBCb290Ij5TcHJpbmcgQm9vdDwvb3B0aW9uPgogICAgICAgICAgICAg"
    "ICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJBY3RpeCI+QWN0aXg8L29wdGlvbj4KICAgICAgICAg"
    "ICAgICAgICAgICAgICAgPG9wdGlvbiB2YWx1ZT0iQXh1bSI+QXh1bTwvb3B0aW9uPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8b3B0aW9uIHZhbHVlPSJMYXJhdmVsIj5MYXJhdmVsPC9vcHRpb24+"
    "CiAgICAgICAgICAgICAgICAgICAgICAgIDxvcHRpb24gdmFsdWU9IlJhaWxzIj5SYWlsczwvb3B0"
    "aW9uPgogICAgICAgICAgICAgICAgICAgIDwvc2VsZWN0PgogICAgICAgICAgICAgICAgPC9kaXY+"
    "CiAgICAgICAgICAgIDwvZGl2PgoKICAgICAgICAgICAgPGJ1dHRvbgogICAgICAgICAgICAgICAg"
    "aWQ9ImdlbmVyYXRlLWJ0biIKICAgICAgICAgICAgICAgIGNsYXNzPSJpbmxpbmUtZmxleCB3LWZ1"
    "bGwgaXRlbXMtY2VudGVyIGp1c3RpZnktY2VudGVyIGdhcC0yIHJvdW5kZWQtbGcgYmctcHJpbWFy"
    "eSBweC00IHB5LTIuNSB0ZXh0LXNtIGZvbnQtbWVkaXVtIHRleHQtcHJpbWFyeS1mb3JlZ3JvdW5k"
    "IHNoYWRvdy14cyB0cmFuc2l0aW9uLWNvbG9ycyBob3ZlcjpiZy1wcmltYXJ5LzkwIGRpc2FibGVk"
    "OnBvaW50ZXItZXZlbnRzLW5vbmUgZGlzYWJsZWQ6b3BhY2l0eS01MCBjdXJzb3ItcG9pbnRlciIK"
    "ICAgICAgICAgICAgICAgIGRpc2FibGVkCiAgICAgICAgICAgID4KICAgICAgICAgICAgICAgIDxz"
    "cGFuIGlkPSJidG4tdGV4dCI+4pqhIEdlbmVyYXIgUHJvbXB0PC9zcGFuPgogICAgICAgICAgICAg"
    "ICAgPHNwYW4gaWQ9ImJ0bi1zcGlubmVyIiBjbGFzcz0iaGlkZGVuIj4KICAgICAgICAgICAgICAg"
    "ICAgICA8c3ZnIGNsYXNzPSJoLTQgdy00IGFuaW1hdGUtc3BpbiIgdmlld0JveD0iMCAwIDI0IDI0"
    "IiBmaWxsPSJub25lIj48Y2lyY2xlIGNsYXNzPSJvcGFjaXR5LTI1IiBjeD0iMTIiIGN5PSIxMiIg"
    "cj0iMTAiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjQiPjwvY2lyY2xlPjxw"
    "YXRoIGNsYXNzPSJvcGFjaXR5LTc1IiBmaWxsPSJjdXJyZW50Q29sb3IiIGQ9Ik00IDEyYTggOCAw"
    "IDAxOC04VjBDNS4zNzMgMCAwIDUuMzczIDAgMTJoNHoiPjwvcGF0aD48L3N2Zz4KICAgICAgICAg"
    "ICAgICAgIDwvc3Bhbj4KICAgICAgICAgICAgPC9idXR0b24+CgogICAgICAgIDwvc2VjdGlvbj4K"
    "CiAgICAgICAgPHNlY3Rpb24gaWQ9ImVycm9yLXNlY3Rpb24iIGNsYXNzPSJtdC02IGhpZGRlbiI+"
    "CiAgICAgICAgICAgIDxkaXYgY2xhc3M9InJvdW5kZWQtbGcgYm9yZGVyIGJvcmRlci1kZXN0cnVj"
    "dGl2ZS81MCBiZy1kZXN0cnVjdGl2ZS8xMCBwLTQgdGV4dC1zbSB0ZXh0LWRlc3RydWN0aXZlIj4K"
    "ICAgICAgICAgICAgICAgIDxwIGlkPSJlcnJvci1tZXNzYWdlIj48L3A+CiAgICAgICAgICAgIDwv"
    "ZGl2PgogICAgICAgIDwvc2VjdGlvbj4KCiAgICAgICAgPHNlY3Rpb24gaWQ9InJlc3VsdC1zZWN0"
    "aW9uIiBjbGFzcz0ibXQtOCBoaWRkZW4iPgogICAgICAgICAgICA8ZGl2IGNsYXNzPSJyb3VuZGVk"
    "LWxnIGJvcmRlciBib3JkZXItYm9yZGVyIGJnLWNhcmQgc2hhZG93LXNtIj4KICAgICAgICAgICAg"
    "ICAgIDxkaXYgY2xhc3M9ImZsZXggaXRlbXMtY2VudGVyIGp1c3RpZnktYmV0d2VlbiBib3JkZXIt"
    "YiBib3JkZXItYm9yZGVyIHB4LTQgcHktMyI+CiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFz"
    "cz0iZmxleCBpdGVtcy1jZW50ZXIgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAgICAgICA8c3Bh"
    "biBpZD0icmVzdWx0LWljb24iIGNsYXNzPSJ0ZXh0LWxnIj7wn5al77iPPC9zcGFuPgogICAgICAg"
    "ICAgICAgICAgICAgICAgICA8aDIgaWQ9InJlc3VsdC10aXRsZSIgY2xhc3M9InRleHQtc20gZm9u"
    "dC1zZW1pYm9sZCB0ZXh0LWNhcmQtZm9yZWdyb3VuZCI+U3lzdGVtIFByb21wdDwvaDI+CiAgICAg"
    "ICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzcz0iZmxl"
    "eCBpdGVtcy1jZW50ZXIgZ2FwLTIiPgogICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGlk"
    "PSJjb3B5LWJ0biIgY2xhc3M9ImlubGluZS1mbGV4IGl0ZW1zLWNlbnRlciBnYXAtMS41IHJvdW5k"
    "ZWQtbWQgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZCBweC0yLjUgcHktMS41IHRl"
    "eHQteHMgZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIHRyYW5zaXRpb24tY29sb3Jz"
    "IGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0LWFjY2VudC1mb3JlZ3JvdW5kIGN1cnNvci1wb2lu"
    "dGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIPCfk4sgQ29waWFyCiAgICAgICAgICAg"
    "ICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIGlk"
    "PSJyZWdlbmVyYXRlLWJ0biIgY2xhc3M9ImlubGluZS1mbGV4IGl0ZW1zLWNlbnRlciBnYXAtMS41"
    "IHJvdW5kZWQtbWQgYm9yZGVyIGJvcmRlci1ib3JkZXIgYmctYmFja2dyb3VuZCBweC0yLjUgcHkt"
    "MS41IHRleHQteHMgZm9udC1tZWRpdW0gdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIHRyYW5zaXRpb24t"
    "Y29sb3JzIGhvdmVyOmJnLWFjY2VudCBob3Zlcjp0ZXh0LWFjY2VudC1mb3JlZ3JvdW5kIGN1cnNv"
    "ci1wb2ludGVyIj4KICAgICAgICAgICAgICAgICAgICAgICAgICAgIPCflIQgUmVnZW5lcmFyCiAg"
    "ICAgICAgICAgICAgICAgICAgICAgIDwvYnV0dG9uPgogICAgICAgICAgICAgICAgICAgIDwvZGl2"
    "PgogICAgICAgICAgICAgICAgPC9kaXY+CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJwLTQi"
    "PgogICAgICAgICAgICAgICAgICAgIDxwcmUgaWQ9InJlc3VsdC1jb250ZW50IiBjbGFzcz0id2hp"
    "dGVzcGFjZS1wcmUtd3JhcCBicmVhay13b3JkcyBmb250LW1vbm8gdGV4dC1zbSBsZWFkaW5nLXJl"
    "bGF4ZWQgdGV4dC1jYXJkLWZvcmVncm91bmQiPjwvcHJlPgogICAgICAgICAgICAgICAgPC9kaXY+"
    "CiAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPSJib3JkZXItdCBib3JkZXItYm9yZGVyIHB4LTQg"
    "cHktMiI+CiAgICAgICAgICAgICAgICAgICAgPHAgaWQ9InJlc3VsdC10aW1lc3RhbXAiIGNsYXNz"
    "PSJ0ZXh0LXhzIHRleHQtbXV0ZWQtZm9yZWdyb3VuZCI+PC9wPgogICAgICAgICAgICAgICAgPC9k"
    "aXY+CiAgICAgICAgICAgIDwvZGl2PgogICAgICAgIDwvc2VjdGlvbj4KCiAgICA8L21haW4+Cgog"
    "ICAgPGZvb3RlciBjbGFzcz0iYm9yZGVyLXQgYm9yZGVyLWJvcmRlciBweS02IHRleHQtY2VudGVy"
    "IHRleHQteHMgdGV4dC1tdXRlZC1mb3JlZ3JvdW5kIj4KICAgICAgICA8cD5aUHJvbXB0ICZtZGFz"
    "aDsgR2VuZXJhZG9yIGRlIHByb21wdHMgZXN0cnVjdHVyYWRvcyBwYXJhIEdMTTwvcD4KICAgIDwv"
    "Zm9vdGVyPgoKICAgIDxzY3JpcHQgc3JjPSIvanMvYXBwLmpzIj48L3NjcmlwdD4KPC9ib2R5Pgo8"
    "L2h0bWw+Cg=="
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
