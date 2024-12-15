from locust import HttpUser, TaskSet, task


class ProfileBehavior(TaskSet):

    @task
    def test_edit_profile_page_get(self):
        """
        Prueba de carga para acceder a la página de edición de perfil.
        """
        response = self.client.get("/profile/edit")
        if response.status_code != 200:
            print(f"Failed to access profile edit page: {response.status_code}")
        elif b"Edit profile" not in response.content:
            print("Expected content not found on the profile edit page")

    @task
    def test_search_user_profiles(self):
        """
        Prueba de carga para la búsqueda de perfiles por nombre o apellido.
        """
        queries = ["Name", "Surname", "NonExistentName"]
        for query in queries:
            response = self.client.get(f"/profile/search?query={query}")
            if response.status_code != 200:
                print(f"Failed to search profiles with query '{query}': {response.status_code}")
            if query == "Name" and b"Name" not in response.content:
                print(f"Expected 'Name' in search results, but it was not found for query '{query}'")
            if query == "Surname" and b"Surname" not in response.content:
                print(f"Expected 'Surname' in search results, but it was not found for query '{query}'")
            if query == "NonExistentName" and b"No profiles found" not in response.content:
                print(f"Expected 'No profiles found' for query '{query}', but it was not found in response")

    @task
    def test_search_case_insensitivity(self):
        """
        Prueba de carga para verificar la insensibilidad a mayúsculas/minúsculas en la búsqueda.
        """
        queries = ["name", "surname", "NAME"]
        for query in queries:
            response = self.client.get(f"/profile/search?query={query}")
            if response.status_code != 200:
                print(f"Failed to search profiles with query '{query}': {response.status_code}")
            if b"Name" not in response.content:
                print(f"Expected 'Name' in search results for query '{query}', but it was not found")

    @task
    def test_search_empty_query(self):
        """
        Prueba de carga para la búsqueda con una consulta vacía.
        """
        response = self.client.get("/profile/search?query=")
        if response.status_code != 200:
            print(f"Failed to search profiles with an empty query: {response.status_code}")
        if b"No profiles found" not in response.content:
            print("Expected 'No profiles found' for an empty query, but it was not found in response")

    @task
    def test_search_single_character(self):
        """
        Prueba de carga para la búsqueda con una sola letra.
        """
        response = self.client.get("/profile/search?query=N")
        if response.status_code != 200:
            print(f"Failed to search profiles with single character query: {response.status_code}")
        if b"Name" not in response.content:
            print("Expected 'Name' in search results for query 'N', but it was not found")

    @task
    def test_search_with_extra_spaces(self):
        """
        Prueba de carga para la búsqueda con espacios adicionales.
        """
        response = self.client.get("/profile/search?query=  Name  ")
        if response.status_code != 200:
            print(f"Failed to search profiles with query containing extra spaces: {response.status_code}")
        if b"Name" not in response.content:
            print("Expected 'Name' in search results for query with extra spaces, but it was not found")

    @task
    def test_search_no_results(self):
        """
        Prueba de carga para la búsqueda que no devuelve resultados.
        """
        response = self.client.get("/profile/search?query=NonExistentName")
        if response.status_code != 200:
            print(f"Failed to search profiles with query 'NonExistentName': {response.status_code}")
        if b"No profiles found" not in response.content:
            print("Expected 'No profiles found' for query 'NonExistentName', but it was not found")


class UserBehavior(HttpUser):
    tasks = [ProfileBehavior]
    min_wait = 5000  # Tiempo mínimo entre tareas (5 segundos)
    max_wait = 9000  # Tiempo máximo entre tareas (9 segundos)
    host = "http://localhost:5000"  # URL base de la aplicación a probar
