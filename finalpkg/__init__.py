from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from finalpkg import config
thc=Flask(__name__,instance_relative_config=True)
thc.config.from_pyfile('config.py')
thc.config.from_object(config.LiveConfig)
csrf=CSRFProtect(thc)
db=SQLAlchemy(thc)
from finalpkg import projectroutes,forms,staffroutes,adminroutes,thc_models
