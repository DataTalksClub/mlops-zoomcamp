import abc


class MetricImplementation:
    @abc.abstractmethod
    def calculate(self, context, data):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def supported_engines(cls):
        raise NotImplementedError()
