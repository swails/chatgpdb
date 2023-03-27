from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<pdb_id>\w+)/$", consumers.PDBConsumer.as_asgi()),
]