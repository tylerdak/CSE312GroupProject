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

@dataclass
class AuthTokenPair:
	raw: bytes
	hashed: bytes

class AuthToken:
	@staticmethod
	def new() -> bytes:
		tokenLength = 64
		rawToken = secrets.token_urlsafe(tokenLength)
		return rawToken.encode("ascii")
	
	@staticmethod
	def hashed(raw: bytes) -> str:
		return hashlib.sha256(raw).hexdigest()

	@staticmethod
	def newSet() -> AuthTokenPair:
		newThing = AuthToken.new()
		return AuthTokenPair(raw=newThing, hashed=AuthToken.hashed(raw=newThing))

	@staticmethod
	def validAuthToken(authCookie: str) -> bool:
		try:
			userAuth = authCookie
			if userAuth == None or authTokens.find_one({"token": AuthToken.hashed(raw=userAuth.encode("ascii"))}) == None:
				return False
			return True
		except KeyError:
			return False
	
	# this assumes the authToken is already verified
	# returns a username
	@staticmethod
	def getUsernameFromAuthToken(authToken: str) -> str:
		return authTokens.find_one({"token":AuthToken.hashed(raw=authToken.encode("ascii"))})["owner"]
