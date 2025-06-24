def device_definition(device: dict) -> dict:
    input_string = device["def"]
    parts = input_string.split()

    result = {
        "name": parts[0],
        "qtd": int(parts[1]),
        "type": parts[2]
    }

    return result


def link_definition(link: dict) -> dict:
    input_string = link["def"]
    parts = input_string.split()

    result = {
        "d1": parts[0],
        "d2": parts[1],
        "type": parts[2]
    }

    return result