import configparser;
from directory import DIRECTORY;

def get(section, key):
	config = configparser.ConfigParser();
	config.read(DIRECTORY+"/config/config.ini");

	return config[section][key];

def set(section, key, value):
	config = configparser.ConfigParser();
	config.read(DIRECTORY+"/config/config.ini");
	
	config[section][key] = value;
	
	with open(DIRECTORY+"/config/config.ini", "w") as f:
		config.write(f);
	
if __name__ == "__main__":
	print(get("view", "side"));
