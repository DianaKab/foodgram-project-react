from rest_framework import viewsets, mixins


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet
                          ):
    pass
