from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///sistema_saude.db')
Session = sessionmaker(bind=engine)
session = Session()

class Companhia(Base):
    __tablename__ = 'companhias'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)

class Movimentacao(Base):
    __tablename__ = 'movimentacoes'
    id = Column(Integer, primary_key=True)
    beneficiario = Column(String, nullable=False)
    empresa = Column(String)
    tipo = Column(String)
    data_inicio = Column(Date, default=datetime.now().date())
    data_finalizacao = Column(Date, nullable=True)
    cia_nome = Column(String)
    observacoes = Column(String) # NOVA COLUNA
    itens = relationship("ItemChecklist", back_populates="movimentacao", cascade="all, delete-orphan")

class ItemChecklist(Base):
    __tablename__ = 'itens_checklist'
    id = Column(Integer, primary_key=True)
    nome_item = Column(String)
    entregue = Column(Boolean, default=False)
    mov_id = Column(Integer, ForeignKey('movimentacoes.id'))
    movimentacao = relationship("Movimentacao", back_populates="itens")

Base.metadata.create_all(engine)