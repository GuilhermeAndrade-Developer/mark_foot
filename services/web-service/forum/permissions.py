from rest_framework import permissions
from django.contrib.auth.models import User


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada que permite apenas aos autores
    editar seus próprios posts/tópicos.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura para qualquer request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissões de escrita apenas para o autor
        return obj.author == request.user


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Permissão para moderadores poderem editar/deletar
    qualquer conteúdo do fórum.
    """
    
    def has_permission(self, request, view):
        # Permissões de leitura para qualquer request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Verificar se é staff ou superuser
        return request.user and (request.user.is_staff or request.user.is_superuser)


class CanVotePermission(permissions.BasePermission):
    """
    Permissão para votação em posts.
    Usuários não podem votar nos próprios posts.
    """
    
    def has_object_permission(self, request, view, obj):
        # Apenas usuários autenticados podem votar
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Não pode votar no próprio post
        if hasattr(obj, 'author') and obj.author == request.user:
            return False
        
        return True


class CanCreateTopicPermission(permissions.BasePermission):
    """
    Permissão para criação de tópicos.
    Pode incluir verificações adicionais como reputação mínima.
    """
    
    def has_permission(self, request, view):
        # Usuário deve estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar se o usuário não está banido (implementação futura)
        # if hasattr(request.user, 'forum_profile') and request.user.forum_profile.is_banned:
        #     return False
        
        # Por enquanto, todos os usuários autenticados podem criar tópicos
        return True


class CanPostReplyPermission(permissions.BasePermission):
    """
    Permissão para responder em tópicos.
    Verifica se o tópico não está fechado ou bloqueado.
    """
    
    def has_permission(self, request, view):
        # Usuário deve estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Se estiver criando um post, verificar o tópico
        if request.method == 'POST' and 'topic' in request.data:
            from .models import ForumTopic
            
            try:
                topic_id = request.data['topic']
                topic = ForumTopic.objects.get(id=topic_id)
                
                # Verificar se o tópico está aberto
                if topic.status in ['closed', 'locked']:
                    return False
                
            except ForumTopic.DoesNotExist:
                return False
        
        return True


class CategoryModerationPermission(permissions.BasePermission):
    """
    Permissão para moderação de categorias específicas.
    """
    
    def has_object_permission(self, request, view, obj):
        # Staff sempre tem permissão
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Verificar se é moderador da categoria (implementação futura)
        # if hasattr(obj, 'moderators') and request.user in obj.moderators.all():
        #     return True
        
        return False


class ForumAdminPermission(permissions.BasePermission):
    """
    Permissão para administração geral do fórum.
    """
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and
                (request.user.is_staff or request.user.is_superuser))


class ReputationBasedPermission(permissions.BasePermission):
    """
    Permissão baseada na reputação do usuário.
    Diferentes ações requerem diferentes níveis de reputação.
    """
    
    REQUIRED_REPUTATION = {
        'create_topic': 0,      # Qualquer usuário pode criar tópicos
        'vote': 15,             # Precisa de 15 pontos para votar
        'edit_others': 100,     # Precisa de 100 pontos para editar posts de outros
        'moderate': 500,        # Precisa de 500 pontos para moderação
    }
    
    def __init__(self, required_action='create_topic'):
        self.required_action = required_action
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Staff sempre tem permissão
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Verificar reputação
        try:
            profile = request.user.forum_profile
            required_rep = self.REQUIRED_REPUTATION.get(self.required_action, 0)
            return profile.reputation_score >= required_rep
        except:
            # Se não tem perfil, assumir reputação 0
            return self.REQUIRED_REPUTATION.get(self.required_action, 0) == 0


class ThrottleVotingPermission(permissions.BasePermission):
    """
    Permissão para limitar votação excessiva.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Implementar throttling baseado em tempo (implementação futura)
        # Por exemplo, máximo 100 votos por hora
        
        return True


class AntiSpamPermission(permissions.BasePermission):
    """
    Permissão para prevenir spam.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Staff não tem limitações
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Implementar verificações anti-spam (implementação futura)
        # - Limite de posts por minuto
        # - Verificação de conteúdo duplicado
        # - Análise de padrões suspeitos
        
        return True


# Mixins de permissões para usar nas ViewSets

class ForumBasePermissionMixin:
    """
    Mixin base com permissões comuns do fórum.
    """
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, CanCreateTopicPermission]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthorOrReadOnly]
        elif self.action == 'vote':
            permission_classes = [CanVotePermission]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        
        return [permission() for permission in permission_classes]


class TopicPermissionMixin(ForumBasePermissionMixin):
    """
    Mixin específico para permissões de tópicos.
    """
    
    def get_permissions(self):
        if self.action in ['close', 'pin']:
            permission_classes = [IsAuthorOrReadOnly | IsModeratorOrReadOnly]
        else:
            return super().get_permissions()
        
        return [permission() for permission in permission_classes]


class PostPermissionMixin(ForumBasePermissionMixin):
    """
    Mixin específico para permissões de posts.
    """
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, CanPostReplyPermission]
        elif self.action == 'report':
            permission_classes = [permissions.IsAuthenticated]
        else:
            return super().get_permissions()
        
        return [permission() for permission in permission_classes]
