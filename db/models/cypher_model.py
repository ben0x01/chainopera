from sqlalchemy import Column, Boolean, Integer, String
from db.models.base_model import Base

class Zk1LabsModel(Base):
    __tablename__ = "Zk1Labs"
    id = Column(Integer, primary_key=True, index=True)
    private_key = Column(String, nullable=False)
    proxy = Column(String, nullable=False)
    email = Column(String, nullable=False)
    twitter = Column(String, nullable=False)
    ds_token = Column(String, nullable=False)
    login = Column(Boolean, nullable=False)
    join_waiting_list = Column(Boolean, nullable=False)
    follow_twitter = Column(Boolean, nullable=False)
    write_twitter_handle = Column(Boolean, nullable=False)
    discord_oauth = Column(Boolean, nullable=False)
    used_code = Column(Boolean, nullable=False)
    used_or_received_code = Column(String, nullable=False)
    os_header = Column(String, nullable=False)
    chrome_version = Column(String, nullable=False)
    errors = Column(String, nullable=False)