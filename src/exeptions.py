class TaskValidationError(Exception):
    pass


class InvalidStatusError(TaskValidationError):
    pass


class InvalidPriorityError(TaskValidationError):
    pass


class InvalidTaskIdError(TaskValidationError):
    pass


class InvalidDescriptionError(TaskValidationError):
    pass