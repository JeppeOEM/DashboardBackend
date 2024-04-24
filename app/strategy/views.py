"""
Views for the recipe APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from core.models import Recipe
from strategy import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # serializer_class = serializers.StrategySerializer
    serializer_class = serializers.StrategyDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    #overwriting get_querset method
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    #get_serializer_class
    #Returns the class that should be used for the serializer.
    #https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself

    #Is a method ViewSet class from rest_framework, and it being overwritten to return a regular strategy instance
    #Instead of a detailed one
    def get_serializer_class(self):
        """Return the serializer class for request."""

        #self.action = "list" refers to a specific action or method within a ViewSet or APIView class.
        if self.action == 'list':
            #dont call the constructor of the class so NO () in the end, just a refrence to the class that rest_framework
            #can instanciate and use it the ViewSet
            return serializers.StrategySerializer

        return self.serializer_class
    #Overwriting methods from View Class
    #https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    #When we call create on the ViewSet, we can call this method as part of the creation of that new object
    #The Validation Serializer is passed so we are Authenticated and are allowed to create new objects
    def perform_create(self, serializer):
        """Create a new recipe."""

        serializer.save(user=self.request.user)