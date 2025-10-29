from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Usuario

class UsuarioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='testuser',
            cpf='12345678901',
            telefone='(11) 99999-9999',
            email='test@example.com',
            password='testpass123'
        )

    def test_usuario_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.cpf, '12345678901')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_usuario_str(self):
        self.assertEqual(str(self.user), 'testuser')

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            cpf='12345678901',
            telefone='(11) 99999-9999',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('pedido:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_valid(self):
        response = self.client.post(reverse('pedido:login'), {
            'id': '12345678901',  # cpf
            'senha': 'testpass123'
        })
        self.assertRedirects(response, reverse('pedido:selecionar_tamanho'))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('pedido:login'), {
            'id': 'invalid',
            'senha': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Usuário ou senha inválidos.')

    def test_cadastro_view_get(self):
        response = self.client.get(reverse('pedido:cadastrar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro.html')

    def test_selecionar_tamanho_view_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('pedido:selecionar_tamanho'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedido/tamanho.html')
