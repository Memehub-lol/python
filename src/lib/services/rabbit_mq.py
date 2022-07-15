from src.lib.environment import Environment


class RabbitMQ:
    protocol = "pyamqp"
    host = "rabbitmq" if Environment.is_docker else "127.0.0.1"
    port = 5672

    @classmethod
    def url(cls):
        return f"{cls.protocol}://{cls.host}:{cls.port}/"
