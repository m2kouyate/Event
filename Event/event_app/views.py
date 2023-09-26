from django.db import transaction
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from rest_framework.exceptions import PermissionDenied
from rest_framework.renderers import JSONRenderer

from .models import Event
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponseRedirect

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def check_creator(self, instance):
        if self.request.user != instance.creator:
            raise PermissionDenied("You don't have permission to modify this event.")

    def perform_destroy(self, instance):
        self.check_creator(instance)
        instance.delete()

    def perform_update(self, serializer):
        self.check_creator(self.get_object())
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"error": None, "result": serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer_class()(event, context={'request': request})
        return Response({"error": None, "result": serializer.data}, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        event = self.get_object()
        if request.user == event.creator:
            return Response({"error": None, "result": {'status': 'You are the creator of the event'}}, status=status.HTTP_200_OK)

        if request.user in event.participants.all():
            return Response({"error": None, "result": {'status': 'Already joined'}}, status=status.HTTP_200_OK)
        event.participants.add(request.user)
        return Response({"error": None, "result": {'status': 'Joined'}}, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def unjoin(self, request, pk=None):
        event = self.get_object()
        if request.user not in event.participants.all():
            return Response({"error": None, "result": {'status': 'You are not a participant'}}, status=status.HTTP_200_OK)
        event.participants.remove(request.user)
        return Response({"error": None, "result": {'status': 'Unjoined'}}, status=status.HTTP_200_OK)


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    ordering = ['-date_created']


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_creator'] = self.request.user == self.object.creator
        return context


@method_decorator(login_required, name='dispatch')
class EventCreateView(CreateView):
    model = Event
    fields = ['title', 'text']
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('event_app:events')


@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    fields = ['title', 'text']
    template_name = 'events/event_form.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.creator != self.request.user:
            raise Http404("You are not allowed to edit this Event")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('event_app:event_detail', args=[str(self.object.id)])


@method_decorator(login_required, name='dispatch')
class EventDeleteView(DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_app:events')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.creator != self.request.user:
            raise Http404("You are not allowed to delete this Event")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class JoinEventView(View):
    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)

        event.participants.add(request.user)

        return HttpResponseRedirect(reverse('event_app:event_detail', args=[event_id]))


@method_decorator(login_required, name='dispatch')
class UnjoinEventView(View):
    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)

        event.participants.remove(request.user)

        return HttpResponseRedirect(reverse('event_app:event_detail', args=[event_id]))



