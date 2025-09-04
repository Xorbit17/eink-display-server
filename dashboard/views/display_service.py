from django.http import HttpResponse, FileResponse, HttpResponseServerError, Http404, HttpRequest, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.utils import timezone
from dashboard.models.schedule import Display
from pathlib import Path
from dashboard.models.application import PrerenderedDashboard
from dashboard.models.schedule import WeeklyRule
from dashboard.constants import ModeKind
from dashboard.services.select_image import get_variant
from dashboard.services.display import create_new_display
from dashboard.services.render_page import render_png, run_eink_pipeline_for_page_in_memory
from pydantic import BaseModel, ValidationError, Field
from typing import Literal, Annotated, TypeAlias
from dataclasses import dataclass, asdict
import io


def _get_file_response(path: str | Path):
    normalisedPath = Path(path)
    if not normalisedPath.exists():
        return HttpResponse(status=404)
    response = FileResponse(open(normalisedPath, "rb"), content_type="image/png")
    response["Cache-Control"] = "no-store"

ResolutionDimension: TypeAlias = Annotated[int, Field(gt=0, lt=5000)] 

class BootstrapRequestBody(BaseModel):
    hardware_id: str
    horizontal_pixels: ResolutionDimension
    vertical_pixels: ResolutionDimension

@dataclass
class BootstrapResponseBody:
    human_readable_id: str
    token_key: str
    mode: ModeKind

class BootstrapController(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    def post(self, request):
        now=timezone.localtime()
        try:
            body = BootstrapRequestBody.model_validate(request.data)
        except ValidationError as e:
            return Response(
                {"detail": "Invalid JSON body", "errors": e.errors()},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if Display.objects.filter(hardware_id=body.hardware_id).exists():
            # Cannot bootstrap a known device more then once
            return Response(
                {"detail": "Display already provisioned. Authenticate to fetch/rotate token.", "code": "already_provisioned"},
                status=status.HTTP_409_CONFLICT,
            )
            
        display,user,token_key = create_new_display(
            host=request.get_host(),
            hardware_id=body.hardware_id,
            x_res=body.horizontal_pixels,
            y_res=body.vertical_pixels,
        )
        # Determine mode
        response = JsonResponse(asdict(BootstrapResponseBody(
            human_readable_id=display.human_readable_id,
            token_key=token_key,
            mode=WeeklyRule.resolve_mode(display,now=now), 
        )))
        return response

class ButtonRequestBody(BaseModel):
    button_pressed: Literal["A", "B", "C", "D"]

class DisplayButtonController(APIView):
    permission_classes = [IsAuthenticated]  # BasicAuth via DRF
    parser_classes = [JSONParser]  # ensure JSON only

    def post(self, request):
        display = request.user.display
        display.last_seen = timezone.now()
        display.save(update_fields=["last_seen"])

        try:
            body = ButtonRequestBody.model_validate(request.data)
        except ValidationError as e:
            return Response(
                {"detail": "Invalid JSON body", "errors": e.errors()},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pressed = body.button_pressed
        # TODO: Handle button press

        return Response({"ok": True, "button": pressed}, status=status.HTTP_200_OK)


class DisplayDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        display = request.user.display
        display.last_seen = now
        display.save(update_fields=["last_seen"])
        # Get latest pregenerated dashboad
        try:
            latest = PrerenderedDashboard.objects.latest("created_at")
            if not latest.path:
                raise RuntimeError("Generated dashboard record found but no associated image was generated.")
        except PrerenderedDashboard.DoesNotExist:
            return HttpResponseServerError("No dashboard records exist. Is the generation job running?")
        except RuntimeError as e:
            return HttpResponseServerError(str(e))
        out_path = Path(latest.path)

        response = _get_file_response(out_path)
        if not isinstance(response, FileResponse):
            return response
        # Response is an image
        response["Cache-Control"] = "no-store"
        return response
    
class DisplayVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        display = request.user.display
        display.last_seen = now
        display.save(update_fields=["last_seen"])
        try:
            variant = get_variant()
        except:
            return HttpResponseServerError("No variants have been generated. Is the variant creation job running and are source present?")
        if not variant.path:
            return HttpResponseServerError("Variant did not hava path; therefore its generation process failed. Check the variant generation job logs.")
        response = _get_file_response(variant.path)
        if not isinstance(response, FileResponse):
            return response
        # Response is an image
        response["Cache-Control"] = "no-store"
        return response
    
class DisplayBootScreenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        display = request.user.display
        display.last_seen = now
        display.save(update_fields=["last_seen"])
        png = render_png(f"http://localhost:8000/bootstrap?pk={display.pk}") # TODO remove hardcoded value. Relative URL
        buffer = io.BytesIO(png)
        buffer.seek(0)
        out_buffer = run_eink_pipeline_for_page_in_memory(buffer.getvalue())
        response = FileResponse(out_buffer,content_type="image/png")
        response["Cache-Control"] = "no-store"
        return response
        