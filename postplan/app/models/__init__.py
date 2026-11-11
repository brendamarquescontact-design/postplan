class ValidationError(Exception):
    """Erro de validação com mensagens por campo: {'campo': 'mensagem'}."""

    def __init__(self, errors):
        super().__init__(str(errors))
        self.errors = errors
