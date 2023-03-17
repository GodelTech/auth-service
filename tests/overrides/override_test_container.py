import platform
from testcontainers.postgres import PostgresContainer
from typing import Any

class CustomPostgresContainer(PostgresContainer):
    def get_connection_url(self, host: Any = None) -> Any:
        connection_url = super().get_connection_url(host=host)
        
        if platform.system() == "Windows":
            connection_url = connection_url.replace('localnpipe', 'localhost')
        
        return connection_url 
