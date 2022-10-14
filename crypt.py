# https://github.com/pyca/bcrypt
import bcrypt

# password manager class
class PassMan:

	# this function assumes the given password is under 72 characters to fit bcrypt's limit
	def hash(rawPassword: bytes):
		return bcrypt.hashpw(rawPassword, bcrypt.gensalt())

	def check(submittedPassword: bytes, storedHash: bytes):
		return bcrypt.checkpw(submittedPassword, storedHash)