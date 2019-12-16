from python_json_config import ConfigBuilder

# create config_util parser
builder = ConfigBuilder()
builder.set_field_access_required()
# parse config_util
config = builder.parse_config('config.json')
