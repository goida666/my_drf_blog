from rest_framework import viewsets, permissions, pagination, generics, filters
from .serializers import PostSerializer, TagSerializer, ContactSerializer, RegisterSerializer, UserSerializer, CommentSerializer
from .models import Post, Comment
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.core.mail import send_mail
from taggit.models import Tag
from django.views.generic import TemplateView

class PageNumberSetPagination(pagination.PageNumberPagination):  # pagination.PageNumberPagination - класс, дающий возможность пагинации
    page_size = 6
    page_query_param = 'page_size'    # позволяет клиентам переопределить page_size (например 10)
    ordering = 'created_at'   # обьекты отображаются в порядке их создания


class PostViewSet(viewsets.ModelViewSet):    # Определение класса PostViewSet, который является подклассом ModelViewSet из Django REST framework. ModelViewSet предоставляет стандартные CRUD операции (Create, Retrieve, Update, Delete) для модели
    search_fields = ['content', 'h1']
    filter_backends = (filters.SearchFilter,) 
    serializer_class = PostSerializer       # указывает чтоэтот класс будет использовать serializer для (де)сериализации данных
    queryset = Post.objects.all()            # класс будет использовать все обьекты из модели Post
    lookup_field = 'slug'                    #  поле slug будет использоваться для поиска объектов модели Post
    permission_classes = [permissions.AllowAny]   # любой пользователь (аутентифицированный или нет) может просматривать, создавать, обновлять и удалять объекты модели Post
    pagination_class = PageNumberSetPagination   # добавляет возможность управления размером страницы (количеством элементов на странице)


class TagDetailView(generics.ListAPIView):           # список постов по тегу
    serializer_class = PostSerializer
    pagination_class = PageNumberSetPagination   # ссылка на класс PNSP, чтобы контролить вывод данных на странице
    permission_classes = [permissions.AllowAny]  


    def get_queryset(self):                         # функция, определяющая какие данные будут возвращены при обрботке запроса
        tag_slug = self.kwargs['tag_slug'].lower()  # переменная (тут часть url), по ней можно искать записи по тегам
        tag = Tag.objects.get(slug=tag_slug)        # получаем все теги из БД
        return Post.objects.filter(tags=tag)        # возвращает обьекты Post c cовпавшими тегами


class TagView(generics.ListAPIView):      # список тегов
    queryset = Tag.objects.all()            # передаем все теги
    serializer_class = TagSerializer         # использует TagSerializer, для (де)сериализации данных
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):             # класс представления для последних 5 записей
    queryset = Post.objects.all().order_by('-id')[:5]  # возвращает последние 5 записей
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class FeedBackView(generics.ListAPIView):           # класс представления обратной связи
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerializer(data=request.data)   
        if serializer_class.is_valid:
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(f'От {name} | {subject}', message, from_email, ['sanyalohhhh1337@gmail.com'])
            return Response({"success": "Sent"})

class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Пользователь успешно создан",
        })

class ProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request, *args,  **kwargs):
        return Response({
            "user": UserSerializer(request.user, context=self.get_serializer_context()).data,
        })

class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_slug = self.kwargs['post_slug'].lower()
        post = Post.objects.get(slug=post_slug)
        return Comment.objects.filter(post=post)


        
