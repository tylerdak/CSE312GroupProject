# https://github.com/pyca/bcrypt
from dataclasses import dataclass
from typing import Tuple
import bcrypt
import secrets
import string
import hashlib
from dbstuff import *

# password manager class
class PassMan:

	# this function assumes the given password is under 72 characters to fit bcrypt's limit
	def hash(rawPassword: bytes):
		return bcrypt.hashpw(rawPassword, bcrypt.gensalt())

	def check(submittedPassword: bytes, storedHash: bytes):
		return bcrypt.checkpw(submittedPassword, storedHash)

# This class is designed to be a shell class 
# It only holds two poro
@dataclass
class AuthTokenPair:
	raw: bytes
	hashed: bytes

class AuthToken:
	# creates a new authtoken
	# made with letters, numbers, and urlsafe characters
	# length is currently 64 which, with just letters and numbers,
	# would be 381 bits of entropy!!!
	# we're aiming for 80, so this is great!
	@staticmethod
	def new() -> bytes:
		tokenLength = 64
		rawToken = secrets.token_urlsafe(tokenLength)
		return rawToken.encode("ascii")
	
	# hashes a given bytestring (theoretically a raw authtoken)
	@staticmethod
	def hashed(raw: bytes) -> str:
		return hashlib.sha256(raw).hexdigest()

	# create and hash a new auth token
	# returned as an AuthTokenPair for readability
	@staticmethod
	def newSet() -> AuthTokenPair:
		newThing = AuthToken.new()
		return AuthTokenPair(raw=newThing, hashed=AuthToken.hashed(raw=newThing))

	# Usage (assuming: 'import AuthToken'): authTokenIsValid = AuthToken.validAuthToken(authCookie=myAuthToken)
	# returns a bool that tells whether the given authToken is 
	# assigned to a user or not
	# THIS DOES NOT IDENTIFY THE USER
	@staticmethod
	def validAuthToken(authCookie: str) -> bool:
		try:
			userAuth = authCookie
			if userAuth == None or authTokens.find_one({"token": AuthToken.hashed(raw=userAuth.encode("ascii"))}) == None:
				return False
			return True
		except KeyError:
			return False
	
	# Usage (assuming: 'import AuthToken'): username = AuthToken.getUsernameFromAuthToken(authToken=myAuthToken)
	# this assumes the authToken is already verified
	# returns a username
	@staticmethod
	def getUsernameFromAuthToken(authToken: str) -> str:
		return authTokens.find_one({"token":AuthToken.hashed(raw=authToken.encode("ascii"))})["owner"]
