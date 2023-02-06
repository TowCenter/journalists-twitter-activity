import configparser
import os
import sys

class Config:
	
	def __init__(self, env, root_directory):
		self.config = self.load_config(env, root_directory)

	def get_property(self, object, property, fallback=None):
		return self.config.get(object, property, fallback=fallback)

	def load_config(self, env, config_directory):
		# Load config file based on environment.
		absolute_config_file_name = os.path.join(config_directory, env + ".cfg")
		# Check if file exists; if not, throw error and exit.
		if not os.path.isfile(absolute_config_file_name):
			print("Error: {0} doesn't exist".format(absolute_config_file_name))
			sys.exit(1)
		# Now, read the config file.
		config = configparser.ConfigParser()
		config.read(absolute_config_file_name)
		return config
