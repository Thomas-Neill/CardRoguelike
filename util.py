import copy
#assumes dicts are filled with lists
#to properly merge overlapping keys, we add the lists together.
def mergeDicts(ds):
    final = {}
    for d in ds:
        for key in d:
            if key not in final:
                final[key] = []
            final[key] += d[key]
    return final
