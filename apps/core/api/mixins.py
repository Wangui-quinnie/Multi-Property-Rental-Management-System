class CurrentUserMixin:
    """
    Nicknames `request.user` as `self.user` on any view that
    inherits this. Purely a convenience — no behavior change.
    """
    @property
    def user(self):
        return self.request.user