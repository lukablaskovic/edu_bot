from datetime import datetime, timedelta
import jwt
from jwt import DecodeError, InvalidSignatureError
import streamlit as st
import extra_streamlit_components as stx
import time

class CookieHandler:
    def __init__(self, cookie_name: str, cookie_key: str, cookie_expiry_days: float=30.0):
        """
        Create a new instance of "CookieHandler".

        Parameters
        ----------
        cookie_name: str
            Name of the cookie stored on the client's browser for password-less re-authentication.
        cookie_key: str
            Key to be used to hash the signature of the re-authentication cookie.
        cookie_expiry_days: float
            Number of days before the re-authentication cookie automatically expires on the client's 
            browser.
        """
        self.cookie_name            =   cookie_name
        self.cookie_key             =   cookie_key
        self.cookie_expiry_days     =   cookie_expiry_days
        self.cookie_manager         =   stx.CookieManager()
        self.token                  =   None
        self.exp_date               =   None

    def get_cookie(self) -> str:
        """
        Retrieves, checks, and then returns the re-authentication cookie.

        Returns
        -------
        str
            re-authentication cookie.
        """
        if 'logout' in st.session_state and st.session_state['logout']:
            return False
        self.token = self.cookie_manager.get(cookie=self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if (self.token is not False and 'email' in self.token.keys() and
                self.token['exp_date'] > datetime.now().timestamp()):
                return self.token
            
    def delete_cookie(self):
        """
        Deletes the re-authentication cookie.
        """
        try:
            self.cookie_manager.delete(self.cookie_name)
        except KeyError as e:
            print(e)

    def set_cookie(self, name, email, picture, oauth_id):
        """
        Sets the re-authentication cookie.
        """
        self.exp_date = self._set_exp_date()
        token = self._token_encode(name, email, picture, oauth_id)
        self.cookie_manager.set(self.cookie_name, token,
                                    expires_at=datetime.now() + timedelta(days=self.cookie_expiry_days))
        time.sleep(0.3)
    def _set_exp_date(self) -> str:
        """
        Sets the re-authentication cookie's expiry date.

        Returns
        -------
        str
            re-authentication cookie's expiry timestamp in Unix Epoch.
        """
        return (datetime.now() + timedelta(days=self.cookie_expiry_days)).timestamp()
    
    def _token_decode(self) -> str:
        """
        Decodes the contents of the re-authentication cookie.

        Returns
        -------
        str
            Decoded cookie used for password-less re-authentication.
        """
        try:
            return jwt.decode(self.token, self.cookie_key, algorithms=['HS256'])
        except InvalidSignatureError as e:
            print(e)
            return False
        except DecodeError as e:
            print(e)
            return False
        
    def _token_encode(self, name : str, email: str, picture: str, oauth_id: str) -> str:
        """
        Encodes the contents of the re-authentication cookie.

        Returns
        -------
        str
            Cookie used for password-less re-authentication.
        """
        return jwt.encode({'email': email, 'name': name, 'picture': picture, 'oauth_id': oauth_id,
            'exp_date': self.exp_date}, self.cookie_key, algorithm='HS256')