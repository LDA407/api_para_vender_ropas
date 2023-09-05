from rest_framework import permissions
# from django.http import HttpResponseForbidden
from permissions import IsStaffEditorPermission

class StaffEditorPermission():
    permissions_clases = [
        permissions.IsAuthenticated,
        IsStaffEditorPermission,
        permissions.IsAdminUser
    ]


# class HttpsOnlyMixin:
#     def dispatch(self, request, *args, **kwargs):
#         if not request.is_secure():
#             return HttpResponseForbidden("Error! This page can only be accessed using HTTPS.")

#         if 'HTTP_X_FORWARDED_PROTO' in request.META and request.META['HTTP_X_FORWARDED_PROTO'] == 'https':
#             request.is_secure = lambda: True

#         if not request.is_secure():
#             return not_suported_response("Insecure request. Please upgrade to HTTPS")

#         return super().dispatch(request, *args, **kwargs)
