from django.conf import settings
from django.shortcuts import render

from django.conf import settings
from django.http import JsonResponse


class MaintenanceModeMiddleware:
    """
    Maintenance middleware:
    - Admin URLs bypass
    - Static URLs bypass
    - Superusers bypass
    - APIs / normal pages JSON 503
    Works for both DEBUG True and False.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_paths = ["/admin/", "/static/", "/media/"]
        if settings.DEBUG:
            self.excluded_paths.append("/__debug__/")

    def __call__(self, request):
        path = request.path_info or "/"

        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return self.get_response(request)

        #  Superuser bypass
        user = getattr(request, "user", None)
        if (
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "is_superuser", False)
        ):
            return self.get_response(request)

        #  Maintenance mode
        if getattr(settings, "MAINTENANCE_MODE", False):

            return JsonResponse(
                {
                    "error": "The site is currently under maintenance. Please try again later.",
                    "status": 503,
                    "headers": {"Retry-After": "3600"},
                },
                status=503,
                headers={"Retry-After": "3600"},
            )

        return self.get_response(request)


# from django.http import JsonResponse
# from django.urls import resolve, Resolver404


# class HandleInvalidURLMiddleware:
#     """
#     Middleware to return a custom JSON message for invalid URLs.
#     """

#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         try:

#             # print(request.path)

#             resolve(request.path_info)

#         except Resolver404:

#             return JsonResponse(
#                 {
#                     "error": "Invalid URL. Please check your endpoint pls try to match realted to  /api , or /api/v1/.",
#                     "status": 404,
#                 },
#                 status=404,
#             )

#         response = self.get_response(request)
#         return response


# -------------------------- Others for templates  -------------

# env_flag = getattr(settings, "MAINTENANCE_MODE", False)
# db_flag = False
# try:
#     maintenance = Maintenance.objects.first()
#     db_flag = maintenance.is_active if maintenance else False
# except Exception:
#     # DB not ready (migrations)
#     db_flag = False

# if env_flag or db_flag:
#     # Always render HTML template
#     response = render(request, "maintenance/maintenance.html", status=503)
#     response["Retry-After"] = "3600"
#     return response
