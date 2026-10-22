def smart_update(old, new):
    changed = False
    for k in old:
        v = new.get(k)
        if isinstance(v, dict):
            changed |= smart_update(old[k], v)
        elif v is not None:
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            changed |= old[k] != v
            old[k] = v
    return changed
