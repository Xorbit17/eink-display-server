from django.shortcuts import render
from django.views import View
from dashboard.services.select_image import get_variant
from django.http import FileResponse, Http404
import os
import mimetypes

class PhotoView(View):

    def get(self, request):
        """
        Returns one image (as raw bytes) chosen by final score.
        """
        try:
            chosen = get_variant()
        except Exception:
            raise Http404("Failed to select an image.")

        path = chosen.path
        if not path or not os.path.exists(path):
            raise Http404("Image file not found on disk.")

        ctype, _ = mimetypes.guess_type(path)
        ctype = ctype or "application/octet-stream"

        resp = FileResponse(open(path, "rb"), content_type=ctype)
        # Dynamic content; avoid caching on the client/display unless you want it
        resp["Cache-Control"] = "no-store"
        return resp
