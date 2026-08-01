from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RegistroUsuarioTests(TestCase):
    def setUp(self):
        self.url = reverse("usuarios:registro")

    def test_muestra_formulario_de_registro(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registrar usuario")

    def test_registra_usuario_con_datos_validos(self):
        response = self.client.post(
            self.url,
            {
                "username": "vendedor1",
                "first_name": "Dilan",
                "last_name": "Betancourt",
                "email": "dilan@example.com",
                "rol": Usuario.Rol.VENDEDOR,
                "password1": "ClaveSegura2026!",
                "password2": "ClaveSegura2026!",
            },
            follow=True,
        )

        self.assertRedirects(response, self.url)
        self.assertContains(response, "Usuario registrado correctamente.")
        usuario = Usuario.objects.get(username="vendedor1")
        self.assertEqual(usuario.rol, Usuario.Rol.VENDEDOR)
        self.assertTrue(usuario.check_password("ClaveSegura2026!"))

    def test_no_registra_usuario_con_contrasenas_distintas(self):
        response = self.client.post(
            self.url,
            {
                "username": "vendedor1",
                "email": "dilan@example.com",
                "rol": Usuario.Rol.VENDEDOR,
                "password1": "ClaveSegura2026!",
                "password2": "OtraClave2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(username="vendedor1").exists())


class AutenticacionTests(TestCase):
    def setUp(self):
        self.password = "ClaveSegura2026!"
        self.usuario = Usuario.objects.create_user(
            username="dilan",
            password=self.password,
            rol=Usuario.Rol.VENDEDOR,
        )

    def test_inicio_requiere_autenticacion(self):
        response = self.client.get(reverse("usuarios:inicio"))

        self.assertRedirects(
            response,
            f'{reverse("usuarios:login")}?next={reverse("usuarios:inicio")}',
        )

    def test_usuario_puede_iniciar_sesion(self):
        response = self.client.post(
            reverse("usuarios:login"),
            {"username": self.usuario.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("usuarios:inicio"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.usuario.pk)

    def test_usuario_puede_cerrar_sesion(self):
        self.client.force_login(self.usuario)

        response = self.client.post(reverse("usuarios:logout"))

        self.assertRedirects(response, reverse("usuarios:login"))
        self.assertNotIn("_auth_user_id", self.client.session)
