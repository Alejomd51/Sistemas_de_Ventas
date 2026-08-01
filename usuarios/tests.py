from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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


class RestriccionPorRolTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="administrador",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.ADMIN,
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor",
            password="ClaveSegura2026!",
            rol=Usuario.Rol.VENDEDOR,
        )

    def test_usuario_anonimo_es_enviado_al_login(self):
        url = reverse("usuarios:panel_admin")

        response = self.client.get(url)

        self.assertRedirects(response, f'{reverse("usuarios:login")}?next={url}')

    def test_admin_puede_acceder_a_su_panel(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("usuarios:panel_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel de administrador")

    def test_vendedor_no_puede_acceder_al_panel_admin(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("usuarios:panel_admin"))

        self.assertEqual(response.status_code, 403)

    def test_vendedor_puede_acceder_a_su_panel(self):
        self.client.force_login(self.vendedor)

        response = self.client.get(reverse("usuarios:panel_vendedor"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel de vendedor")

    def test_admin_no_puede_acceder_al_panel_vendedor(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("usuarios:panel_vendedor"))

        self.assertEqual(response.status_code, 403)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class RecuperacionContrasenaTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="dilan",
            email="dilan@example.com",
            password="ClaveAnterior2026!",
            rol=Usuario.Rol.VENDEDOR,
        )

    def test_envia_correo_de_recuperacion(self):
        response = self.client.post(
            reverse("usuarios:password_reset"),
            {"email": self.usuario.email},
        )

        self.assertRedirects(response, reverse("usuarios:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Recuperación de contraseña", mail.outbox[0].subject)
        self.assertIn("/usuarios/restablecer/", mail.outbox[0].body)

    def test_token_valido_permite_cambiar_contrasena(self):
        uid = urlsafe_base64_encode(force_bytes(self.usuario.pk))
        token = default_token_generator.make_token(self.usuario)
        url = reverse(
            "usuarios:password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            response.url,
            {
                "new_password1": "ClaveNueva2026!",
                "new_password2": "ClaveNueva2026!",
            },
        )

        self.assertRedirects(response, reverse("usuarios:password_reset_complete"))
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password("ClaveNueva2026!"))
