# importar bibliotecas
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, declarative_base

# configurar banco
engine = create_engine('sqlite:///safeguard.db')
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class Funcionario(Base):
    __tablename__ = "funcionarios"
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    cpf = Column(String(40), nullable=False, index=True, unique=True)

    # representaçao classe
    def __repr__(self):
        return '<Funcionario: {} {}>'.format(self.nome, self.cpf)

    def save(self):
        db_session.add(self)
        db_session.commit()

    # função para deletar
    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_funcionario(self):
        dados_funcionario = {
            "id_funcionario": self.id,
            "nome": self.nome,
            "cpf": self.cpf
        }
        return dados_funcionario

class Epi(Base):
    __tablename__ = "epis"
    id = Column(Integer, primary_key=True)
    nome = Column(String(40), nullable=False, index=True)
    descricao = Column(String(11), nullable=False, index=True)
    validade = Column(String(40), nullable=False, index=True)

    def __repr__(self):
        return '<Epi: {} {} {}>'.format(self.id, self.nome, self.descricao)

    def save(self):
        db_session.add(self)
        db_session.commit()

        # função para deletar

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_epi(self):
        dados_epi = {
            "id_epi": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "validade": self.validade
        }
        return dados_epi

class Entrega(Base):
    __tablename__ = 'entregas'
    id = Column(Integer, primary_key=True)
    data_entrega = Column(String(40), nullable=False)
    ca = Column(Integer, nullable=False)
    periodo = Column(Integer, nullable=False)
    # chave estrangeira
    epi_id = Column(Integer, ForeignKey('epis.id'))
    epis = relationship(Epi)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'))
    funcionarios = relationship(Funcionario)

    def __repr__(self):
        return '<Entrega: {} {} {} {}>'.format(self.data_entrega, self.ca, self.funcionario_id, self.epi_id)

    def save(self):
        db_session.add(self)
        db_session.commit()

        # função para deletar

    def delete(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_entrega(self):
        dados_entrega = {
            "id_entrega": self.id,
            "data_entrega": self.data_entrega,
            "ca": self.ca,
            "periodo": self.periodo,
            "epi_id": self.epi_id,
            "funcionario_id": self.funcionario_id
        }
        return dados_entrega


# metodo para criar banco
def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
