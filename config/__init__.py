import tomlkit, os

config_path = os.path.abspath(__file__).replace('__init__.py','')

def config(key:str):
    if key not in ["qweather_api_key"]:
        with open(os.path.join(config_path,'config.toml')) as f:
            _config = tomlkit.parse(f.read())
        return _config[key]
    match key:
        case "qweather_api_key":
            with open(os.path.join(config_path,'ed25519-private.pem')) as f:
                _config = f.read()
            return _config
        case _:
            raise ValueError(f"Invalid config key: {key}")