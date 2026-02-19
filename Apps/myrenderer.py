from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler as drf_exception_handler


class MyRenderer(JSONRenderer):
    """
    Success responses -> wrap:
    {
      "msg": "<Model> created successfully",
      "data": ...,
      "status": 201
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        view = renderer_context.get("view")

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # errors ko yaha wrap nahi karte
        if getattr(response, "exception", False):
            return super().render(data, accepted_media_type, renderer_context)

        action = getattr(view, "action", "")

        # model name auto
        model_name = "Resource"
        try:
            qs = getattr(view, "queryset", None)
            model = qs.model if qs is not None else view.get_queryset().model
            model_name = model._meta.verbose_name.title()
        except Exception:
            pass

        msg_map = {
            "list": "fetched successfully",
            "retrieve": "retrieved successfully",
            "create": "created successfully",
            "update": "updated successfully",
            "partial_update": "updated successfully",
            "destroy": "deleted successfully",
        }
        suffix = msg_map.get(action, "processed successfully")

        wrapped = {
            "msg": f"{model_name} {suffix}",
            "data": None if action == "destroy" else data,
            "status": response.status_code,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)


def my_exception_handler(exc, context):
    """
    Standard error format:
    {
      "msg": "...",
      "errors": {...},
      "status": <http_status>
    }
    """
    response = drf_exception_handler(exc, context)

    # Unhandled / non-DRF exception
    if response is None:
        return Response(
            {
                "msg": "Server error",
                "errors": {"detail": "Something went wrong"},
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Pick a helpful message
    msg = "Error"

    # Common DRF case: {"detail": "..."}
    if isinstance(response.data, dict) and "detail" in response.data:
        msg = str(response.data["detail"])

    # Validation errors usually look like {"field": ["..."]}
    elif response.status_code == status.HTTP_400_BAD_REQUEST:
        msg = "Validation error"

    # Not found, auth, permission (optional nicer defaults)
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        msg = "Not found"
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        msg = "Authentication required"
    elif response.status_code == status.HTTP_403_FORBIDDEN:
        msg = "Permission denied"

    return Response(
        {
            "msg": msg,
            "errors": response.data,
            "status": response.status_code,
        },
        status=response.status_code,
    )
