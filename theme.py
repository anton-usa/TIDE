import configparser;
from directory import DIRECTORY;

def get(section=None, key=None):
	config = configparser.ConfigParser();
	config.read(DIRECTORY+"/config/themes.ini");
	
	if section and key:
		return config[section][key];
	elif section:
		return config[section];
	else:
		return config;

def set(section, key, value):
	config = configparser.ConfigParser();
	config.read(DIRECTORY+"/config/themes.ini");
	
	config[section][key] = value;
	
	with open(DIRECTORY+"/config/themes.ini", "w") as f:
		config.write(f);

def delete(section):
	config = configparser.ConfigParser();
	config.read(DIRECTORY+"/config/themes.ini");
	del config[section];
	
	with open(DIRECTORY+"/config/themes.ini", "w") as f:
		config.write(f);

if __name__ == "__main__":
	print(get("Classic", "linenumbers"));
