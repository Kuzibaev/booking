def patch_data(data, model):
    _data = data.dict(exclude_unset=True)
    for key, value in _data.items():
        setattr(model, key, value)
