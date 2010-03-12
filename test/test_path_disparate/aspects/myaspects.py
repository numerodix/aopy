def decorator(func):
    def new_func(*args, **kw):
        print("Decorator")
        return func(*args, **kw)
    return new_func
