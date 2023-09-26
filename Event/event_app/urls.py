from django.urls import path

from .views import EventListView, EventCreateView, EventUpdateView, EventDeleteView, JoinEventView, UnjoinEventView, \
    EventDetailView

urlpatterns = [
    path('', EventListView.as_view(), name='events'),
    path('events/create/', EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/update/', EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
    path('events/<int:event_id>/join/', JoinEventView.as_view(), name='join_event'),
    path('events/<int:event_id>/unjoin/', UnjoinEventView.as_view(), name='unjoin_event'),
]
