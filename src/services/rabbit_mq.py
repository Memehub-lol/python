


class RabbitMQ:
    protocol = "pyamqp"
    host = "rabbitmq"
    port = 5672

    @classmethod
    def url(cls):
        return f"{cls.protocol}://{cls.host}:{cls.port}/"
