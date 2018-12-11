from django.shortcuts import render

# Create your views here.
from rest_framework import generics , mixins
from rest_framework import status , permissions
from .models import Photos
from .serializers import PhotoSerializer

class ListPhotoView(generics.ListAPIView, mixins.CreateModelMixin,generics.GenericAPIView):
    queryset = Photos.objects.all()
    serializer_class = PhotoSerializer



    def get(self, request, *args, **kwargs):
        return self.list(request, *args ,**kwargs)


    def post(self,request, *args, **kwargs):
        return self.create(request,*args,**kwargs)

#
# class ProductViewSet(BaseViewSet, viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#
#     @detail_route(methods=['post'])
#     def upload_docs(request):
#         try:
#             file = request.data['file']
#         except KeyError:
#             raise ParseError('Request has no resource file attached')
#         product = Product.objects.create(image=file, ....)