"""
URL configuration for Backends project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from Apps.views import Invalid_Url

urlpatterns = [
    path("admin/", admin.site.urls),
]
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from Apps.views import home, stats

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Auth (DRF)
    # path("api-auth/", include("rest_framework.urls")),
    # Common / public
    path("silk/", include("silk.urls", namespace="silk")),
    path("", home, name="home"),
    path("status/", stats, name="status"),
    # ---------------- API v1 ----------------
    path("api/v1/", include("Apps.urls")),  # common / shared APIs
    path("api/v1/authors/", include("AuthorApp.urls")),
    path("api/v1/books/", include(("BookApp.urls"), namespace="books")),
    path("api/v1/category/", include("CategoryApp.urls")),
    path("api/v1/cart/", include("CartApp.urls")),
    path("api/v1/cartitem/", include("Cartitem.urls")),
    path("api/v1/users/", include("UserApp.urls")),
    path("orders/", include("OrderApp.urls")),
]


handler404 = "Apps.views.Invalid_Url"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
