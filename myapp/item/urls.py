from django.urls import path
from .views      import PreProcessing, itemList, itemDetail, GetSkinType

urlpatterns = [
    path('data', PreProcessing.as_view()),
    path('skin-type', GetSkinType.as_view()),
    path('products', itemList.as_view()),
    path('products/<int:id>?<str:skin_type>', itemDetail.as_view()),
]
