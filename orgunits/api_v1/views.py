"""
Copyright 2020 ООО «Верме»
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from orgunits.api_v1.serializers import OrganizationSerializer
from orgunits.models import Organization
from wfm.views import TokenAuthMixin


class OrganizationViewSet(TokenAuthMixin, ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    @action(methods=["GET"], detail=True)
    def parents(self, request, *args, **kwargs):
        """
        Возвращает родителей запрашиваемой организации
        TODO: Написать два действия для ViewSet (parents и children), используя методы модели
        """
        id = kwargs["pk"]
        root = Organization.objects.get(id=id)
        parents = root.parents()
        json_parent = [OrganizationSerializer(parent).data for parent in parents]
        return Response(json_parent)

    @action(methods=["GET"], detail=True)
    def children(self, request, *args, **kwargs):
        id = kwargs["pk"]
        root = Organization.objects.get(id=id)
        children = root.children()
        json_child = [OrganizationSerializer(child).data for child in children]
        return Response(json_child)

