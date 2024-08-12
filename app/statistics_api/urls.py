from django.urls import path
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=OpenAPISchemaGenerator,
)


app_name = "statistics_api"
urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # path('helloht/', views.HelloView.as_view(), name='hello-view'),
    path("polls", views.AllPollsView.as_view(), name="polls"),
    path("novelties", views.AllNoveltiesView.as_view(), name="novelties"),
    path("polls/<int:poll_id>/", views.PollDetail.as_view(), name="poll_detail"),
    path("novelties/<int:novelty_id>/", views.NoveltyDetail.as_view(), name="novelty_detail"),
    path("me/", views.RequestsLeft.as_view(), name="me"),
]
