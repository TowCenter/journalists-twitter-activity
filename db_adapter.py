from contextlib import contextmanager

import sqlalchemy 
from sqlalchemy.orm import sessionmaker

import sys
import traceback

class DbAdapter:

	engine = None
	session = None
	dialect = ''
	driver = ''
	host = ''
	database = ''
	username = ''
	password = ''

	# always needs a username or password, else it'll go boom. 
	def __init__(self, dialect, driver, host, database, username, password):
		if not driver.strip():
			driver = ''
		else:
			driver = '+{}'.format(driver.strip())  # handle awkward syntax here, instead of relying on the client. 
											# perhaps it makes sense to have a case statement based on dialect? 
		try:
			self.dialect = dialect
			self.driver = driver
			self.host = host
			self.database = database
			self.username = username
			self.password = password
			if not dialect or not host or not database or not username or not password:
				raise Exception("Dialect, host, database, username, and password are all mandatory parameters.")
			self.engine = sqlalchemy.create_engine("{}{}://{}:{}@{}/{}". \
								format(dialect, driver, username, password, host, database))
		except Exception as e: 
			print('unable to initialise the db_adaptor')

	# possible todo: support multiple parallel database connections, and store instances in a dict. 

	# each request will (should) have its own session. 
	@contextmanager
	def session_scope(self):
		Session = sessionmaker(bind=self.engine)
		session = Session()
		try:
			yield session
			session.commit()
		except Exception as e:
			if type(e) == sqlalchemy.exc.OperationalError:
				self.engine = sqlalchemy.create_engine("{}{}://{}:{}@{}/{}". \
								format(self.dialect, self.driver, self.username, self.password, self.host, self.database)) 
			session.rollback()
			traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
			print('Caught exception while attempting to commit to session.')
		finally:
			session.close()
