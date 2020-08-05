from django.contrib import admin

from django.urls import path
from django.conf.urls import include

from .rest import router, UserViewSet
from . import views as topical_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

	path('api/', include(router.urls)),
	path('api/me/', UserViewSet.as_view({ 'get': 'me' }), name = 'me'),
	path('api/search/', topical_views.search_products, name='search_products'),
	path('api/ingredient/fuzzy/<str:fuzzy>/', topical_views.fuzzy_name, name = 'fuzzy_name'),
	path('api/ingredient/<str:fuzzy_name>/tag/<str:tag_name>/', topical_views.tag_data, name = 'tag_data'),
	path('api/product/notfound/<str:upc>/', topical_views.product_404, name = 'product-404')
]
